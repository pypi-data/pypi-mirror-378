"""Flow-native stay_on_line tool implementation."""

from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
from pipecat.frames.frames import TTSSpeakFrame, LLMMessagesAppendFrame


async def stay_on_line(
    flow_manager: FlowManager, duration: int = 60, message: str = ""
) -> FlowResult:
    """
    When the user asks you to wait or hold on or stay on the line, call this function to wait for that duration. And then after that duration, we will resume the call.

    Args:
        duration: The duration in seconds to wait for the user. Default 60.
        message: An optional message to say to the user before waiting (e.g., 'Okay, I will wait.').

    Returns:
        FlowResult indicating hold status
    """
    s = flow_manager.state
    proc = s.get("stay_on_line_processor")
    logger = s.get("bot_logger")
    monitor = s.get("function_call_monitor", [])

    monitor.append("stay_on_line_called")

    if logger:
        logger.info(f"User requested hold for {duration}s")

    if message:
        # Speak the message
        await flow_manager.llm.push_frame(TTSSpeakFrame(text=message))
        # Also append to context
        await flow_manager.llm.push_frame(
            LLMMessagesAppendFrame(
                messages=[{"role": "assistant", "content": message}], run_llm=False
            )
        )

    if proc is not None:
        # Start the hold using the processor with context aggregator
        context_aggregator = s.get("context_aggregator")
        if context_aggregator:
            context = context_aggregator.user()._context
        else:
            context = None
        await proc.start_hold(duration, context)

    return ({"status": "success", "data": {"holding_for_secs": duration}}, None)
