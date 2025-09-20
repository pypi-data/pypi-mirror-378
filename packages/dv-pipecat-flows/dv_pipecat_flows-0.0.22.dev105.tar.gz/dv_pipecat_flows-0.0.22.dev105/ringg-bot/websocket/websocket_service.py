import asyncio
import json
import urllib.parse
import traceback
import bot
import bot_with_flows
from fastapi import WebSocket
from loguru import logger
from voice_services.common import (
    get_runtime_config,
    get_redis_client,
    get_websocket_connections,
    get_agent_config,
    set_agent_config,
    replace_template_variables,
    set_runtime_config,
)
from env_config import api_config
from utils.http_client import create_http_client_session
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object


class WebSocketService:  # noqa: D101
    def __init__(self):  # noqa: D107
        pass

    async def handle_connection(self, websocket: WebSocket, callback_call_id: str = None):
        """Handle unified WebSocket connection for all telephony providers."""
        websocket_connections = get_websocket_connections()
        redis_client = get_redis_client()

        msg = await websocket.receive_json()
        stream_id = None
        call_id = None
        telephony_provider = None

        print("here is the", callback_call_id)

        if msg.get("event") == "connected":
            # Twilio: consume the next 'start' event
            msg = await websocket.receive_json()
            if msg.get("event") != "start":
                raise ValueError(f"Expected 'start' event, got {msg.get('event')}")
            start = msg["start"]
            stream_id = start["streamSid"]
            call_id = start["callSid"]
            # Extract customParameters for callback_call_id
            custom = start.get("customParameters", {})
            print("here is the custom parameters", custom)
            callback_call_id = custom.get("callback_call_id")
            telephony_provider = "twilio"

        elif msg.get("event") == "start":
            # Plivo: single 'start' event flow
            start = msg["start"]
            stream_id = start["streamId"]
            call_id = start["callId"]
            telephony_provider = "plivo"

        websocket_connections[callback_call_id] = websocket

        logger.info("WebSocket connection accepted", call_id=callback_call_id)

        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        logger.info("Stream ID: {}".format(stream_id), call_id=callback_call_id)

        if not call_id:
            raise ValueError("Call ID not found in connection data")

        runtime_config = await get_runtime_config(callback_call_id)
        runtime_config.call_config.telephony_provider = telephony_provider

        # Check orchestration mode to determine which bot to use
        orchestration_mode = runtime_config.orchestration_mode

        if orchestration_mode == "single_node":
            # Use simple bot without flows
            run_bot = bot.run_bot
            logger.info(f"Using single_node bot for call {callback_call_id}")
        else:
            # Use bot with flows
            run_bot = bot_with_flows.run_bot
            logger.info(f"Using multi_node bot with flows for call {callback_call_id}")

        # Run the bot with the established WebSocket connection and stream ID
        await run_bot(
            websocket_client=websocket,
            call_id=call_id,
            stream_id=stream_id,
            callback_call_id=callback_call_id,
            channel="telephony",
            runtime_config=runtime_config,
            redis_client=redis_client,
        )

    async def handle_external_connection(
        self, websocket: WebSocket, telephony: str = None, agent_id: str = None
    ):
        """Handle external WebSocket connection for custom clients with Ringg AI protocol support."""
        websocket_connections = get_websocket_connections()
        redis_client = get_redis_client()

        # Wait for the initial connection message
        start_event = await websocket.receive_json()
        logger.debug("Start event received: {}", start_event, call_id=agent_id)

        if start_event.get("event") != "start":
            raise ValueError("Expected 'start' event not received")

        # Handle Ringg AI WebSocket protocol format
        if telephony == "custom":
            # Extract details from Ringg AI format
            start_data = start_event.get("start", {})
            agent_data = start_event.get("agent", {})

            stream_id = start_data.get("stream_sid")
            call_id = start_data.get("call_sid")
            codec = start_data.get("codec", "pcmu")  # Default to pcmu
            sample_rate = start_data.get("sample_rate", 8000)  # Default to 8kHz

            # Validate agent configuration
            event_agent_id = agent_data.get("id")
            if event_agent_id != agent_id:
                raise ValueError(
                    f"Agent ID mismatch: query param {agent_id} vs message {event_agent_id}"
                )

            custom_vars = agent_data.get("custom_vars", {})

            logger.debug(
                f"Ringg AI protocol - Agent: {agent_id}, Codec: {codec}, Sample rate: {sample_rate}Hz, Custom vars: {str(custom_vars)}",
                call_id=call_id,
            )

            # Try to get agent config from Redis cache first
            agent_config = await get_agent_config(agent_id)

            if not agent_config:
                # Fetch agent config from calling backend
                try:
                    url = f"{api_config.CALLING_BACKEND_URL}/calling/inbound"

                    logger.info(
                        f"Fetching agent config from backend for agent_id: {agent_id}",
                        call_id=call_id,
                    )

                    async with create_http_client_session() as session:
                        async with session.post(
                            url,
                            json={
                                "agent_id": agent_id,  # Pass agent_id instead of from_number
                                "call_sid": call_id,
                                "calling_source": "custom",
                            },
                            headers={"X-API-KEY": api_config.X_API_KEY},
                        ) as response:
                            response.raise_for_status()
                            agent_config = await response.json()
                            print(agent_config)

                            if agent_config:
                                # Cache agent config in Redis with 30 min TTL
                                await set_agent_config(agent_id, agent_config, ttl_minutes=30)
                                logger.info(
                                    f"Agent config cached for agent_id: {agent_id}", call_id=call_id
                                )
                            else:
                                logger.error(
                                    f"No agent config received from backend for agent_id: {agent_id}",
                                    call_id=call_id,
                                )
                                raise ValueError("Agent configuration not found")

                except Exception as e:
                    logger.error(f"Failed to fetch agent config from backend: {e}", call_id=call_id)
                    raise ValueError(f"Failed to fetch agent configuration: {str(e)}")
            else:
                logger.info(f"Using cached agent config for agent_id: {agent_id}", call_id=call_id)

            # Convert agent_config (dict) to RunConfig object
            runtime_config = generate_runtime_config_object(agent_config)

            # Apply variable replacement to prompt and intro_message
            if runtime_config.call_config.prompt:
                runtime_config.call_config.prompt = replace_template_variables(
                    runtime_config.call_config.prompt, custom_vars
                )

            if runtime_config.call_config.intro_message:
                runtime_config.call_config.intro_message = replace_template_variables(
                    runtime_config.call_config.intro_message, custom_vars
                )

            # Override telephony provider and codec settings for custom telephony
            runtime_config.call_config.telephony_provider = "custom"
            runtime_config.call_config.codec = codec
            runtime_config.call_config.sample_rate = sample_rate
            runtime_config.call_config.record = (
                True  # Always enable recording for external/custom calls
            )

        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        if not call_id:
            raise ValueError("Call ID not found in connection data")

        logger.debug(f"Stream ID: {stream_id}", call_id=call_id)
        websocket_connections[call_id] = websocket

        # Check orchestration mode to determine which bot to use
        orchestration_mode = runtime_config.orchestration_mode

        if orchestration_mode == "single_node":
            # Use simple bot without flows
            run_bot = bot.run_bot
            logger.debug(f"Using single_node bot for call {call_id}")
        else:
            # Use bot with flows
            run_bot = bot_with_flows.run_bot
            logger.debug(f"Using multi_node bot with flows for call {call_id}")

        # Run the bot with the established WebSocket connection and stream ID
        await run_bot(
            websocket_client=websocket,
            call_id=call_id,
            stream_id=stream_id,
            callback_call_id=call_id,
            channel="telephony",
            runtime_config=runtime_config,
            redis_client=redis_client,
        )

        return call_id

    async def handle_exotel_connection(self, websocket: WebSocket, callback_call_id: str):
        """Handle Exotel WebSocket connection."""
        websocket_connections = get_websocket_connections()
        redis_client = get_redis_client()

        connected_event = await websocket.receive_json()
        if connected_event.get("event") != "connected":
            raise ValueError("Expected 'connected' event not received")

        start_event = await websocket.receive_json()
        logger.info(f"Start event received: {start_event} for {callback_call_id}")
        if start_event.get("event") != "start":
            raise ValueError("Expected 'start' event not received")

        callback_call_id = next(iter(start_event.get("start").get("custom_parameters")))
        websocket_connections[callback_call_id] = websocket

        stream_id = start_event.get("start").get("stream_sid")
        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        logger.info(f"Stream ID: {stream_id}")

        call_id = start_event.get("start").get("call_sid")
        if not call_id:
            raise ValueError("Call ID not found in connection data")

        runtime_config = await get_runtime_config(callback_call_id)
        logger.info(f"Runtime config {runtime_config}")
        runtime_config.call_config.telephony_provider = "exotel"

        # Check orchestration mode to determine which bot to use
        orchestration_mode = runtime_config.orchestration_mode

        if orchestration_mode == "single_node":
            # Use simple bot without flows
            run_bot = bot.run_bot
            logger.info(f"Using single_node bot for call {callback_call_id}")
        else:
            # Use bot with flows
            run_bot = bot_with_flows.run_bot
            logger.info(f"Using multi_node bot with flows for call {callback_call_id}")

        await run_bot(
            websocket_client=websocket,
            call_id=call_id,
            stream_id=stream_id,
            callback_call_id=callback_call_id,
            channel="telephony",
            runtime_config=runtime_config,
            redis_client=redis_client,
        )

    async def handle_convox_connection(self, websocket: WebSocket):
        """Handle ConVox WebSocket connection."""
        websocket_connections = get_websocket_connections()
        redis_client = get_redis_client()

        # Initialize variables to avoid UnboundLocalError
        call_id = None
        final_call_id = None
        start_event = None

        connection_event = await websocket.receive_json()
        logger.info(f"ConVox first event received: {connection_event}")

        event_type = connection_event.get("event") or connection_event.get("event_type")

        if event_type == "connected":
            call_id = connection_event.get("callid")
            caller = connection_event.get("caller")
            if caller and caller.startswith("+"):
                caller = caller[1:]

            start_event = await websocket.receive_json()
            logger.info(f"ConVox start event received: {start_event}")

            if start_event.get("event") != "start":
                raise ValueError(
                    f"Expected 'start' event after connection, got '{start_event.get('event')}'"
                )

        elif event_type == "start":
            start_event = connection_event
            logger.info(f"ConVox start event received as first event: {start_event}")

            start_details = start_event.get("start", {})
            call_id = start_details.get("callId")

        else:
            logger.warning(f"Unexpected first event type: {event_type}, treating as start event")
            start_event = connection_event
            start_details = start_event.get("start", {})
            call_id = start_details.get("callId") or connection_event.get("callid")

        # Extract details from start event
        start_details = start_event.get("start", {})
        stream_id = start_details.get("streamId")

        final_call_id = start_details.get("callId", start_details.get("call_id", call_id))
        final_callback_id = final_call_id

        if not final_call_id:
            raise ValueError("Call ID not found in ConVox events")

        # Store WebSocket connection
        websocket_connections[final_callback_id] = websocket

        # Get stored runtime config for ConVox
        runtime_config = await get_runtime_config(final_callback_id)
        if not runtime_config:
            raise ValueError(f"Runtime config not found for ConVox call ID: {final_callback_id}")

        runtime_config.call_config.telephony_provider = "convox"

        logger.info(
            f"ConVox Stream ID: {stream_id}, Call ID: {final_call_id}", call_id=final_call_id
        )

        # Send success response to ConVox for start event
        await websocket.send_json(
            {
                "status": "success",
                "message": "call_start event has been received and call session initiated",
            }
        )

        # Check orchestration mode to determine which bot to use
        orchestration_mode = runtime_config.get("orchestration_mode", "multi_node")

        if orchestration_mode == "single_node":
            # Use simple bot without flows
            run_bot = bot.run_bot
            logger.info(f"Using single_node bot for call {final_callback_id}")
        else:
            # Use bot with flows
            run_bot = bot_with_flows.run_bot
            logger.info(f"Using multi_node bot with flows for call {final_callback_id}")

        # Run the bot with ConVox WebSocket connection
        await run_bot(
            websocket_client=websocket,
            call_id=final_call_id,
            stream_id=stream_id,
            callback_call_id=final_callback_id,
            channel="telephony",
            runtime_config=runtime_config,
            redis_client=redis_client,
        )

        return final_call_id

    async def handle_asterisk_connection(
        self,
        websocket: WebSocket,
        call_id: str,
        encoding: str = "pcmu",
        tenant: str = "default",
        provider: str = None,
        ubona_did: str = None,
        ubona_cli: str = None,
    ):
        """Handle Asterisk WebSocket connection."""
        websocket_connections = get_websocket_connections()
        redis_client = get_redis_client()

        # Constants
        ASTERISK = "asterisk"
        UBONA = "ubona"

        try:
            # 1) Wait for "start" message from the bridge (with timeout)
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            print(f"Raw message received from Asterisk bridge: {msg}")

            # Clean and parse JSON message
            try:
                # Strip whitespace and newlines that might cause parsing issues
                clean_msg = msg.strip()
                start = json.loads(clean_msg)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from Asterisk bridge: {e}, raw message: {repr(msg)}")
                logger.error(
                    "Failed to parse JSON from Asterisk bridge",
                    call_id=call_id,
                )
                await websocket.close()
                return

            if start.get("event") != "start":
                logger.error(
                    f"Asterisk: did not receive 'start' within 5s, got: {start.get('event')}"
                )
                await websocket.close()
                return

            # Debug: Log available sources for call_id extraction
            variables = start.get("variables", {})
            app_args = start.get("app_args")
            channel_id = start.get("channel_id")

            print(
                f"Call ID extraction sources - variables: {variables}, app_args: {app_args}, query_call_id: {call_id}, channel_id: {channel_id}",
            )

            # Extract call_id from start message - try multiple sources
            # Priority: X_CALL_ID variable > app_args[0] > query param > channel_id
            start_call_id = None

            if variables and "X_CALL_ID" in variables:
                start_call_id = variables["X_CALL_ID"]
            elif app_args:
                start_call_id = app_args[0] if isinstance(app_args, list) else app_args
            elif call_id:
                start_call_id = call_id
            else:
                start_call_id = channel_id or call_id

            final_call_id = start_call_id or call_id

            await websocket.send_text(json.dumps({"event": "started", "streamId": final_call_id}))
            logger.info(
                f"STARTED call_id={final_call_id} encoding={encoding}",
                call_id=final_call_id,
            )
            websocket_connections[final_call_id] = websocket

            # Detect if this is a Ubona call
            is_ubona_call = False

            if provider == "ubona":
                is_ubona_call = True
                from_number = ubona_cli.strip() if ubona_cli else None
                to_number = ubona_did.strip() if ubona_did else None

                logger.info(
                    f"Detected Ubona call - DID: {to_number}, CLI: {from_number}",
                    call_id=final_call_id,
                )

                if not from_number or not to_number:
                    logger.error(
                        f"No from_number or to_number found for Ubona call", call_id=final_call_id
                    )
                    await websocket.close(code=1008)  # Policy Violation
                    return

            # Get call config - for Ubona calls, fetch from backend first
            if is_ubona_call:
                # For Ubona calls, make backend API call to get call config
                try:
                    url = f"{api_config.CALLING_BACKEND_URL}/calling/inbound"

                    logger.info(
                        f"Making backend API call for Ubona - from: {from_number}, to: {to_number}",
                        call_id=final_call_id,
                    )

                    async with create_http_client_session() as session:
                        async with session.post(
                            url,
                            json={
                                "from_number": from_number,
                                "to_number": to_number,
                                "call_sid": final_call_id,
                                "calling_source": UBONA,
                            },
                        ) as response:
                            response.raise_for_status()
                            call_details = await response.json()
                            if call_details:
                                parsed_config = generate_runtime_config_object(call_details)
                                call_config_validator(parsed_config.call_config)
                                await set_runtime_config(final_call_id, call_details)
                            else:
                                logger.warning(
                                    f"No call_config in backend response for Ubona call",
                                    call_id=final_call_id,
                                )

                except Exception as e:
                    logger.error(
                        f"Failed to get Ubona call config from backend: {e}", call_id=final_call_id
                    )
                    await websocket.close(code=1008)  # Policy Violation
                    return
            # For regular Asterisk calls, get from Redis cache

            runtime_config = await get_runtime_config(final_call_id)

            if not runtime_config:
                logger.error(f"No call_config for {final_call_id}; closing")
                await websocket.close(code=1008)  # Policy Violation
                return

            runtime_config.call_config.telephony_provider = ASTERISK
            runtime_config.call_config.record_locally = (
                True  # Enable recording by default for Asterisk
            )

            # Determine which bot to use based on orchestration mode
            orchestration_mode = runtime_config.orchestration_mode
            if orchestration_mode == "single_node":
                run_bot = bot.run_bot
                logger.info(f"Using single_node bot for call {final_call_id}")
            else:
                run_bot = bot_with_flows.run_bot
                logger.info(f"Using multi_node bot with flows for call {final_call_id}")

            await run_bot(
                websocket_client=websocket,
                call_id=final_call_id,
                stream_id=final_call_id,
                callback_call_id=final_call_id,
                channel="telephony",
                runtime_config=runtime_config,
                redis_client=redis_client,
            )

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for start event from Asterisk bridge", call_id=call_id)
            await websocket.close()
        except Exception as e:
            traceback.print_exc()
            logger.exception("Unhandled error in asterisk websocket: {}", str(e), call_id=call_id)

        return final_call_id

    async def cleanup_connection(self, call_id: str):
        """Clean up WebSocket connection."""
        websocket_connections = get_websocket_connections()
        websocket_connections.pop(call_id, None)
