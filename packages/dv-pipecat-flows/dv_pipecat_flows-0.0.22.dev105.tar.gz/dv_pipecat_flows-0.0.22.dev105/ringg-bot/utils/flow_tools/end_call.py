"""Flow-native end_call tool implementation."""

from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult


async def end_call(flow_manager: FlowManager, final_message: str) -> FlowResult:
    """
    End the current call when the conversation has reached a natural conclusion or user says bye or tells to cut the call or speak with you later as they are busy.

    Args:
        final_message: The final message to say to the user before ending the call. Should be a polite goodbye message appropriate for the conversation context. Keep is short and less than 15 words.

    Returns:
        FlowResult indicating the call end has been scheduled
    """
    s = flow_manager.state
    monitor = s.get("function_call_monitor", [])
    logger = s.get("bot_logger")

    monitor.append("end_call_called")

    if logger:
        logger.info(f"Scheduling call end with message: {final_message}")

    # Run *after* the next LLM completion & TTS using deferred post-actions
    flow_manager.actions.schedule_deferred_post_actions(
        [{"type": "end_conversation", "text": final_message}]
    )

    return ({"status": "success", "data": {"scheduled": True, "message": final_message}}, None)
