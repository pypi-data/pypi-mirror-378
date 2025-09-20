import os
import sys
from typing import Optional

from dotenv import load_dotenv
from loguru import logger  # Import logger
from pydantic_settings import BaseSettings


# Function to read secrets from mounted files
def read_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    secret_path = f"/etc/secrets/{secret_name}"
    try:
        with open(secret_path, "r") as file:
            value = file.read().strip()
            # Return None or default if the file is unexpectedly empty
            return value if value else default
    except FileNotFoundError:
        logger.debug(f"Secret file not found at {secret_path}, using default or None.")
        return default
    except IOError as e:
        logger.error(f"Error reading secret file {secret_path}: {e}")
        return default


# Determine the primary .env file path (local dev vs testing)
if "pytest" in sys.modules:
    _ENV_FILE = "env.TEST"
else:
    _ENV_FILE = ".env"

# Check if running in Kubernetes by looking for the secrets mount path
# and read secrets into environment variables if present.
SECRETS_DIR = "/etc/secrets"
if os.path.isdir(SECRETS_DIR):
    logger.info(f"Secrets directory {SECRETS_DIR} found. Reading secrets into environment.")
    # Define the list of secrets expected to be mounted as files
    secrets_to_read = [
        "OPENAI_API_KEY",
        "EXOTEL_SID",
        "EXOTEL_API_KEY",
        "EXOTEL_API_TOKEN",
        "EXOTEL_REGION",
        "APP_ID",
        "DEEPGRAM_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
        "AZURE_SPEECH_API_KEY",
        "AZURE_SPEECH_REGION",
        "AZURE_CHATGPT_API_KEY",
        "AZURE_CHATGPT_ENDPOINT",
        "AZURE_GPT_5_API_KEY",
        "AZURE_GPT_5_ENDPOINT",
        "NGROK_URL",
        "PLIVO_AUTH_ID",
        "PLIVO_AUTH_TOKEN",
        "CARTESIA_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_REGION",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME",
        "ENVIRONMENT",
        "REDIS_URL",
        "GLADIA_API_KEY",
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
        "WEAVIATE_CLUSTER_URI",
        "WEAVIATE_CLUSTER_API_KEY",
        "WEAVIATE_COLLECTION_NAME",
        "CALLING_BACKEND_URL",
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "CALLING_BACKEND_API_KEY",
        "X_API_KEY",
        "WEAVIATE_HOST",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "CONVOX_API_URL",
        "CONVOX_API_KEY",
        "CONVOX_API_SECRET",
        "SPEECHMATICS_API_KEY",
        # "ANALYZER_POOL_SIZE",
        # "ENABLE_SMART_TURN",
        # "LOCAL_SMART_TURN_MODEL_PATH",
        "FAL_API_KEY",
        "DAILY_API_KEY",
        "ASTERISK_ARI_URL",
        "ASTERISK_ARI_USER",
        "ASTERISK_ARI_PASS",
        "ASTERISK_ARI_APP",
        "ELEVENLABS_API_KEY_V2",
        "VISTAAR_API_BASE_URL",
        "ADMIN_API_KEY",
        "SARVAM_API_KEY",
    ]
    loaded_secrets_count = 0
    for secret_name in secrets_to_read:
        secret_value = read_secret(secret_name)
        if secret_value:
            os.environ[secret_name] = secret_value
            loaded_secrets_count += 1
            logger.debug(f"Loaded secret '{secret_name}' into environment.")
        else:
            logger.warning(f"Secret '{secret_name}' not found in {SECRETS_DIR} or file is empty.")
    logger.info(f"Finished loading {loaded_secrets_count} secrets from {SECRETS_DIR}.")
else:
    logger.info(f"Secrets directory {SECRETS_DIR} not found. Assuming local development.")
    logger.info(f"Loading environment variables from local file: {_ENV_FILE}")
    load_dotenv(dotenv_path=_ENV_FILE, override=True)  # Load .env file if secrets dir doesn't exist


# Pydantic settings will now load from environment variables
# (set either by mounted secrets or local .env file)
class Config(BaseSettings):
    OPENAI_API_KEY: str = "openai_api_key"
    EXOTEL_SID: str = "exotel_sid"
    EXOTEL_API_KEY: str = "exotel_api_key"
    EXOTEL_API_TOKEN: str = "exotel_api_token"
    EXOTEL_REGION: str = "exotel_region"
    APP_ID: str = "app_id"
    DEEPGRAM_API_KEY: str = "deepgram_api_key"
    ELEVENLABS_API_KEY: str = "elevenlabs_api_key"
    ELEVENLABS_VOICE_ID: str = "elevenlabs_voice_id"
    AZURE_SPEECH_API_KEY: str = "azure_speech_api_key"
    AZURE_SPEECH_REGION: str = "azure_speech_region"
    AZURE_CHATGPT_API_KEY: str = "azure_chatgpt_api_key"
    AZURE_CHATGPT_ENDPOINT: str = "azure_chatgpt_endpoint"
    AZURE_GPT_5_API_KEY: str = "azure_gpt_5_api_key"
    AZURE_GPT_5_ENDPOINT: str = "azure_gpt_5_endpoint"
    NGROK_URL: str = "ngrok_url"
    PLIVO_AUTH_ID: str = "plivo_auth_id"
    PLIVO_AUTH_TOKEN: str = "plivo_auth_token"

    # HTTP Client Configuration for API calls
    HTTP_CLIENT_TIMEOUT_TOTAL: float = 60.0  # Total timeout for HTTP requests (seconds)
    HTTP_CLIENT_TIMEOUT_CONNECT: float = 20.0  # Connection timeout (seconds)
    HTTP_CLIENT_TIMEOUT_READ: float = 30.0  # Socket read timeout (seconds)
    HTTP_CLIENT_POOL_SIZE: int = 50  # Total connection pool size
    HTTP_CLIENT_POOL_SIZE_PER_HOST: int = 10  # Max connections per host
    HTTP_CLIENT_DNS_CACHE_TTL: int = 300  # DNS cache TTL (seconds)
    HTTP_CLIENT_KEEPALIVE_TIMEOUT: int = 30  # Keep-alive timeout (seconds)

    # Rate Limiting Configuration
    PLIVO_RATE_LIMIT_CPS: float = 1.8  # Plivo calls per second (slightly under 2 CPS limit)
    PLIVO_RATE_LIMIT_BURST: int = 3  # Burst capacity for rate limiter
    PLIVO_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 10  # Failures before opening circuit
    PLIVO_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: float = 30.0  # Recovery timeout (seconds)

    # Twilio Rate Limiting Configuration
    TWILIO_RATE_LIMIT_CPS: float = 1.0  # Twilio calls per second (conservative for trial accounts)
    TWILIO_RATE_LIMIT_BURST: int = 2  # Burst capacity for rate limiter
    TWILIO_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 10  # Failures before opening circuit
    TWILIO_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: float = 30.0  # Recovery timeout (seconds)

    TELEPHONY_RETRY_MAX_ATTEMPTS: int = (
        1  # Maximum retry attempts (reduced to prevent duplicate calls)
    )
    TELEPHONY_RETRY_INITIAL_DELAY: float = 1.0  # Initial retry delay (seconds)
    TELEPHONY_RETRY_MAX_DELAY: float = 60.0  # Maximum retry delay (seconds)
    TELEPHONY_RETRY_EXPONENTIAL_BASE: float = 2.0  # Exponential backoff base

    # Telephony-specific timeout settings
    PLIVO_API_TIMEOUT: float = 120.0  # Plivo API timeout (longer for call initiation)
    TWILIO_API_TIMEOUT: float = 45.0

    CARTESIA_API_KEY: str = "cartesia_api_key"
    AWS_ACCESS_KEY_ID: str = "aws_access_key_id"
    AWS_REGION: str = "us-east-1"  # Keep default if desired
    AWS_SECRET_ACCESS_KEY: str = "aws_secret_access_key"
    S3_BUCKET_NAME: str = "s3_bucket_name"
    ENVIRONMENT: str = "development"  # Default environment
    REDIS_URL: str = "redis_url"
    GLADIA_API_KEY: str = "gladia_api_key"
    GROQ_API_KEY: str = "groq_api_key"
    GEMINI_API_KEY: str = "gemini_api_key"
    WEAVIATE_CLUSTER_URI: str = "weaviate_cluster_uri"
    WEAVIATE_CLUSTER_API_KEY: str = "weaviate_cluster_api_key"
    WEAVIATE_COLLECTION_NAME: str = "weaviate_collection_name"
    CALLING_BACKEND_URL: str = "calling_backend_url"
    LIVEKIT_URL: str = "livekit_url"
    LIVEKIT_API_KEY: str = "livekit_api_key"
    LIVEKIT_API_SECRET: str = "livekit_api_secret"
    CALLING_BACKEND_API_KEY: str = "calling_backend_api_key"
    X_API_KEY: str = "x_api_key"
    WEAVIATE_HOST: str = "weaviate_host"
    TWILIO_ACCOUNT_SID: str = "twilio_account_sid"
    TWILIO_AUTH_TOKEN: str = "twilio_auth_token"
    CONVOX_API_URL: str = "convox_api_url"
    CONVOX_API_KEY: str = "convox_api_key"
    SPEECHMATICS_API_KEY: str = "speechmatics_api_key"
    HAMSA_API_KEY: str = "hamsa_api_key"  #
    FAL_API_KEY: str = "fal_api_key"  # FAL API key for Smart Turn service
    DAILY_API_KEY: str = "daily_api_key"
    ASTERISK_ARI_URL: str = "http://35.211.140.39:8088/ari"  # Asterisk ARI URL (external IP)
    ASTERISK_ARI_USER: str = "pipecat"  # Asterisk ARI username
    ASTERISK_ARI_PASS: str = "asdf!@#$"  # Asterisk ARI password
    ASTERISK_ARI_APP: str = "pipecat"  # Stasis application name (must match Asterisk dialplan)
    ELEVENLABS_API_KEY_V2: str = "elevenlabs_api_key_v2"
    VISTAAR_API_BASE_URL: str = "https://vistaar.kenpath.ai/api"  # Vistaar API base
    ADMIN_API_KEY: str = "admin_api_Key"
    SARVAM_API_KEY: str = "sarvam_api_key"

    # # Analyzer Pool Configuration for Turn Detection
    # ANALYZER_POOL_SIZE: int = 5  # Number of analyzer pairs to pre-warm
    # ENABLE_SMART_TURN: bool = False  # Enable Smart Turn v2 semantic turn detection
    # LOCAL_SMART_TURN_MODEL_PATH: str = ""  # Path to local Smart Turn model (optional)

    class Config:
        # Keep env_file for local development fallback, although environment vars take precedence.
        env_file: str = _ENV_FILE
        extra = "ignore"


api_config = Config()


# Log loaded config values (excluding sensitive keys)
def log_loaded_config():
    sensitive_keys = {"KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH"}
    config_dict = api_config.model_dump()
    for key, value in config_dict.items():
        is_sensitive = any(sk in key.upper() for sk in sensitive_keys)
        display_value = "****" if is_sensitive and value else value
        logger.debug(f"Config - {key}: {display_value}")


log_loaded_config()
