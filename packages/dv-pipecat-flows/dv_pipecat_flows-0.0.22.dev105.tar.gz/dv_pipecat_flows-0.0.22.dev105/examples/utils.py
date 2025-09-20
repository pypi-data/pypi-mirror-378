#
# Copyright (c) 2024-2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Utility functions for Pipecat Flows examples.

This module provides helper functions to reduce boilerplate and keep examples
focused on the core flow concepts.
"""

import os
from typing import Any


def create_llm(provider: str = None, model: str = None) -> Any:
    """Create an LLM service instance based on environment configuration.

    Args:
        provider: LLM provider name. If None, uses LLM_PROVIDER env var (defaults to 'openai')
        model: Model name. If None, uses provider's default model

    Returns:
        Configured LLM service instance

    Raises:
        ValueError: If provider is unsupported or required API keys are missing

    Supported Providers:
        - openai: Requires OPENAI_API_KEY
        - anthropic: Requires ANTHROPIC_API_KEY
        - google: Requires GOOGLE_API_KEY
        - aws: Uses AWS default credential chain (SSO, environment variables, or IAM roles)
              Optionally set AWS_REGION (defaults to us-west-2)

    Usage:
        # Use default provider (from LLM_PROVIDER env var, defaults to OpenAI)
        llm = create_llm()

        # Use specific provider
        llm = create_llm("anthropic")

        # Use specific provider and model
        llm = create_llm("openai", "gpt-4o-mini")

        # Use AWS Bedrock (requires AWS credentials via SSO, env vars, or IAM)
        llm = create_llm("aws")
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
    else:
        provider = provider.lower()

    # Provider configurations
    configs = {
        "openai": {
            "service": "pipecat.services.openai.llm.OpenAILLMService",
            "api_key_env": "OPENAI_API_KEY",
            "default_model": "gpt-4.1",
        },
        "anthropic": {
            "service": "pipecat.services.anthropic.llm.AnthropicLLMService",
            "api_key_env": "ANTHROPIC_API_KEY",
            "default_model": "claude-sonnet-4-20250514",
        },
        "google": {
            "service": "pipecat.services.google.llm.GoogleLLMService",
            "api_key_env": "GOOGLE_API_KEY",
            "default_model": "gemini-2.0-flash",
        },
        "aws": {
            "service": "pipecat.services.aws.llm.AWSBedrockLLMService",
            "api_key_env": None,  # AWS uses default credential chain
            "default_model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "region": "us-west-2",
        },
    }

    config = configs.get(provider)
    if not config:
        available = ", ".join(configs.keys())
        raise ValueError(f"Unsupported LLM provider: {provider}. Available: {available}")

    # Dynamic import of the LLM service
    module_path, class_name = config["service"].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    service_class = getattr(module, class_name)

    # Get API key (skip for AWS which uses default credential chain)
    if provider == "aws" or config["api_key_env"] is None:
        api_key = None  # AWS uses default credential chain
    else:
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            raise ValueError(f"Missing API key: {config['api_key_env']} for provider: {provider}")

    # Use provided model or default
    selected_model = model or config["default_model"]

    # Build kwargs
    kwargs = {"api_key": api_key, "model": selected_model}

    # Add AWS-specific parameters
    if provider == "aws":
        kwargs["aws_region"] = os.getenv("AWS_REGION", config["region"])
        kwargs["params"] = service_class.InputParams(temperature=0.8)
        # Remove the generic api_key since AWS uses default credential chain
        del kwargs["api_key"]

    return service_class(**kwargs)
