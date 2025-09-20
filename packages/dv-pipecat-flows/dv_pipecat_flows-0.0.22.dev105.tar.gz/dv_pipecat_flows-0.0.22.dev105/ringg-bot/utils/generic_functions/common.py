import json
import socket
import time

import aiohttp
from cache import cache
from fastapi import HTTPException
from loguru import logger
from openai.types.chat import ChatCompletionToolParam

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.audio.vad.vad_analyzer import VADParams

from .response_handler import response_formatters

# Convert JSON tools to FunctionSchema objects for registration


def tool_json_to_function_schema(tool_json):
    return FunctionSchema(
        name=tool_json["name"],
        description=tool_json.get("description", ""),
        properties=tool_json["parameters"].get("properties", {}),
        required=tool_json["parameters"].get("required", []),
    )


def validate_vad_input(vad_input):  # noqa: D417
    """Validates if the vad_speaking dictionary contains all required keys.

    Args:
        vad_speaking: A dictionary containing VAD parameters
    Returns:
        bool: True if all required keys are present, False otherwise.
    """
    required_keys = ["confidence", "start_secs", "stop_secs", "min_volume"]

    if not isinstance(vad_input, dict):
        return False

    return all(key in vad_input for key in required_keys)


def _clamp(v, lo, hi):
    """Clamp value between low and high bounds."""
    return max(lo, min(hi, v))


def get_vad_params(advanced_vad, smart_turn_enabled=False, vad_input=None):
    """Get VAD parameters optimized for the detection mode.

    Args:
        advanced_vad: Whether to use advanced VAD with separate speaking/silent params
        smart_turn_enabled: Whether Smart Turn semantic detection is enabled
        vad_input: Optional dict with custom VAD parameters

    Returns:
        Tuple of (vad_params_speaking, vad_params_bot_silent)
    """
    # Legacy path: no advanced VAD
    if not advanced_vad:
        vad_params_speaking = None
        if vad_input and validate_vad_input(vad_input):
            vad_params_bot_silent = VADParams(
                confidence=vad_input["confidence"],
                start_secs=vad_input["start_secs"],
                stop_secs=vad_input["stop_secs"],
                min_volume=vad_input["min_volume"],
            )
        else:
            vad_params_bot_silent = VADParams()
        return vad_params_speaking, vad_params_bot_silent

    # Advanced VAD with Smart Turn optimization
    if smart_turn_enabled:
        # Smart Turn: release sooner, let semantic detector arbitrate the turn
        sp_default = VADParams(confidence=0.70, start_secs=0.20, stop_secs=0.2, min_volume=0.60)
        sl_default = VADParams(confidence=0.60, start_secs=0.10, stop_secs=0.2, min_volume=0.60)

        if vad_input and validate_vad_input(vad_input):
            vad_params_speaking = VADParams(
                confidence=vad_input.get("confidence", sp_default.confidence),
                start_secs=vad_input.get("start_secs", sp_default.start_secs),
                # Keep stop short for fast hand-off (clamp to ~0.15–0.35s)
                stop_secs=_clamp(vad_input.get("stop_secs", sp_default.stop_secs), 0.15, 0.35),
                min_volume=vad_input.get("min_volume", sp_default.min_volume),
            )
            # Also allow vad_input to override silent params when Smart Turn is on
            vad_params_bot_silent = VADParams(
                confidence=vad_input.get("confidence", sl_default.confidence),
                start_secs=vad_input.get("start_secs", sl_default.start_secs),
                stop_secs=_clamp(vad_input.get("stop_secs", sl_default.stop_secs), 0.15, 0.35),
                min_volume=vad_input.get("min_volume", sl_default.min_volume),
            )
        else:
            vad_params_speaking = sp_default
            vad_params_bot_silent = sl_default

        return vad_params_speaking, vad_params_bot_silent

    else:
        # Advanced VAD without Smart Turn: existing values
        if vad_input and validate_vad_input(vad_input):
            vad_params_speaking = VADParams(
                confidence=vad_input["confidence"],
                start_secs=vad_input["start_secs"],
                stop_secs=vad_input["stop_secs"],
                min_volume=vad_input["min_volume"],
            )
        else:
            vad_params_speaking = VADParams(
                confidence=0.75, start_secs=0.30, stop_secs=0.70, min_volume=0.70
            )

        vad_params_bot_silent = VADParams(
            confidence=0.65, start_secs=0.10, stop_secs=0.70, min_volume=0.60
        )
        return vad_params_speaking, vad_params_bot_silent


def call_config_validator(call_config):
    if call_config.language in ["te-IN", "gu-IN", "kn-IN"]:
        if call_config.tts_provider not in ["azure", "google", "sarvam"]:
            raise HTTPException(
                status_code=400,
                detail="For 'te-IN', 'gu-IN', or 'kn-IN' language, 'tts_provider' must be 'azure', 'google', or 'sarvam'",
            )
        if call_config.stt_provider not in ["azure", "google", "gladia"]:
            raise HTTPException(
                status_code=400,
                detail="For 'te-IN' or 'gu-IN' language, 'stt_provider' must be 'azure/google/gladia'",
            )

    # Validate voicemail configuration
    if call_config.voicemail:
        if not isinstance(call_config.voicemail.detect, bool):
            raise HTTPException(status_code=400, detail="voicemail.detect must be a boolean")

        if call_config.voicemail.action not in ["summarise", "end"]:
            raise HTTPException(
                status_code=400,
                detail="voicemail.action must be either 'summarise' or 'end'",
            )

        if not isinstance(call_config.voicemail.retry, bool):
            raise HTTPException(status_code=400, detail="voicemail.retry must be a boolean")

    if call_config.dtmf_input:
        digits = call_config.dtmf_input.digits
        timeout = call_config.dtmf_input.timeout
        end = call_config.dtmf_input.end
        reset = call_config.dtmf_input.reset

        if digits is not None and not isinstance(digits, int):
            raise HTTPException(status_code=400, detail="dtmf_input.digits must be an integer")

        if timeout is not None and not isinstance(timeout, (int, float)):
            raise HTTPException(
                status_code=400, detail="dtmf_input.timeout must be an integer or float"
            )

        if end is not None and not isinstance(end, str):
            raise HTTPException(status_code=400, detail="dtmf_input.end must be a string")

        if reset is not None and not isinstance(reset, str):
            raise HTTPException(status_code=400, detail="dtmf_input.reset must be a string")

        if not digits and not end:
            raise HTTPException(
                status_code=400, detail="Either dtmf_input.digits or dtmf_input.end must be present"
            )


def convert_tools_for_llm_provider(tools, llm_provider):
    """Convert tools to provider-specific format.

    Args:
        tools: List of tools in format [{"name": str, "description": str, "parameters": dict}]
        llm_provider: One of "gemini" or "openai compatible like openai/groq"

    Returns:
        - For Google: List of {"function_declarations": [...]}
        - For OpenAI: List of ChatCompletionToolParam objects
    """
    # if llm_provider == "google":
    #     return [{"function_declarations": [tool]} for tool in tools]
    # else:
    return [
        ChatCompletionToolParam(
            type="function",
            function={
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        )
        for tool in tools
    ]


def is_arabic_present(primary_language: str | None, additional_languages: list | None) -> bool:
    """Fast check for Arabic language presence.

    Consider Arabic if a code starts with 'ar' (case-insensitive), e.g. 'ar', 'ar-SA'.
    Optimized for speed: avoids lower()/strip() on entire strings where possible and
    exits early on first match.
    - Optimized (char checks): ~0.21 µs per call
    - Simple (lstrip().lower().startswith): ~0.87 µs per call
    - Speedup: ~4.2x, but absolute savings ≈ 0.66 µs per call
    """
    # Fast-path primary language (string-only)
    s = primary_language
    if isinstance(s, str):
        # Ignore leading whitespace; trailing whitespace doesn't affect startswith
        s = s.lstrip()
        if len(s) >= 2:
            c0 = s[0]
            if c0 == "a" or c0 == "A":
                c1 = s[1]
                if c1 == "r" or c1 == "R":
                    return True

    # Check additional languages
    if not additional_languages:
        return False

    for l in additional_languages:
        if not isinstance(l, str):
            # Skip non-string entries to keep the function tight and predictable
            continue
        s = l.lstrip()
        if len(s) >= 2:
            c0 = s[0]
            if c0 == "a" or c0 == "A":
                c1 = s[1]
                if c1 == "r" or c1 == "R":
                    return True

    return False


def get_hostname():
    return socket.gethostname()


# Define a function to check if the text is in Hindi


# print(format_tts_text("23-October-2025", "en"))
# print(format_tts_text("31-October-2024", "hi"))
# print(format_tts_text("23-Oct", "en"))
# print(format_tts_text("23-10", "hi"))
# print(format_tts_text("23-10-2025", "en"))
# print(format_tts_text("23,00,000", "en"))
# print(format_tts_text("23000000", "hi"))
# print(format_tts_text("230,000", "hi"))
# print(format_tts_text("10.06", "hi"))
# print(format_tts_text("23.90", "hi"))
# print(format_tts_text("23.90", "en"))
# print(format_tts_text("100000", "en"))
# print(format_tts_text("25th lakhs", "hi"))
# print(format_tts_text("25th lakhs", "en"))
# print(format_tts_text("10%", "hi"))
# print(format_tts_text("25 %", "en"))
# print(format_tts_text("+919999876598", "en"))  # The +91 should be stripped off.
# print(format_tts_text("9999876598", "en"))
# print(format_tts_text("9999876598", "hi"))
# print(format_tts_text("121st Friday", "en"))
# print(format_tts_text("$12223.80", "en"))
# print(format_tts_text("₹23.08", "en"))
# print(format_tts_text("₹23 lakh", "en"))
# print(format_tts_text("₹23 lakhs", "en"))
# s = """
# Your order details are as follows:

# - **Order ID:** 1111
# - **Order Date:** 02-02-2025
# - **Amount:** ₹67,549
# - **Order Status:** Completed
# - **Payment Method:** UPI
# - **Masked Card Number:** XXXX-XXXX-XXXX-1111


# Since the order was completed before the promised timestamp of 04-02-2025, late fees are not applicable"""
async def get_cache_key(function_name, args):
    """Generate a cache key from function name and arguments.

    Args:
        function_name (str): Name of the function being called
        args (dict): Arguments passed to the function

    Returns:
        str: A unique cache key string
    """
    # Sort the args dictionary to ensure consistent keys
    sorted_args = dict(sorted(args.items()))
    args_str = json.dumps(sorted_args, sort_keys=True)
    return f"{function_name}:{args_str}"


async def make_api_request(
    session: aiohttp.ClientSession, method: str, url, headers, request_data=None
):
    """Make API request and return the JSON response."""
    start_time = time.time()

    try:
        if method.upper() == "GET":
            async with session.request(method, url, headers=headers) as response:
                response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx responses
                result = await response.json()
        else:
            async with session.request(method, url, headers=headers, json=request_data) as response:
                response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx responses
                result = await response.json()

        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        logger.info(f"API call to {url} completed in {duration}ms")

        return result
    except Exception as e:
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        logger.error(f"API call to {url} failed after {duration}ms: {str(e)}")
        raise


async def cache_and_process_api_response(
    response_json, tool_config, function_name, args, use_cache, cache_ttl, logger
):
    """Process API response: cache raw result and apply response handler if needed."""
    # Cache the raw result before applying response handler
    if use_cache:
        cache_key = await get_cache_key(function_name, args)
        await cache.set(cache_key, response_json, ttl=cache_ttl)
        logger.debug(f"Cached result for {function_name} with key {cache_key}, TTL {cache_ttl}s")

    # Apply response handler if specified
    response_handler = tool_config.get("response_formatter")
    logger.debug(
        f"Applying response handler: {response_handler} for {tool_config.get('response_formatter')}"
    )
    if response_handler and response_handler in response_formatters:
        formatter_args = args.copy()

        if "responseSelectedKeys" in tool_config:
            formatter_args["responseSelectedKeys"] = tool_config["responseSelectedKeys"]
        response_json = await response_formatters[response_handler](
            response_json, formatter_args, logger
        )

    return response_json
