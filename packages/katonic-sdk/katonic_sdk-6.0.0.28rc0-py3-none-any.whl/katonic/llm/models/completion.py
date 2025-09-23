#!/usr/bin/env python
# Script            : Main script to categorize all the foundational models.
# Component         : GenAi model deployment
# Author            : Vinay Namani
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

from .openai_chat_llm import create_openai_model
from .azure_llm import create_azure_model
from .ai21_llm import create_ai21_model
from .bedrock_llm import create_bedrock_model
from .google_llm import create_google_model
from .openrouter_llm import create_openrouter_model
from .cohere_llm import create_cohere_model
from .lighton_llm import create_lighton_model
from .anyscale_llm import create_anyscale_model
from .replicate_llm import create_replicate_model
from .anthropic_llm import create_anthropic_model
from .alephalpha_llm import create_alephalpha_model
from .togetherai_llm import create_togetherai_model
from .groq_llm import create_groq_model
from .huggingface_llm import create_huggingface_model
from .katonic_llm import create_katonic_model
from .sambanova_llm import create_sambanova_model
from .nvidia_llm import create_nvidia_model
from .perplexity_llm import create_perplexity_model
from .vllm_llm import create_vllm_model
from .tgi_llm import create_tgi_model


def initialize_model_factory(service_type, provider, model_name, logger, module=None):
    """
    Initialize model factory with comprehensive error handling
    
    Args:
        service_type: Type of service (e.g., "chat", "completion")
        provider: Provider name (e.g., "OpenAI", "Anthropic")
        model_name: Name of the model
        logger: Logger instance (deprecated, kept for compatibility)
        module: Optional module parameter for katonic models
        
    Returns:
        Model instance
        
    Raises:
        ValueError: If required parameters are invalid
        RuntimeError: If model creation fails
    """
    # Input validation
    if not service_type or not isinstance(service_type, str):
        raise ValueError(f"Invalid service_type: {service_type}. Must be a non-empty string.")
        
    if not provider or not isinstance(provider, str):
        raise ValueError(f"Invalid provider: {provider}. Must be a non-empty string.")
        
    if not model_name or not isinstance(model_name, str):
        raise ValueError(f"Invalid model_name: {model_name}. Must be a non-empty string.")
    
    try:
        if provider == "OpenAI":
            return create_openai_model(service_type, model_name)
        elif provider == "OpenRouter":
            return create_openrouter_model(service_type, model_name)
        elif provider == "Anyscale":
            return create_anyscale_model(service_type, model_name)
        elif provider == "Azure OpenAI":
            return create_azure_model(service_type)
        elif provider == "Groq":
            return create_groq_model(service_type, model_name)
        elif provider == "Huggingface":
            return create_huggingface_model(service_type, model_name)
        elif provider == "AI21":
            return create_ai21_model(service_type, model_name)
        elif provider == "Replicate":
            return create_replicate_model(service_type, model_name)
        elif provider == "Cohere":
            return create_cohere_model(service_type, model_name)
        elif provider == "Aleph Alpha":
            return create_alephalpha_model(service_type, model_name)
        elif provider == "Anthropic":
            return create_anthropic_model(service_type, model_name)
        elif provider == "Together AI":
            return create_togetherai_model(service_type, model_name)
        elif provider == "AWS Bedrock":
            return create_bedrock_model(service_type, model_name)
        elif provider == "lighton":
            return create_lighton_model(service_type, model_name)
        elif provider == "Google":
            return create_google_model(service_type, model_name)
        elif provider == "Katonic LLM":
            return create_katonic_model(service_type, model_name)
        elif provider == "Sambanova":
            return create_sambanova_model(service_type, model_name)
        elif provider == "Nvidia":
            return create_nvidia_model(service_type, model_name)
        elif provider == "Perplexity":
            return create_perplexity_model(service_type, model_name)
        elif provider == "VLLM LLM":
            return create_vllm_model(service_type)
        elif provider == "TGI LLM":
            return create_tgi_model(service_type)
        elif provider == "katonic":
            return create_katonic_model(service_type, model_name, module)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: OpenAI, OpenRouter, Anyscale, Azure OpenAI, Groq, Huggingface, AI21, Replicate, Cohere, Aleph Alpha, Anthropic, Together AI, AWS Bedrock, lighton, Google, Katonic LLM, Sambanova, Nvidia, Perplexity, VLLM LLM, TGI LLM, katonic")
            
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Failed to create model for provider '{provider}' with model '{model_name}': {str(e)}")