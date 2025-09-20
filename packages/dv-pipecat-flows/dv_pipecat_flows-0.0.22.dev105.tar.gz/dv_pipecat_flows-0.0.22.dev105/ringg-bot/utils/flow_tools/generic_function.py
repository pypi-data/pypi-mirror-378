"""Flow-native generic function tool implementation."""

import random
import time
from typing import Dict, Any
import aiohttp

from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
from pipecat.frames.frames import TTSSpeakFrame, LLMMessagesAppendFrame, FunctionCallResultProperties

from ..generic_functions.common import (
    cache_and_process_api_response,
    get_cache_key,
    make_api_request,
)


async def generic_function(flow_manager: FlowManager, function_name: str, **args) -> FlowResult:
    """
    Generic HTTP API function handler for custom tools.
    This function makes HTTP requests based on node-specific configuration.

    Args:
        function_name: Name of the function to execute
        **args: Dynamic arguments passed from LLM function call

    Returns:
        FlowResult with API response data
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    monitor = s.get("function_call_monitor", [])
    pre_query_phrases = s.get("pre_query_phrases", [])
    cache = s.get("cache")
    response_formatters = s.get("response_formatters", {})

    # Get current node and function config
    current_node = flow_manager.current_node
    runtime_config = s.get("nodes_runtime_config", {})
    node_config = runtime_config.get(current_node, {})
    function_config = node_config.get("functions", {}).get(function_name, {})

    start_time = time.time()
    monitor.append(f"{function_name}_called")

    if logger:
        logger.debug(f"Generic function handler called for: {function_name}")
        logger.debug(f"Node: {current_node}, Config: {function_config}")

    # 60% chance: speak a pre-query phrase
    if pre_query_phrases and random.random() < 0.6:
        phrase = random.choice(pre_query_phrases)
        await flow_manager.llm.push_frame(TTSSpeakFrame(text=phrase))
        await flow_manager.llm.push_frame(
            LLMMessagesAppendFrame(
                messages=[{"role": "assistant", "content": phrase}], run_llm=False
            )
        )

    # Check if function has HTTP configuration
    http_config = function_config.get("http_parameters", {})
    if not http_config:
        if logger:
            logger.error(
                f"No HTTP configuration found for function '{function_name}' in node '{current_node}'"
            )
        return (
            {
                "status": "error",
                "error": f"No HTTP configuration found for function '{function_name}'",
            },
            None,
        )

    # Extract configuration parameters
    use_cache = function_config.get("cache_response", False)
    cache_ttl = function_config.get("cache_ttl", 300)  # Default 5 minutes TTL
    response_formatter = function_config.get("response_formatter")
    response_selected_keys = function_config.get("responseSelectedKeys", [])

    # Try cache first if enabled
    if use_cache and cache:
        cache_key = await get_cache_key(function_name, args)
        cached_result = await cache.get(cache_key)
        if logger:
            logger.info(f"Cached result: {cached_result}")

        if cached_result:
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            if logger:
                logger.info(
                    f"Cache hit for {function_name} with key {cache_key} - completed in {duration}ms"
                )

            # Apply response formatter if specified
            if response_formatter and response_formatter in response_formatters:
                formatter_args = args.copy()
                if response_selected_keys:
                    formatter_args["responseSelectedKeys"] = response_selected_keys

                cached_result = await response_formatters[response_formatter](
                    cached_result, formatter_args, logger
                )

            # Don't add tool message here - pipecat framework handles tool result messages automatically
            return ({"status": "success", "data": cached_result}, None)

    # Prepare HTTP request
    url = http_config.get("url", "")
    method = http_config.get("method", "POST")
    headers = http_config.get("headers", {}).copy()
    body = http_config.get("body", {}).copy() if http_config.get("body") else None

    # Add Content-Type header if not present
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"

    # Replace template variables in headers
    for header_key, header_value in headers.items():
        if isinstance(header_value, str) and "{{" in header_value:
            for arg_key, arg_value in args.items():
                headers[header_key] = header_value.replace(f"{{{{{arg_key}}}}}", str(arg_value))

    # Prepare request data
    if body and isinstance(body, dict):
        # Replace template variables in body
        for body_key, body_value in body.items():
            if isinstance(body_value, str) and "{{" in body_value:
                for arg_key, arg_value in args.items():
                    body[body_key] = body_value.replace(f"{{{{{arg_key}}}}}", str(arg_value))
        request_data = body
    else:
        request_data = args

    # Replace template variables in URL
    if "{{" in url:
        for arg_key, arg_value in args.items():
            url = url.replace(f"{{{{{arg_key}}}}}", str(arg_value))

    if logger:
        logger.debug(f"Making API call: url: {url} headers: {headers} body: {request_data}")

    try:
        async with aiohttp.ClientSession() as session:
            response_json = await make_api_request(
                session,
                method,
                url,
                headers,
                request_data if method.upper() != "GET" else None,
            )

            # Process the response (includes caching if enabled)
            # Create a tool_config structure for compatibility with existing cache_and_process_api_response
            tool_config = {
                "cache_response": use_cache,
                "cache_ttl": cache_ttl,
                "response_formatter": response_formatter,
                "responseSelectedKeys": response_selected_keys,
            }

            processed_response = await cache_and_process_api_response(
                response_json, tool_config, function_name, args, use_cache, cache_ttl, logger
            )

            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            if logger:
                logger.info(f"Function '{function_name}' completed successfully in {duration}ms")

            # Don't add tool message here - pipecat framework handles tool result messages automatically

            return ({"status": "success", "data": processed_response}, None)

    except Exception as e:
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)
        if logger:
            logger.error(
                f"Error executing HTTP request for function '{function_name}' after {duration}ms: {e}"
            )
        return ({"status": "error", "error": str(e)}, None)
