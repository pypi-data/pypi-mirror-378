import random
import time

import aiohttp

from pipecat.frames.frames import FunctionCallResultProperties

from ..generic_functions.common import (
    cache_and_process_api_response,
    get_cache_key,
    make_api_request,
)


async def generic_function_handler(
    function_name,
    tool_call_id,
    args,
    llm,
    call_config,
    tts,
    pre_query_phrases,
    result_callback,
    cache,
    response_formatters,
    function_call_monitor,
    logger,
):
    start_time = time.time()
    logger.debug(f"Generic function handler called for function: {function_name}")
    function_call_monitor.append(f"{function_name}_called")
    # speak a filler word only 60% of the times
    if random.random() < 0.6:
        if len(pre_query_phrases) > 0:
            phrase = random.choice(pre_query_phrases)
            await tts.say(phrase)
    tool_config = None
    if call_config:
        # Handle both dict and Pydantic model
        if hasattr(call_config, "get"):
            tools = call_config.get("tools")
        else:
            tools = getattr(call_config, "tools", None)
        
        if tools:
            for tool in tools:
                if tool["name"] == function_name:
                    tool_config = tool
                    break
    if not tool_config:
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)
        logger.error(f"Function '{function_name}' not found in call config after {duration}ms")
        await result_callback(
            {"status": "error", "message": f"Tool '{function_name}' not found in call config."},
            properties=FunctionCallResultProperties(run_llm=True),
        )
        return

    logger.debug(f"Tool config: {tool_config} with args: {args}")

    if "http" in tool_config:
        # Check if caching is enabled for this tool
        use_cache = tool_config.get("cache_response", False)
        cache_ttl = tool_config.get("cache_ttl", 300)  # Default 5 minutes TTL

        # Try to get from cache if caching is enabled
        if use_cache:
            cache_key = await get_cache_key(function_name, args)
            cached_result = await cache.get(cache_key)
            logger.info(f"Cached result: {cached_result}")
            if cached_result:
                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)
                logger.info(
                    f"Cache hit for {function_name} with key {cache_key} - completed in {duration}ms"
                )

                # Apply response handler if specified
                response_formatter = tool_config.get("response_formatter")
                if response_formatter and response_formatter in response_formatters:
                    formatter_args = args.copy()

                    if "responseSelectedKeys" in tool_config:
                        formatter_args["responseSelectedKeys"] = tool_config["responseSelectedKeys"]

                    cached_result = await response_formatters[response_formatter](
                        cached_result, formatter_args, logger
                    )
                await result_callback(
                    {"status": "success", "data": cached_result},
                    properties=FunctionCallResultProperties(run_llm=True),
                )
                return
        http_config = tool_config["http"]
        # Get the URL from http_config - note that modifying this local variable
        # won't affect the original http_config dictionary
        url = http_config.get("url")
        method = http_config.get("method", "POST")
        headers = http_config.get("headers", {}).copy()  # Create a copy of headers

        # Add Content-Type header if not present
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        body = http_config.get("body")
        if body and isinstance(body, dict):
            body = body.copy()  # Create a copy of body if it exists and is a dict

        # Replace variables in headers
        for header_key, header_value in headers.items():
            if isinstance(header_value, str) and "{{" in header_value:
                for arg_key, arg_value in args.items():
                    headers[header_key] = header_value.replace(f"{{{{{arg_key}}}}}", str(arg_value))

        # Prepare data for the request
        request_data = {}
        if body:
            if isinstance(body, dict):
                # Replace variables in the body
                for body_key, body_value in body.items():
                    if isinstance(body_value, str) and "{{" in body_value:
                        for arg_key, arg_value in args.items():
                            body[body_key] = body_value.replace(
                                f"{{{{{arg_key}}}}}", str(arg_value)
                            )
                request_data = body
            else:
                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)
                logger.error(f"Body validation failed for '{function_name}' after {duration}ms")
                await result_callback(
                    {
                        "status": "error",
                        "message": f"Body for tool '{function_name}' must be a dictionary.",
                    },
                    properties=FunctionCallResultProperties(run_llm=True),
                )
                return
        else:
            request_data = args

        if "{{" in url:
            for arg_key, arg_value in args.items():
                url = url.replace(f"{{{{{arg_key}}}}}", str(arg_value))

        logger.debug(f"Making API call: url: {url} headers: {headers} body:{request_data}")

        try:
            async with aiohttp.ClientSession() as session:
                response_json = await make_api_request(
                    session,
                    method,
                    url,
                    headers,
                    request_data if method.upper() != "GET" else None,
                )

                # Process the response
                processed_response = await cache_and_process_api_response(
                    response_json, tool_config, function_name, args, use_cache, cache_ttl, logger
                )

                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)
                logger.info(f"Function '{function_name}' completed successfully in {duration}ms")

                await result_callback(
                    {"status": "success", "data": processed_response},
                    properties=FunctionCallResultProperties(run_llm=True),
                )
        except Exception as e:
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            logger.error(
                f"Error executing HTTP request for function '{function_name}' after {duration}ms: {e}"
            )
            await result_callback(
                {"status": "error", "message": str(e)},
                properties=FunctionCallResultProperties(run_llm=True),
            )
    else:
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)
        logger.error(f"No HTTP configuration found for tool '{function_name}' after {duration}ms")
        await result_callback(
            {
                "status": "error",
                "message": f"No HTTP configuration found for tool '{function_name}'.",
            },
            properties=FunctionCallResultProperties(run_llm=True),
        )
