import json
import os
from typing import Optional

from fastapi import HTTPException
from loguru import logger

from utils.transcript import get_transcript_text, get_transcript_url
from utils.tts import get_tts_file_from_redis, put_file_on_redis
from voice_services.common import get_redis_client


class MiscService:
    def __init__(self):
        self.redis_client = get_redis_client()

    async def get_transcript(self, call_id: str):
        """Get call transcript by call ID."""
        transcript = await get_transcript_text(call_id)
        if transcript:
            return {"status": "success", "transcript": transcript}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")

    async def get_transcript_url(self, call_id: str):
        """Get call transcript URL by call ID."""
        transcript_url = get_transcript_url(call_id)
        if transcript_url:
            return {"status": "success", "transcript": transcript_url}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")

    async def cache_test_mp3(self):
        """Cache test_cache.mp3 in Redis using put_file_on_redis."""
        if not self.redis_client:
            raise HTTPException(status_code=503, detail="Redis client not available")
        
        mp3_path = os.path.join(os.path.dirname(__file__), "..", "utils", "test_cache_new.mp3")
        text = "Hello! bro, wassup."
        
        try:
            key = await put_file_on_redis(self.redis_client, text, mp3_path)
            return {"redis_key": key}
        except Exception as e:
            logger.error(f"Failed to cache mp3 file: {e}")
            raise HTTPException(status_code=500, detail="Failed to cache MP3 file.")

    async def get_tts_file(self, text: str):
        """API endpoint to retrieve a cached TTS file from Redis and save it locally."""
        if not self.redis_client:
            raise HTTPException(status_code=503, detail="Redis client not available")
        
        try:
            file_path = await get_tts_file_from_redis(self.redis_client, text)
            if file_path:
                return {"status": "success", "file_path": file_path}
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"TTS data for the provided text not found in cache."
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving TTS file from Redis: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve TTS file from Redis.")