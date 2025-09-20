"""
Async Asterisk ARI API client implementation using aiohttp.

This module provides an async client for Asterisk's REST Interface (ARI),
designed for non-blocking origination of calls and channel management.
"""

import asyncio
import base64
import json
from typing import Any, Dict, Optional

import aiohttp
from loguru import logger
from utils.http_client import get_default_connector, get_default_timeout


class AsyncAsteriskARIError(Exception):
    """Exception raised for Asterisk ARI API errors."""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        is_retryable: bool = True,
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.is_retryable = is_retryable
        super().__init__(f"Asterisk ARI Error {status_code}: {message}")


class AsyncAsteriskARIClient:
    """Async implementation of Asterisk ARI API."""

    def __init__(self, ari_url: str, username: str, password: str, session: aiohttp.ClientSession):
        self.ari_url = ari_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = session

        # Create basic auth header
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

    async def originate_call(
        self,
        endpoint: str,
        app: str,
        caller_id: str,
        variables: Optional[Dict[str, Any]] = None,
        app_args: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Originate an outbound call through Asterisk ARI.

        Args:
            endpoint: The dial URI (e.g. "PJSIP/{number}@{trunk}")
            app: The Stasis application to send the call to
            caller_id: Caller ID to set (e.g. "Name <+1234567890>")
            variables: Channel variables to set
            app_args: Arguments to pass to the Stasis app
            timeout: Call timeout in seconds

        Returns:
            Dict containing the channel information from ARI
        """
        url = f"{self.ari_url}/channels"

        params = {
            "endpoint": endpoint,
            "app": app,  # just the app name
            "callerId": caller_id,
            "timeout": timeout,
        }
        if app_args:
            params["appArgs"] = app_args

        body = {}
        if variables:
            body["variables"] = variables  # in body, not stringified

        # Debug logging
        # logger.debug(f"ARI originate call - params: {params}")
        # logger.debug(f"ARI originate call - body: {body}")

        try:
            async with self.session.post(
                url,
                params=params,
                json=body,  # not stringified params
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=45.0),
            ) as response:
                response_text = await response.text()

                if response.status in (200, 201, 202):
                    try:
                        data = json.loads(response_text) if response_text else {}
                        logger.info(
                            f"Asterisk call originated successfully: {data.get('id', 'unknown')}"
                        )
                        return {
                            "channel_id": data.get("id"),
                            "status": "originated",
                            "call_id": data.get("id"),  # Use ARI channel ID as call ID
                            "raw_response": data,
                        }
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response from Asterisk ARI: {response_text}")
                        raise AsyncAsteriskARIError(
                            response.status, "Invalid JSON response from Asterisk ARI"
                        )
                else:
                    error_msg = (
                        f"ARI originate failed for {endpoint}:  {response.status} {response_text}"
                    )
                    logger.error(error_msg)

                    # Determine if error is retryable
                    is_retryable = response.status >= 500 or response.status == 429

                    raise AsyncAsteriskARIError(
                        response.status, error_msg, is_retryable=is_retryable
                    )

        except asyncio.TimeoutError:
            logger.error("Asterisk ARI call timeout")
            raise AsyncAsteriskARIError(500, "Asterisk ARI request timeout", "TIMEOUT")
        except aiohttp.ClientError as e:
            logger.error(f"Asterisk ARI client error: {e}")
            raise AsyncAsteriskARIError(500, f"Network error: {str(e)}", "CLIENT_ERROR")

    async def get_channel(self, channel_id: str) -> Dict[str, Any]:
        """Get information about a specific channel."""
        url = f"{self.ari_url}/channels/{channel_id}"

        try:
            async with self.session.get(url, headers=self.headers) as response:
                response_text = await response.text()

                if response.status == 200:
                    return json.loads(response_text)
                elif response.status == 404:
                    raise AsyncAsteriskARIError(404, "Channel not found", is_retryable=False)
                else:
                    raise AsyncAsteriskARIError(
                        response.status, f"Failed to get channel info: {response_text}"
                    )

        except asyncio.TimeoutError:
            raise AsyncAsteriskARIError(500, "Asterisk ARI request timeout", "TIMEOUT")
        except aiohttp.ClientError as e:
            raise AsyncAsteriskARIError(500, f"Network error: {str(e)}", "CLIENT_ERROR")

    async def hangup_channel(self, channel_id: str, reason: str = "normal") -> bool:
        """Hangup a specific channel."""
        url = f"{self.ari_url}/channels/{channel_id}"

        try:
            async with self.session.delete(
                url, headers=self.headers, params={"reason": reason}
            ) as response:
                if response.status in (204, 404):
                    # 204: Successfully hung up, 404: Channel already gone
                    return True
                else:
                    response_text = await response.text()
                    logger.error(
                        f"Failed to hangup channel {channel_id}: {response.status} {response_text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error hanging up channel {channel_id}: {e}")
            return False


# Global session management
_asterisk_session: Optional[aiohttp.ClientSession] = None


async def get_asterisk_session() -> aiohttp.ClientSession:
    """Get or create the global Asterisk ARI session."""
    global _asterisk_session

    if _asterisk_session is None or _asterisk_session.closed:
        connector = get_default_connector()
        timeout = get_default_timeout()

        _asterisk_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "Pipecat-Asterisk-ARI-Client/1.0"},
        )

    return _asterisk_session


async def cleanup_asterisk_session():
    """Clean up the global Asterisk ARI session."""
    global _asterisk_session

    if _asterisk_session and not _asterisk_session.closed:
        await _asterisk_session.close()
        _asterisk_session = None


async def create_asterisk_call(
    ari_url: str,
    username: str,
    password: str,
    endpoint: str,
    app: str,
    caller_id: str,
    variables: Optional[Dict[str, Any]] = None,
    app_args: Optional[str] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Create an outbound call using Asterisk ARI.

    Args:
        ari_url: Asterisk ARI base URL
        username: ARI username
        password: ARI password
        endpoint: Dial URI (e.g., "PJSIP/1234@trunk")
        app: Stasis application name
        caller_id: Caller ID to present
        variables: Channel variables to set
        app_args: Arguments for the Stasis app
        timeout: Call timeout in seconds

    Returns:
        Dict with call information
    """
    session = await get_asterisk_session()
    client = AsyncAsteriskARIClient(ari_url, username, password, session)

    return await client.originate_call(
        endpoint=endpoint,
        app=app,
        caller_id=caller_id,
        variables=variables,
        app_args=app_args,
        timeout=timeout,
    )
