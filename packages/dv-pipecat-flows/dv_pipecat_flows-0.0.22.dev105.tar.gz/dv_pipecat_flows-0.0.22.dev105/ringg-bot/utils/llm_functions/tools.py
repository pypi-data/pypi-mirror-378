import asyncio
from typing import Any, Callable, Dict

from loguru import logger

from pipecat.services.openai import OpenAILLMService


async def send_email_generic(
    function_name: str,
    tool_call_id: str,
    args: Dict[str, Any],
    llm: OpenAILLMService,
    context: Any,
    result_callback: Callable,
):
    """
    Sends an email using a generic method.

    Args:
        function_name: The name of the function being called.
        tool_call_id: The ID of the tool call.
        args: A dictionary containing the arguments for the function.
              Expected keys: 'subject', 'body', 'to_address'.
        llm: The OpenAILLMService instance.
        context: The context object.
        result_callback: The callback function to send the result back to the LLM.
    """
    subject = args.get("subject")
    body = args.get("body")
    to_address = args.get("to_address")

    # Replace this with your actual email sending logic
    logger.info(f"Sending email to {to_address} with subject '{subject}' and body '{body}'")

    # Simulate API call delay
    await asyncio.sleep(1)

    # Send result back to LLM
    await result_callback(
        function_name,
        tool_call_id,
        f"Email sent successfully to {to_address}",
        context,
    )


async def send_email_specific(
    function_name: str,
    tool_call_id: str,
    args: Dict[str, Any],
    llm: OpenAILLMService,
    context: Any,
    result_callback: Callable,
):
    """
    Sends an email using a specific template.

    Args:
        function_name: The name of the function being called.
        tool_call_id: The ID of the tool call.
        args: A dictionary containing the arguments for the function.
              Expected keys: 'template_id', 'parameters', 'to_address'.
        llm: The OpenAILLMService instance.
        context: The context object.
        result_callback: The callback function to send the result back to the LLM.
    """
    template_id = args.get("template_id")
    parameters = args.get("parameters")
    to_address = args.get("to_address")

    # Replace this with your actual email sending logic using the template
    logger.info(
        f"Sending email to {to_address} using template '{template_id}' with parameters '{parameters}'"
    )

    # Simulate API call delay
    await asyncio.sleep(1)

    # Send result back to LLM
    await result_callback(
        function_name,
        tool_call_id,
        f"Email sent successfully to {to_address} using template '{template_id}'",
        context,
    )


async def send_sms(
    function_name: str,
    tool_call_id: str,
    args: Dict[str, Any],
    llm: OpenAILLMService,
    context: Any,
    result_callback: Callable,
):
    """
    Sends an SMS message.

    Args:
        function_name: The name of the function being called.
        tool_call_id: The ID of the tool call.
        args: A dictionary containing the arguments for the function.
              Expected keys: 'to_number', 'text'.
        llm: The OpenAILLMService instance.
        context: The context object.
        result_callback: The callback function to send the result back to the LLM.
    """
    to_number = args.get("to_number")
    text = args.get("text")

    # Replace this with your actual SMS sending logic
    logger.info(f"Sending SMS to {to_number} with text '{text}'")

    # Simulate API call delay
    await asyncio.sleep(1)

    # Send result back to LLM
    await result_callback(
        function_name,
        tool_call_id,
        f"SMS sent successfully to {to_number}",
        context,
    )
