"""Transport factory for creating different transport types with appropriate configurations."""

from typing import Optional
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.turn.smart_turn.fal_smart_turn import FalSmartTurnAnalyzer
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)
from pipecat.transports.base_transport import TransportParams
from pipecat.serializers.plivo import PlivoFrameSerializer
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.serializers.exotel import ExotelFrameSerializer
from pipecat.serializers.convox import ConVoxFrameSerializer
from pipecat.serializers.asterisk import AsteriskFrameSerializer
from pipecat.serializers.custom import CustomFrameSerializer
from env_config import api_config
from utils.generate_config import CallConfig
from voice_services.webcall.webcall_params import WebCallParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport


def get_telephony_serialiser(provider, stream_id, call_id, codec=None, sample_rate=None):
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
    elif provider == "smallwebrtc":
        # WebRTC doesn't need a frame serializer - it's handled by SmallWebRTCTransport
        return None
    else:
        raise ValueError(f"Unknown telephony provider: {provider}")


async def build_transport(
    channel: str,
    call_config: CallConfig,
    stream_id: str,
    call_id: str,
    websocket_client=None,
    webcall_params: Optional[WebCallParams] = None,
    vad_analyzer=None,
    turn_analyzer=None,
    background_mixer=None,
    webrtc_connection=None,
    noise_filter=None,
):
    """
    Build the appropriate transport based on channel type.

    Args:
        channel: "telephony", "daily", or "smallwebrtc"
        call_config: Call configuration object
        stream_id: Stream identifier
        call_id: Call identifier
        websocket_client: WebSocket client for telephony
        daily_room_url: Daily room URL for web calls
        daily_bot_token: Daily bot token for web calls
        webrtc_connection: WebRTC connection for SmallWebRTC
        background_mixer: Audio mixer for background audio
        codec: Audio codec for telephony
        fal_session: FAL session for smart turn

    Returns:
        tuple: (transport, audio_in_sample_rate, audio_out_sample_rate)
    """
    if channel == "telephony":
        serializer = get_telephony_serialiser(
            call_config.telephony_provider, stream_id, call_id, call_config.codec,
            call_config.sample_rate
        )
        vad_analyzer = SileroVADAnalyzer()

        transport = FastAPIWebsocketTransport(
            websocket=websocket_client,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                add_wav_header=False,
                vad_enabled=True,
                vad_analyzer=vad_analyzer,
                turn_analyzer=turn_analyzer,
                audio_in_passthrough=True,
                serializer=serializer,
                audio_out_mixer=background_mixer,
                audio_in_filter=noise_filter,
            ),
        )

        # Determine sample rates based on provider
        if call_config.telephony_provider == "convox":
            audio_in_sample_rate = 16000
            audio_out_sample_rate = 16000
        else:
            audio_in_sample_rate = 8000
            audio_out_sample_rate = 8000

        # Override for specific providers that need 16kHz
        if call_config.stt_provider == "speechmatics" or call_config.enable_smart_turn:
            audio_in_sample_rate = 16000

        return transport, audio_in_sample_rate, audio_out_sample_rate

    elif channel == "daily":
        if not webcall_params:
            raise ValueError("webcall_params is required for Daily transport")

        # Check if this is a chat-only session
        is_chat_only = webcall_params.media_type == "text"
        is_audio_enabled = not is_chat_only

        # Only create VAD analyzer for audio sessions
        if is_audio_enabled and not vad_analyzer:
            vad_analyzer = SileroVADAnalyzer()

        transport = DailyTransport(
            room_url=webcall_params.room_url,
            token=webcall_params.bot_token,
            bot_name=webcall_params.bot_name,
            params=DailyParams(
                audio_in_enabled=is_audio_enabled,
                audio_out_enabled=is_audio_enabled,
                transcription_enabled=False,
                vad_analyzer=vad_analyzer if is_audio_enabled else None,
            ),
        )

        # Return appropriate sample rates based on media type
        if is_chat_only:
            # For chat-only, audio sample rates are irrelevant
            return transport, 0, 0
        else:
            # Use wideband audio for web calls with audio
            return transport, 16000, 24000

    elif channel == "smallwebrtc":
        vad_analyzer = SileroVADAnalyzer()
        # Configure turn analyzer if smart turn is enabled
        # Create SmallWebRTC transport
        transport = SmallWebRTCTransport(
            webrtc_connection=webrtc_connection,
            params=TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad_analyzer,
            ),
        )

        # Use wideband audio for WebRTC calls
        return transport, 16000, 24000

    else:
        raise ValueError(f"Unknown channel: {channel}")
