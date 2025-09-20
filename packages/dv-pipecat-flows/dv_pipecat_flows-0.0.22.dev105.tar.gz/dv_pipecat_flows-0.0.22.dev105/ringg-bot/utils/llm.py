import json

from env_config import api_config

from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.google.llm_openai import GoogleLLMOpenAIBetaService
from pipecat.services.google.llm_vertex import GoogleVertexLLMService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.vistaar.llm import VistaarLLMService


def initialize_llm_service(llm_provider, llm_model, temperature, **kwargs):
    if llm_provider == "groq":  # Condition to use GroqLLMService
        # If qwen in model then set extra to {"reasoning_effort": "none"}. If  openai, set it to low. Else leave it as empty.
        model_lower = llm_model.lower() if isinstance(llm_model, str) else str(llm_model).lower()
        extra = {}
        if "qwen" in model_lower:
            extra = {"reasoning_effort": "none"}
        elif "openai" in model_lower:
            extra = {"reasoning_effort": "low"}
        llm = GroqLLMService(
            api_key=api_config.GROQ_API_KEY,
            model=llm_model,
            params=OpenAILLMService.InputParams(
                extra=extra,
                temperature=temperature,
            ),
            # metrics=SentryMetrics(),
        )
    elif llm_provider == "google_vertexai":
        # Use Google Vertex AI via OpenAI-compatible interface
        with open("creds.json", "r") as cred_file:
            cred_info = json.load(cred_file)
        project_id = cred_info.get("project_id")
        llm = GoogleVertexLLMService(
            credentials_path="creds.json",
            params=GoogleVertexLLMService.InputParams(
                project_id=project_id,
                location="global",
                temperature=temperature,
                extra={"extra_body": {"google": {"thinking_config": {"thinking_budget": 0}}}},
            ),
            model=f"google/{llm_model}",
        )
    elif llm_provider == "google":
        llm = GoogleLLMOpenAIBetaService(
            api_key=api_config.GEMINI_API_KEY,
            model=llm_model,
            params=OpenAILLMService.InputParams(
                temperature=temperature,
                extra={"reasoning_effort": "none"},
            ),
        )
    elif llm_provider == "azure":
        azure_llm_config = {
            "model": llm_model,
            "params": OpenAILLMService.InputParams(temperature=temperature),
            **kwargs,
        }
        if llm_model.lower().startswith("gpt-5"):
            azure_llm_config["endpoint"] = api_config.AZURE_GPT_5_ENDPOINT
            azure_llm_config["api_key"] = api_config.AZURE_GPT_5_API_KEY
            if llm_model == "gpt-5-nano":
                azure_llm_config["api_version"] = "2025-04-01-preview"
                azure_llm_config["reasoning_effort"] = "minimal"
                azure_llm_config["params"] = OpenAILLMService.InputParams(
                    temperature=1,
                    extra={"service_tier": "priority"},
                )
            else:
                # gpt-5-chat: standard chat model, no reasoning settings
                azure_llm_config["params"] = OpenAILLMService.InputParams(
                    temperature=temperature,
                    extra={"service_tier": "priority"},
                )
        else:
            azure_llm_config["endpoint"] = api_config.AZURE_CHATGPT_ENDPOINT
            azure_llm_config["api_key"] = api_config.AZURE_CHATGPT_API_KEY

        llm = AzureLLMService(**azure_llm_config)
    elif llm_provider == "vistaar":
        # Extract Vistaar-specific parameters from kwargs, assured that we are getting in kwargs
        source_lang = kwargs.pop("source_lang", "en")
        target_lang = kwargs.pop("target_lang", "en")
        session_id = kwargs.pop("session_id")
        base_url = kwargs.pop("base_url")
        pre_query_response_phrases = kwargs.pop("pre_query_response_phrases", [])

        llm = VistaarLLMService(
            base_url=base_url,
            params=VistaarLLMService.InputParams(
                source_lang=source_lang,
                target_lang=target_lang,
                session_id=session_id,
                pre_query_response_phrases=pre_query_response_phrases,
            ),
            **kwargs,
        )
    else:  # Default to OpenAILLMService if llm_provider is not groq
        llm = OpenAILLMService(
            api_key=api_config.OPENAI_API_KEY,
            model=llm_model,
            params=OpenAILLMService.InputParams(
                temperature=temperature,
            ),
            # metrics=SentryMetrics(),
        )

    return llm
