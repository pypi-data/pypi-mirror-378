"""Common functions shared between bot.py and bot_with_flows.py."""

import redis.asyncio as redis
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.filters.pyrnn_local_filter import PyRnnNoiseLocalFilter
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.processors.transcript_processor import TranscriptProcessor
from pipecat.serializers.convox import ConVoxFrameSerializer
from pipecat.serializers.exotel import ExotelFrameSerializer
from pipecat.serializers.plivo import PlivoFrameSerializer
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.serializers.asterisk import AsteriskFrameSerializer
from pipecat.serializers.custom import CustomFrameSerializer
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.pipeline.tts_switcher import TTSSwitcher
from pipecat.pipeline.service_switcher import ServiceSwitcherStrategyManual

from env_config import api_config
from utils.llm import initialize_llm_service
from utils.stt import initialize_stt_service
from utils.tts import initialize_tts_service, format_tts_text
from utils.transcript import TranscriptHandler, save_audio_to_file
from utils.pipeline import (
    initialise_dtmf_input,
    initialize_filler_config,
    initialize_hold_detector,
    initialize_stt_mute_strategy,
    initialize_user_idle,
    initialize_voicemail_detector,
)
from utils.stay_on_line_processor import StayOnLineProcessor
from utils.frames_monitor import BotSpeakingFrameMonitor
from utils.callbacks import end_callback, warning_callback
from utils.background_audio import background_audio_manager


def get_telephony_serialiser(
    provider: str, stream_id: str, call_id: str, codec: Optional[str] = None, sample_rate: Optional[int] = None
):
    """Get the appropriate serializer for telephony providers."""
    if provider == "plivo":
        return PlivoFrameSerializer(
            stream_id=stream_id, params=PlivoFrameSerializer.InputParams(auto_hang_up=False)
        )
    elif provider == "twilio":
        return TwilioFrameSerializer(
            stream_sid=stream_id,
            call_sid=call_id,
            account_sid=api_config.TWILIO_ACCOUNT_SID,
            auth_token=api_config.TWILIO_AUTH_TOKEN,
            params=TwilioFrameSerializer.InputParams(auto_hang_up=True),
        )
    elif provider == "exotel":
        return ExotelFrameSerializer(stream_sid=stream_id)
    elif provider == "asterisk":
        # Use codec if provided, otherwise default to pcmu
        telephony_encoding = codec or "pcmu"
        return AsteriskFrameSerializer(
            stream_id=stream_id,
            params=AsteriskFrameSerializer.InputParams(
                auto_hang_up=True, telephony_encoding=telephony_encoding
            ),
        )
    elif provider == "convox":
        # ConVox sends 16kHz audio
        return ConVoxFrameSerializer(
            stream_id=stream_id,
            params=ConVoxFrameSerializer.InputParams(convox_sample_rate=16000, auto_hang_up=False),
        )
    elif provider == "custom":
        # Use the new CustomFrameSerializer for external/custom telephony
        return CustomFrameSerializer(
            stream_sid=stream_id,
            call_sid=call_id,
            params=CustomFrameSerializer.InputParams(
                codec=codec or "pcmu",
                custom_sample_rate=sample_rate or 8000
            )
        )
    else:
        raise ValueError(f"Unknown telephony provider: {provider}")


def create_tts_switcher(call_config, bot_logger, tts_params, runtime_config=None):
    """Create TTSSwitcher with TTS service instances based on actual flow overrides."""
    
    # Store TTS services and their configuration mapping
    tts_services = []
    tts_service_map = {}
    
    # Create default TTS service based on call_config
    default_config_key = f"{call_config.tts_provider}_{call_config.voice}_{call_config.language}"
    default_tts = initialize_tts_service(
        tts_provider=call_config.tts_provider,
        language=call_config.language,
        voice=call_config.voice,
        tts_model=call_config.tts_model,
        **tts_params
    )
    tts_services.append(default_tts)
    tts_service_map[default_config_key] = default_tts
    
    bot_logger.info(f"Created default TTS service: {call_config.tts_provider}/{call_config.voice}")
    
    # Collect TTS overrides from runtime config if provided
    if runtime_config:
        nodes_runtime_config = runtime_config.get("nodes_runtime_config", {})
        
        for node_id, node_runtime in nodes_runtime_config.items():
            resolved_overrides = node_runtime.get("resolved_overrides", {})
            tts_override = resolved_overrides.get("tts")
            
            if tts_override:
                provider = tts_override.get("provider", call_config.tts_provider)
                voice_id = tts_override.get("voice_id", call_config.voice)
                language = tts_override.get("language", call_config.language)
                voice_model = tts_override.get("voice_model", call_config.tts_model)
                
                config_key = f"{provider}_{voice_id}_{language}"
                
                # Skip if we already have this configuration
                if config_key in tts_service_map:
                    bot_logger.debug(f"TTS config {config_key} already exists for node {node_id}")
                    continue
                
                try:
                    tts_service = initialize_tts_service(
                        tts_provider=provider,
                        language=language,
                        voice=voice_id,
                        tts_model=voice_model,
                        **tts_params
                    )
                    tts_services.append(tts_service)
                    tts_service_map[config_key] = tts_service
                    bot_logger.info(f"Created TTS service for node {node_id}: {provider}/{voice_id}/{language}")
                    
                except Exception as e:
                    bot_logger.warning(f"Failed to create TTS service {provider}/{voice_id} for node {node_id}: {e}")
                    continue
    
    # Create TTSSwitcher with all TTS services
    if len(tts_services) > 1:
        tts_switcher = TTSSwitcher(tts_services, ServiceSwitcherStrategyManual)
        bot_logger.info(f"Created TTSSwitcher with {len(tts_services)} TTS services")
        return tts_switcher, tts_service_map
    else:
        # Fallback to single service if only one was created
        bot_logger.info("Using single TTS service (no switcher needed)")
        return default_tts, tts_service_map


async def initialize_services(call_id, call_config, bot_logger, runtime_config=None):
    """Initialize LLM, STT, and TTS services based on call configuration."""
    services = {}
    use_v2_key = call_config.use_elevenlabs_v2_key
    if use_v2_key:
        elevenlabs_api_key = api_config.ELEVENLABS_API_KEY_V2
        bot_logger.info("Using Elevenlabs V2 API key")
    else:
        elevenlabs_api_key = api_config.ELEVENLABS_API_KEY
        bot_logger.info("Using default Elevenlabs API key")

    llm_kwargs = {"azure_deployment": call_config.azure_deployment}
    # Initialize LLM
    if call_config.llm_provider == "vistaar":
        vistaar_language = call_config.language.split("-")[0]
        llm_kwargs.update(
            {
                "session_id": call_id,
                "source_lang": vistaar_language,
                "target_lang": vistaar_language,
                "base_url": api_config.VISTAAR_API_BASE_URL,
                "pre_query_response_phrases": call_config.pre_query_response_phrases,
            }
        )

    services["llm"] = initialize_llm_service(
        llm_provider=call_config.llm_provider,
        llm_model=call_config.llm_model,
        temperature=call_config.llm_temperature,
        **llm_kwargs,
    )

    bot_logger.info(
        f"LLM service initialized successfully: {call_config.llm_provider}/{call_config.llm_model}"
    )

    # Initialize STT
    services["stt"] = initialize_stt_service(
        stt_provider=call_config.stt_provider,
        language=call_config.language,
        stt_model=call_config.stt_model,
        additional_languages=call_config.add_langs,
        logger=bot_logger,
        record_locally=call_config.record_locally,
        vocab=call_config.vocab,
    )

    # Store all TTS parameters for dynamic switching
    tts_params = {
        "azure_api_key": api_config.AZURE_SPEECH_API_KEY,
        "azure_region": api_config.AZURE_SPEECH_REGION,
        "elevenlabs_api_key": elevenlabs_api_key,
        "google_credentials_path": "creds.json",
        "deepgram_api_key": api_config.DEEPGRAM_API_KEY,
        "cartesia_api_key": api_config.CARTESIA_API_KEY,
        "sarvam_api_key": api_config.SARVAM_API_KEY,
        "voice_config": call_config.voice_config.model_dump() if call_config.voice_config else None,
        "text_formatter": lambda text, lang_code: format_tts_text(
            text, lang_code, dialect=call_config.dialect
        ),
    }
    
    # Create TTS switcher with multiple TTS services based on overrides
    tts_switcher, tts_service_map = create_tts_switcher(
        call_config, bot_logger, tts_params, runtime_config
    )
    
    services["tts"] = tts_switcher
    services["tts_service_map"] = tts_service_map


    return services


def setup_context_aggregators(context: Optional[Dict[str, Any]] = None):
    """Setup OpenAI context aggregators."""
    if context and "messages" in context and "tools_schema" in context:
        # Create context with messages and tools_schema like in the original bot.py
        context_obj = OpenAILLMContext(context["messages"], context["tools_schema"])
    else:
        # Fallback to empty context
        context_obj = OpenAILLMContext()

    return context_obj


def create_transcript_handler(logger, channel=None, call_config=None, task=None):
    """Create and return a TranscriptHandler instance."""
    return TranscriptHandler(logger, channel, call_config, task)


def create_audio_buffer(
    call_id, sample_rate: int = 16000, channels: int = 1
) -> AudioBufferProcessor:
    """Create audio buffer processor for recording."""
    return AudioBufferProcessor(
        callback=lambda audio: save_audio_to_file(
            audio_data=audio,
            sample_rate=sample_rate,
            num_channels=channels,
            call_id=call_id,
        )
    )


def setup_idle_handlers(
    call_config,
    task,
    task_references,
    function_call_monitor,
    bot_logger,
    bot_speaking_frame_monitor,
    call_id,
    stream_id,
    websocket_client,
    callback_call_id,
    context_aggregator,
    context,
    transcript_handler,
    transport,
):
    """Setup idle timeout and warning handlers."""
    user_idle = initialize_user_idle(
        call_config.idle_timeout_warning,
        call_config.idle_timeout_end,
        lambda idle_proc: end_callback(
            idle_proc,
            call_config.telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            transport,
            call_config.record_locally,
        ),
        lambda idle_proc: warning_callback(
            idle_proc,
            user_idle,
            context,
            function_call_monitor,
            call_config.llm_provider,
            bot_logger,
        ),
    )
    return user_idle


def setup_stay_on_line_processor(
    call_config,
    bot_logger,
    task,
    context_aggregator,
    bot_speaking_frame_monitor,
    stay_on_line_needed: bool = False,
):
    """Setup stay on line processor if needed."""
    if not stay_on_line_needed:
        return None

    return StayOnLineProcessor(
        task=task,
        llm_context=context_aggregator,
        bot_logger=bot_logger,
        llm_provider=call_config.llm_provider,
        llm_model=call_config.llm_model,
        bot_speaking_frame_monitor=bot_speaking_frame_monitor,
    )


def setup_vad_analyzer(is_arabic_present: Optional[bool] = False):
    """Setup VAD analyzer."""
    return (
        SileroVADAnalyzer(model_name="silero_vad_v2.onnx")
        if is_arabic_present
        else SileroVADAnalyzer()
    )


def get_call_timing():
    """Get initial call timing data."""
    return {
        "call_start_time": datetime.now(timezone.utc),
        "call_end_time": None,
        "call_duration": None,
    }


async def setup_redis_client(redis_client: Optional[redis.Redis] = None) -> redis.Redis:
    """Setup or reuse Redis client."""
    if redis_client:
        return redis_client

    # Create new Redis client if not provided
    redis_pool = redis.ConnectionPool.from_url(
        api_config.REDIS_URL, decode_responses=False, max_connections=20
    )
    return redis.Redis(connection_pool=redis_pool)


def setup_noise_filter(call_config, call_id: str, callback_call_id: str, bot_logger):
    """Setup noise filter based on configuration."""
    noise_filter_obj = None
    if call_config.noise_filter_config:
        if call_config.noise_filter_config.filter_noise:
            noise_filter_method = call_config.noise_filter_config.method
            if noise_filter_method == "pyrnn_filter":
                bot_logger.info("Using pyrnn_filter for filtering of noise")
                noise_filter_obj = PyRnnNoiseLocalFilter(call_id=call_id or callback_call_id)
            else:
                bot_logger.info(
                    "No other noise filter method supported other than pyrnn_filter defaulting to that"
                )
                noise_filter_method = "pyrnn_filter"
                noise_filter_obj = PyRnnNoiseLocalFilter(call_id=call_id or callback_call_id)
        else:
            bot_logger.info("No noise filtering required")
            noise_filter_obj = None
    else:
        bot_logger.info("No noise filter configuration provided")

    return noise_filter_obj
