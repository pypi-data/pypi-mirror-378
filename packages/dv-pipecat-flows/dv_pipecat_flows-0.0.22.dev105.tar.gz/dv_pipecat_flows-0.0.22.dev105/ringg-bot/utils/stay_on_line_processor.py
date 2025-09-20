# Create a new file: hold_processor.py

import asyncio
from typing import Optional

from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    Frame,
    LLMMessagesFrame,
    LLMMessagesAppendFrame,
    StartUserIdleProcessorFrame,
    StopUserIdleProcessorFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.openai.llm import OpenAILLMContext


class StayOnLineProcessor(FrameProcessor):
    """This processor manages the bot's "hold" state.
    When a hold is initiated, it pauses the main user idle processor.
    The hold is released either after a timeout or when the user speaks again i.e, we get the TranscriptFrame.
    """

    def __init__(self, llm_provider: str, **kwargs):
        super().__init__(**kwargs)
        self._on_hold = False
        self._llm_provider = llm_provider
        self._context = None
        self._hold_task: Optional[asyncio.Task] = None

    async def start_hold(self, timeout: int = 60, context: OpenAILLMContext = None):
        """Initiates the hold state, pausing the idle processor."""
        if self._on_hold and self._hold_task:
            await self.cancel_task(self._hold_task)

        self._on_hold = True
        await self.push_frame(StopUserIdleProcessorFrame(), FrameDirection.UPSTREAM)
        self.logger.info(f"Hold state initiated for {timeout} seconds. UserIdleProcessor paused.")
        self._hold_task = self.create_task(self._timeout_handler(timeout))
        self._context = context

    async def _end_hold(self):
        """Ends the hold state, resuming the idle processor."""
        if not self._on_hold:
            return

        self.logger.info("Hold state ended. Resuming UserIdleProcessor.")
        self._on_hold = False
        await self.push_frame(StartUserIdleProcessorFrame(), FrameDirection.UPSTREAM)
        await self._cleanup()

    async def _timeout_handler(self, timeout: int):
        """Coroutine that waits for the timeout and then ends the hold."""
        try:
            await asyncio.sleep(timeout)
            self.logger.info(f"Hold timeout of {timeout} seconds reached.")
            if self._context:
                role = "user" if self._llm_provider.startswith("google") else "system"
                new_messages = [
                    {
                        "role": role,
                        "content": f"The {timeout}s wait period just ended. ",
                    }
                ]
                await self.push_frame(LLMMessagesAppendFrame(messages=new_messages, run_llm=True))
            await self._end_hold()
        except asyncio.CancelledError:
            self.logger.debug("Hold timeout task cancelled.")

    async def _cleanup(self):
        """Helper method to cancel any running hold task."""
        if self._hold_task and not self._hold_task.done():
            self.logger.debug("HoldProcessor: Cleaning up pending hold task.")
            await self.cancel_task(self._hold_task)
        self._hold_task = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)

        # If we get a transcript from the user while on hold, end the hold.
        if self._on_hold and isinstance(frame, TranscriptionFrame):
            self.logger.info("User spoke, ending hold state.")
            await self._end_hold()
        if isinstance(frame, (CancelFrame, EndFrame)):
            await self._cleanup()
