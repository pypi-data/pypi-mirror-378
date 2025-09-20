"""Plivo Chatbot Implementation.

This module sets up and runs the Plivo chatbot using various services and processors
from the Pipecat framework.
"""

# Standard Library Imports
import asyncio
from datetime import datetime, timezone
from optparse import Option
from typing import Optional

import aiohttp
import redis.asyncio as redis  # Added for Redis client type hinting

# Third-Party Imports
from cache import cache
from dotenv import load_dotenv
from env_config import api_config
from loguru import logger

# ToolsSchema no longer needed with Pipecat Flows
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.fal_smart_turn import FalSmartTurnAnalyzer

# from pipecat.audio.turn.smart_turn.local_smart_turn_v2 import LocalSmartTurnAnalyzerV2
# from pipecat.transcriptions.language import Language # Moved to switch_language.py

# First-Party Imports
from pipecat.frames.frames import BotStoppedSpeakingFrame, Frame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
)
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# Local Application Imports
from pipecat.processors.transcript_processor import TranscriptProcessor

from rag.weaviate_script import get_weaviate_client
from starlette.websockets import WebSocket

# from utils.analyzer_pool import get_smart_turn_pool
from utils.background_audio import background_audio_manager
from utils.callbacks import end_callback, warning_callback
from utils.frames_monitor import BotSpeakingFrameMonitor
from utils.generic_functions.cleanup import cleanup_connection
from utils.generic_functions.common import get_vad_params, is_arabic_present
from utils.generic_functions.response_handler import response_formatters

# Legacy LLM functions are no longer needed - replaced with flow-native implementations
from utils.pipeline import (
    initialise_dtmf_input,
    initialize_filler_config,
    initialize_hold_detector,
    initialize_stt_mute_strategy,
    initialize_user_idle,
    initialize_voicemail_detector,
)
from utils.stay_on_line_processor import StayOnLineProcessor

# Legacy tools no longer needed with Pipecat Flows
from utils.transcript import save_audio_to_file

from pipecat_flows import FlowManager
from utils.generate_config import (
    RunConfig,
    parse_flow_config_to_pipecat,
    generate_data_access_config,
)
from voice_services.webcall.webcall_params import WebCallParams
from transports.factory import build_transport
from utils.transcript import TextModeFrameMonitor
from utils.bot_common import (
    initialize_services,
    setup_vad_analyzer,
    create_transcript_handler,
    get_call_timing,
    setup_noise_filter,
)
from utils.participant_handler import ParticipantHandler

# Initialize Environment Variables
load_dotenv(override=True)

# sentry_sdk.init(
#     dsn=api_config.SENTRY_DSN,  # updated from os.getenv("SENTRY_DSN")
#     server_name=get_hostname(),
#     environment=api_config.ENVIRONMENT,  # updated from os.getenv("ENVIRONMENT")
#     sample_rate=0.5,
# )

# logger.remove(0)
# logger.add(sys.stderr, level="DEBUG")


# Define TTSCompletionListener
class TTSCompletionListener(FrameProcessor):  # noqa: D101
    def __init__(self, tts_done_event, **kwargs):  # noqa: D107
        super().__init__(**kwargs)
        self.tts_done_event = tts_done_event
        self.waiting_for_final_tts = False  # Initialize the flag

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await self.push_frame(frame, direction)
        if self.waiting_for_final_tts and isinstance(frame, BotStoppedSpeakingFrame):
            self.tts_done_event.set()
            self.waiting_for_final_tts = False  # Reset the flag


async def run_bot(
    websocket_client: Optional[WebSocket],  # Optional for Daily.co
    call_id,
    stream_id,
    callback_call_id,
    channel: str,
    runtime_config: Optional[RunConfig] = None,
    redis_client: redis.Redis = None,  # Added redis_client parameter
    webcall_params: Optional[WebCallParams] = None,  # Added for Daily.co integration
    webrtc_connection=None,
):
    bot_logger = logger.bind(call_id=callback_call_id or call_id)

    call_config = runtime_config.call_config
    flow_config = runtime_config.flow_config
    pipecat_flow_config = parse_flow_config_to_pipecat(flow_config)

    bot_logger.info(f"Parsed runtime config successfully")

    bot_logger.info(f"Call config: {call_config}")

    # Track call timing using common function
    timing = get_call_timing()
    call_start_time = timing["call_start_time"]
    call_end_time = timing["call_end_time"]
    call_duration = timing["call_duration"]
    function_call_monitor = list()
    # Configure background audio mixer if audio ID is provided
    background_mixer = None
    # prompt += "\nNote: Today's date is : " + time.strftime("%d %B,%Y and day is %A.")
    # Create audio buffer if recording locally
    audio_buffer = None
    if call_config.record_locally:
        audio_buffer = AudioBufferProcessor(
            buffer_size=0,  # Only trigger at end of recording
        )

        # Register event handler
        @audio_buffer.event_handler("on_audio_data")
        async def on_audio_data(buffer, audio, sample_rate, num_channels):
            await save_audio_to_file(audio, sample_rate, num_channels, callback_call_id or call_id)

    # Initialize Weaviate client if RAG is enabled
    weaviate_client = None
    if call_config.initialize_rag:
        weaviate_client = get_weaviate_client()
        await weaviate_client.connect()

    # Configure background audio mixer if audio ID is provided
    if call_config.background_audio_config:
        background_mixer = background_audio_manager.create_mixer_from_audio_config(
            call_config.background_audio_config
        )
        if background_mixer:
            bot_logger.info(
                f"Background audio enabled with audio ID: {call_config.background_audio_config.audio_id if call_config.background_audio_config else 'unknown'}"
            )
        else:
            bot_logger.warning(
                f"Failed to create background audio mixer for audio ID: {call_config.background_audio_config.audio_id if call_config.background_audio_config else 'unknown'}"
            )
    else:
        bot_logger.info("No background audio ID provided, skipping background audio")

    # Create the final_message_done_event for synchronization
    final_message_done_event = asyncio.Event()
    vad_params_speaking, vad_params_bot_silent = get_vad_params(
        call_config.advanced_vad,
        smart_turn_enabled=call_config.enable_smart_turn,
        vad_input=call_config.vad_input,
    )
    arabic_present = is_arabic_present(call_config.language, call_config.add_langs)

    bot_speaking_frame_monitor = BotSpeakingFrameMonitor(
        final_message_done_event, vad_params_bot_silent, vad_params_speaking
    )

    # Create VAD analyzer using common function
    vad_analyzer = setup_vad_analyzer(arabic_present)

    # Create transcript processor and handler
    transcript = TranscriptProcessor()
    transcript_handler = create_transcript_handler(
        bot_logger, channel, call_config, None
    )  # task will be set later

    # Create text mode interceptor for Daily text messaging

    # Idempotency flag and lock for cleanup
    cleaning_up = False
    cleanup_lock = asyncio.Lock()

    # Configure turn analyzer based on enable_smart_turn setting
    turn_analyzer = None
    fal_session = None
    if call_config.enable_smart_turn:
        fal_session = aiohttp.ClientSession()
        turn_analyzer = FalSmartTurnAnalyzer(
            api_key=api_config.FAL_API_KEY,
            aiohttp_session=fal_session,
            params=SmartTurnParams(stop_secs=0.75, pre_speech_ms=0.0, max_duration_secs=8.0),
        )
        bot_logger.info("FalSmartTurnAnalyzer enabled for semantic turn detection")

    # Check if this is a chat-only session
    is_chat_only = webcall_params and webcall_params.media_type == "text"

    # Initialize noise filter if configured
    noise_filter_obj = setup_noise_filter(call_config, call_id, callback_call_id, bot_logger)

    # Use transport factory to create appropriate transport
    transport, audio_in_sample_rate, audio_out_sample_rate = await build_transport(
        channel=channel,
        call_config=call_config,
        stream_id=stream_id,
        call_id=runtime_config.call_id,
        websocket_client=websocket_client,
        vad_analyzer=vad_analyzer,
        turn_analyzer=turn_analyzer,
        background_mixer=background_mixer,
        webcall_params=webcall_params,
        webrtc_connection=webrtc_connection,
        noise_filter=noise_filter_obj,
    )

    # Initialize all AI services using shared function
    # We need to generate nodes config first to pass TTS overrides to initialize_services
    # Generate runtime config for quick lookup
    nodes_data_access_config = generate_data_access_config(runtime_config, call_config)
    
    services = await initialize_services(call_id, call_config, bot_logger, {"nodes_runtime_config": nodes_data_access_config})
    llm = services["llm"]
    stt = services["stt"]
    tts = services["tts"]
    tts_service_map = services["tts_service_map"]

    # FlowManager will be initialized after task is created

    stay_on_line_processor = None

    # In the run_bot function, before defining end_call_function
    task_references = []

    # Initialize StayOnLineProcessor if needed (will be checked in flow config)
    # This can be conditionally created based on flow requirements
    stay_on_line_processor = StayOnLineProcessor(llm_provider=call_config.llm_provider)

    # Create initial context - tools will be managed by FlowManager
    context = OpenAILLMContext()

    # Add call_id and stream_id to context for end_call function
    context.call_id = call_id
    context.stream_id = stream_id
    context_aggregator = llm.create_context_aggregator(context)

    # Create a placeholder task for callback functions - will be replaced after pipeline creation
    task = None

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

    # Now create the full pipeline with user_idle and other components
    pipeline_steps = [
        transport.input(),  # Transport input from client
        user_idle,
    ]

    # Initialize DTMF aggregator (will be None for non-telephony)
    dtmf_aggregator = None

    # Common end callback for telephony features
    end_callback_func = lambda idle_proc: end_callback(
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
    )

    # Initialize mute strategy and STT for both channels (if not chat-only)
    if not is_chat_only:
        initialize_stt_mute_strategy(
            call_config.mute_during_intro, call_config.mute_while_bot_speaking, pipeline_steps
        )
        pipeline_steps.extend([stt])

    # Telephony-specific processors
    if channel == "telephony":
        initialize_voicemail_detector(
            call_config.mute_during_intro,
            call_config.mute_while_bot_speaking,
            call_config.voicemail,
            pipeline_steps,
            vad_params_bot_silent,
            end_callback_func,
            function_call_monitor,
        )

        initialize_hold_detector(
            call_config.call_hold_config,
            end_callback_func,
            pipeline_steps,
        )

        initialize_filler_config(
            call_config, transport, call_config.voice, call_config.language, pipeline_steps
        )

        if stay_on_line_processor:
            pipeline_steps.append(stay_on_line_processor)

        dtmf_aggregator = initialise_dtmf_input(call_config, pipeline_steps)

    # Add core processing pipeline
    if not is_chat_only:
        # Audio pipeline for voice calls
        pipeline_steps.extend(
            [
                transcript.user(),
                context_aggregator.user(),
                llm,
                tts,
                bot_speaking_frame_monitor,
                transport.output(),
            ]
        )
    else:
        # Text-only pipeline for chat (Daily channel only)
        text_monitor = TextModeFrameMonitor(transcript_handler)
        pipeline_steps.extend(
            [
                context_aggregator.user(),
                llm,
                text_monitor,
                context_aggregator.assistant(),
                transport.output(),
            ]
        )

    # Add audio buffer processor to pipeline if needed (only for audio mode)
    if call_config.record_locally and audio_buffer:
        logger.debug("Adding audio_buffer")
        pipeline_steps.append(audio_buffer)

    # Add transcript processors at the end like the original pattern
    if not is_chat_only:
        pipeline_steps.extend(
            [
                transcript.assistant(),
                context_aggregator.assistant(),
            ]
        )

    pipeline = Pipeline(pipeline_steps)

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            audio_in_sample_rate=audio_in_sample_rate,
            audio_out_sample_rate=audio_out_sample_rate,
            start_metadata={
                "voicemail_detect": call_config.voicemail.detect
                if call_config.voicemail
                else False,
                "call_id": callback_call_id or call_id,
            },
        ),
        conversation_id=str(callback_call_id or call_id),
    )

    # Set task reference for transcript handler
    transcript_handler.task = task

    # Prepare dependencies for flow handlers
    flow_dependencies = {
        "call_config": call_config,
        "tts_switcher": tts,
        "tts_service_map": tts_service_map,
        "weaviate_client": weaviate_client if call_config.initialize_rag else None,
        "collection_name": call_config.rag_collection_name,
        "facets_collection_name": call_config.rag_facets_collection_name,  # Add facets collection name
        "workspace_id": runtime_config.workspace_id,  # Add workspace_id for multi-tenancy
        "pre_query_phrases": call_config.pre_query_response_phrases,
        "cache": cache,
        "response_formatters": response_formatters,
        "function_call_monitor": function_call_monitor,
        "bot_logger": bot_logger,
        "telephony_provider": call_config.telephony_provider,
        "tts_provider": call_config.tts_provider,
        "call_id": call_id,
        "stream_id": stream_id,
        "websocket_client": websocket_client,
        "callback_call_id": callback_call_id,
        "context_aggregator": context_aggregator,
        "transcript_handler": transcript_handler,
        "task": task,
        "task_references": task_references,
        "bot_speaking_frame_monitor": bot_speaking_frame_monitor,
        "final_message_done_event": final_message_done_event,
        "transport": transport,
        "stay_on_line_processor": stay_on_line_processor,
        "dtmf_aggregator": dtmf_aggregator,  # Add DTMF aggregator for flow functions
        "nodes_runtime_config": nodes_data_access_config,
        # NEW: WebCall support
        "webcall_params": webcall_params,
        "channel": channel,
    }

    # Update pipecat flow config with dependencies
    pipecat_flow_config = parse_flow_config_to_pipecat(flow_config, deps=flow_dependencies)

    # Initialize flow manager with task
    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        flow_config=pipecat_flow_config,
    )

    
    # CRITICAL: Populate flow_manager.state with all dependencies that flow tools need
    flow_manager.state.update(flow_dependencies)

    bot_logger.info(f"FlowManager initialized with {len(flow_config.nodes)} nodes")
    bot_logger.info(f"Flow state populated with {len(flow_dependencies)} dependencies")
    bot_logger.info(
        f"Runtime functions config available for nodes: {list(nodes_data_access_config.keys())}"
    )

    # Initialize participant handler for all channels to handle initialization
    participant_handler = ParticipantHandler(
        transport=transport,
        channel=channel,
        call_config=call_config,
        audio_out_sample_rate=audio_out_sample_rate,
        task=task,
        audio_buffer=audio_buffer,
        background_mixer=background_mixer,
        flow_manager=flow_manager,
        bot_logger=bot_logger,
        transcript_handler=transcript_handler,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        await participant_handler.handle_client_connected()

    # Register participant event handlers only for daily channel
    if channel == "daily":
        participant_handler.register_event_handlers()

    # Register event handler for transcript updates
    @transcript.event_handler("on_transcript_update")
    async def on_transcript_update(processor, frame):
        await transcript_handler.on_transcript_update(processor, frame)

    # Text mode monitor is now part of the original pipeline, no need to rebuild

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        nonlocal cleaning_up, call_end_time, call_duration
        async with cleanup_lock:
            if cleaning_up:
                bot_logger.info("Cleanup already performed, skipping.")
                return
            cleaning_up = True

        bot_logger.info("Client disconnected, performing cleanup.")

        # Release Smart Turn analyzer back to pool if used
        # if smart_turn_pool and turn_analyzer:
        #     try:
        #         await smart_turn_pool.release(turn_analyzer)
        #         bot_logger.debug("Released Smart Turn analyzer back to pool")
        #     except Exception as e:
        #         bot_logger.error(f"Failed to release Smart Turn analyzer: {e}")

        # Calculate call end time and duration
        call_end_time = datetime.now(timezone.utc)
        call_duration = (call_end_time - call_start_time).total_seconds()

        # Stop audio recording if enabled
        try:
            if call_config.record_locally and audio_buffer:
                await audio_buffer.stop_recording()
        except Exception as e:
            bot_logger.error(f"Error stopping audio recording: {e}")

        # close weaviate connection
        try:
            if weaviate_client:
                await weaviate_client.close()
        except Exception as e:
            bot_logger.error(f"Error closing Weaviate connection: {e}")

        # Close FAL session if it was created
        if fal_session:
            try:
                await fal_session.close()
                bot_logger.debug("Closed FAL aiohttp session")
            except Exception as e:
                bot_logger.error(f"Error closing FAL session: {e}")

        await cleanup_connection(
            callback_call_id,
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            call_config.record_locally,
            call_config.telephony_provider,
            call_duration,
            # NEW: WebCall support
            webcall_params=webcall_params,
        )

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
