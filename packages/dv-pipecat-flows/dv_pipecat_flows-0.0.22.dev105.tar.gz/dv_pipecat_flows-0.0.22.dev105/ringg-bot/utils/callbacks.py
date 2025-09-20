from typing import Any, Optional, Union

from utils.llm_functions.end_call_handler import end_call

from pipecat.frames.frames import (  # noqa: D100
    LLMMessagesFrame,
    LLMMessagesAppendFrame,
)
from pipecat.processors.two_stage_user_idle_processor import (
    TwoStageUserIdleProcessor,
    UserIdleProcessor,
)  # noqa: D100


async def warning_callback(
    idle_processor: TwoStageUserIdleProcessor,
    user_idle,
    context,
    function_call_monitor,
    llm_provider: str,
    logger,
):
    function_call_monitor.append("warning_callback_called")
    logger.debug("Idle warning: asking the user if they are present.")

    # await tts.say("I couldn't catch that. Are you still there?")
    match llm_provider:
        case u if u.startswith("azure"):
            role = "assistant"
        case u if u.startswith("google"):
            role = "user"
        case _:
            role = "system"

    if idle_processor.last_speaker == "user":
        message = {
            "role": role,
            "content": "Politely and briefly ask them to repeat as you couldn't hear based on the language of the conversation. Assistant needs to respond. Eg: English: Sorry can you please reapeat?",
        }

    else:
        message = {
            "role": role,
            "content": "The user has been quiet. Politely and briefly ask if they're still there based on the language of the conversation. Assistant needs to respond.",
        }

    # if llm_provider == "google":
    #     google_message = glm.Content(role="user", parts=[glm.Part(text=message["content"])])
    #     context.add_message(google_message)
    #     # await llm.queue_frame(OpenAILLMContextFrame(context), FrameDirection.DOWNSTREAM)
    #     await user_idle.push_frame(LLMMessagesFrame(context.messages))

    #     # await user_idle.push_frame(
    #     #     LLMMessagesFrame(
    #     #         GoogleLLMContext.from_standard_message(message=m) for m in context.messages
    #     #     )
    #     # )
    # else:
    # context.add_message(message)
    await user_idle.push_frame(LLMMessagesAppendFrame([message], run_llm=True))


async def end_callback(
    idle_processor: Union[UserIdleProcessor, TwoStageUserIdleProcessor, None],
    telephony_provider,
    call_id,
    stream_id,
    websocket_client,
    callback_call_id,
    context_aggregator,
    transcript_handler,
    task,
    task_references,
    function_call_monitor,
    logger,
    transport: Optional[Any] = None,
    record_locally=False,
):
    logger.debug("Ending call")
    success = await end_call(
        telephony_provider,
        call_id,
        stream_id,
        websocket_client,
        callback_call_id,
        context_aggregator,
        transcript_handler,
        task,
        task_references,
        function_call_monitor,
        logger,
        transport,
        record_locally,
    )
    # try:
    #     if not success:
    #         await user_idle.cleanup()
    # except Exception as e:
    #     logger.error(f"Exception while cleaning useridle processor: {e}")
