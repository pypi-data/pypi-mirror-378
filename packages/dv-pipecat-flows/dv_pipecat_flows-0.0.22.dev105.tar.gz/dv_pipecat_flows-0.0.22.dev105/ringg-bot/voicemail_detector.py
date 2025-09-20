from loguru import logger

from pipecat.frames.frames import (
    BotInterruptionFrame,
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    CancelTaskFrame,
    Frame,
    LLMMessagesAppendFrame,
    StartInterruptionFrame,
    STTMuteFrame,
    TranscriptionFrame,
    VADParamsUpdateFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class VoicemailDetector(FrameProcessor):
    def __init__(
        self,
        end_callback,
        vad_params_bot_silent,
        function_call_monitor,
        voicemail_config=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.end_callback = end_callback
        self.is_muted = False
        self._first_speech_handled = False
        self.voicemail_detected = False
        self.voicemail_phrases = ["leave a message", "after the tone", "voicemail", "voice mail"]
        self.vad_params_bot_silent = vad_params_bot_silent
        self.function_call_monitor = function_call_monitor

        # Handle new voicemail configuration structure
        if voicemail_config is None:
            self.voicemail_detect = False
            self.voicemail_action = "end"
            self.voicemail_retry = False
        else:
            # Access Pydantic model attributes directly
            self.voicemail_detect = voicemail_config.detect
            self.voicemail_action = voicemail_config.action
            self.voicemail_retry = voicemail_config.retry
        self.logger.debug(
            f"Voicemail config: detect: {self.voicemail_detect}, action: {self.voicemail_action}, retry: {self.voicemail_retry}"
        )

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, StartInterruptionFrame):
            await self.push_frame(frame, direction)
            return
        await super().process_frame(frame, direction)
        # Update mute status
        if isinstance(frame, STTMuteFrame):
            self.logger.debug(f"Setting mute to {frame.mute}")
            self.is_muted = frame.mute
        # elif isinstance(frame, BotStartedSpeakingFrame):
        #     if self.voicemail_detected:
        #         self.delivering_final_message = True

        # Track bot speaking status and trigger voicemail callback. The bot is unmuted after userstopped speaking frame is handled at stt_mute_filter, so we listen to this earlier than that here.
        # elif isinstance(frame, BotStoppedSpeakingFrame):
        #     self._first_speech_handled = True
        #     logger.debug("First speech handled set to true")
        #     if self.delivering_final_message:
        #         await self.end_callback(None)

        # Process transcriptions for voicemail and hold detection
        elif isinstance(frame, TranscriptionFrame):
            text = frame.text.lower()
            if self.is_muted:
                self.logger.debug(f"Transcript Frame:{text}")
                # Voicemail detection - only if voicemail_detect is True
                if (
                    self.voicemail_detect
                    and not self._first_speech_handled
                    and any(phrase in text for phrase in self.voicemail_phrases)
                ):
                    self.logger.debug("Voicemail detected")
                    self.function_call_monitor.append("voicemail_detected")
                    await self.push_frame(
                        VADParamsUpdateFrame(self.vad_params_bot_silent), FrameDirection.UPSTREAM
                    )
                    await self.push_frame(STTMuteFrame(mute=False), FrameDirection.UPSTREAM)

                    self.voicemail_detected = True

                    # Handle different voicemail actions
                    if self.voicemail_action == "summarise":
                        # Summarize the message for voicemail
                        await self.push_frame(
                            LLMMessagesAppendFrame(
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "The call has been forwarded to voicemail. So, first give a summary of the message you wanted to say to user, then call the end_call tool with a final message: 'thank you'.",
                                    }
                                ]
                            ),
                            FrameDirection.DOWNSTREAM,
                        )
                    elif self.voicemail_action == "end":
                        # Just end the call immediately
                        await self.end_callback(None)

                    # Interrupt the bot here as whatever it is saying wont be heard by user yet
                    await self.push_frame(BotInterruptionFrame(), FrameDirection.UPSTREAM)
            else:
                await self.push_frame(frame, direction)

        else:
            await self.push_frame(frame, direction)
