"""Flow-native switch_language tool implementation."""

from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
from pipecat.frames.frames import STTUpdateSettingsFrame, TTSUpdateSettingsFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.transcriptions.language import Language
from pipecat.services.google.tts import language_to_google_tts_language
from pipecat.services.tts_service import TTSService
from pipecat.services.google.tts import GoogleTTSService
from pipecat.services.azure import AzureTTSService
from google.cloud import texttospeech_v1

from typing import Union


LANGUAGE_MAP = {
    "english": Language.EN_IN,
    "hindi": Language.HI_IN,
    "telugu": Language.TE_IN,
    "tamil": Language.TA_IN,
    "kannada": Language.KN_IN,
}


async def switch_language(flow_manager: FlowManager, language: str) -> FlowResult:
    """
    Switch to this conversation language when the user asks explicitly asks you to do so.

    Args:
        language: The target language name (e.g., 'telugu', 'english', 'hindi', 'tamil', 'kannada').

    Returns:
        FlowResult indicating success or failure
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    monitor = s.get("function_call_monitor", [])
    tts = s.get("tts")
    tts_provider = s.get("tts_provider", s.get("telephony_provider"))

    language_name = language.lower()
    language_enum = LANGUAGE_MAP.get(language_name)

    monitor.append("called_switch_language")

    if not language_enum:
        if logger:
            logger.warning(f"Language '{language}' not supported")
        return ({"status": "error", "error": f"Language '{language}' not supported"}, None)

    try:
        voice = tts._voice_id if tts else None

        # Update STT (Upstream)
        stt_update_frame = STTUpdateSettingsFrame(settings={"language": language_enum})
        await flow_manager.llm.push_frame(stt_update_frame, FrameDirection.UPSTREAM)
        if logger:
            logger.info(f"Pushed STTUpdateSettingsFrame for {language_name} upstream")

        # Update TTS (Downstream)
        success_message = f"Switched language to {language_name}."
        
        if tts_provider == "azure":
            tts_update_frame = TTSUpdateSettingsFrame(settings={"language": language_enum})
            await flow_manager.llm.push_frame(tts_update_frame, FrameDirection.DOWNSTREAM)
            if logger:
                logger.info(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")
                
        elif tts_provider == "google" and tts:
            if "chirp" in voice.lower() and isinstance(tts, GoogleTTSService):
                if tts._voice_config.get("is_clone", False):
                    tts._voice = texttospeech_v1.VoiceSelectionParams(
                        language_code=str(language_to_google_tts_language(language_enum)).lower(),
                        voice_clone=tts._voice_clone_params,
                    )
                    success_message = f"Switched language to {language_name}."
                else:
                    current_language = tts._settings["language"]
                    voice = voice.lower().replace(current_language.lower() + "-", "")
                    voice = f"{str(language_to_google_tts_language(language_enum)).lower()}-{str(voice).lower()}"
                    if logger:
                        logger.info(
                            f"chirp voice changing from current_voice {current_language}, voice: {voice}, language: {language_enum}"
                        )
                    
                    tts_update_frame = TTSUpdateSettingsFrame(
                        settings={"language": language_enum, "voice": voice}
                    )
                    await flow_manager.llm.push_frame(tts_update_frame, FrameDirection.DOWNSTREAM)
                    if logger:
                        logger.info(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")
                    success_message = f"Switched language to {language_name}."
            else:
                if logger:
                    logger.info(
                        f"Switching language not supported for this TTS provider {tts_provider} and voice {voice}- not chirp"
                    )
                success_message = f"Switching language not supported for this TTS provider {tts_provider} and voice {voice}- not chirp"
        else:
            if logger:
                logger.info(
                    f"Switching language not supported for this TTS provider {tts_provider}"
                )
            success_message = (
                f"Switching language not supported for this TTS provider {tts_provider}"
            )

        return ({"status": success_message}, None)

    except Exception as e:
        if logger:
            logger.exception(f"Error switching language: {e}")
        return ({"status": "error", "error": "Failed to switch language"}, None)
