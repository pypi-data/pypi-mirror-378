#!/usr/bin/env python
# Script              : Main script for basic utilities for train and deployment.
# Component           : GenAi model deployment
# Author              : Vinay Namani
# Copyright (c)       : 2024 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------


import os
import pickle
import inspect
import requests
from datetime import datetime
from routes.models import mappings
from langchain_community.vectorstores import FAISS
from routes.utilities.prompts import answer_validation_prompt

# from langchain_core.messages import AIMessage, HumanMessage
from routes.utilities.constants import EXTRACION_API
from routes.utilities.mongo_init import get_model_provider, get_model_endpoint, get_general_settings
from langchain.schema.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
)
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

project_name = os.getenv("PROJECT_NAME", None)
filter = {
    "projectName": os.getenv("PROJECT_NAME", None),
    "userId": os.getenv("USER_ID", None),
}
TRAINING_STATUS = "FAILED"
KEY_NAMESPACE = os.getenv("KEY_NAMESPACE", None)

call = inspect.stack()[0]


def dict_based_prompt_to_langchain_prompt(
    messages: list[dict[str, str]]
) -> list[BaseMessage]:
    prompt: list[BaseMessage] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if not role:
            raise ValueError(f"Message missing `role`: {message}")
        if not content:
            raise ValueError(f"Message missing `content`: {message}")
        elif role == "user":
            prompt.append(HumanMessage(content=content))
        elif role == "system":
            prompt.append(SystemMessage(content=content))
        elif role == "assistant":
            prompt.append(AIMessage(content=content))
        else:
            raise ValueError(f"Unknown role: {role}")
    return prompt


def extract_validity(model_output: str) -> bool:
    if model_output.strip().strip("```").strip().split()[-1].lower() == "invalid":
        return False
    return True  # If something is wrong, let's not toss away the answer


def answer_validation(logger, query: str, response: str):
    ANSWER_VALIDITY_PROMPT = answer_validation_prompt()
    logger.info("###Answer validity###")
    # logger.info(ANSWER_VALIDITY_PROMPT)

    messages = [
        {
            "role": "user",
            "content": ANSWER_VALIDITY_PROMPT.format(
                user_query=query, llm_answer=response
            ),
        },
    ]
    return messages


def prepare_history(retrieved_chat_history, logger):
    history = []
    for chat_index in range(0, len(retrieved_chat_history)):
        if retrieved_chat_history[chat_index + 1 : chat_index + 2]:
            if (
                retrieved_chat_history[chat_index].role == "user"
                and retrieved_chat_history[chat_index + 1].role == "assistant"
            ): 
                if "I'm sorry, but that topic is beyond what I currently know".lower() in retrieved_chat_history[chat_index + 1].content.lower():
                    continue
                history.extend(
                    [
                        HumanMessage(
                            content=retrieved_chat_history[chat_index].content
                        ),
                        AIMessage(
                            content=retrieved_chat_history[chat_index + 1].content
                        ),
                    ]
                )
            elif retrieved_chat_history[chat_index].role == "assistant":
                continue
            else:
                history.extend(
                    [
                        HumanMessage(
                            content=retrieved_chat_history[chat_index].content
                        ),
                        AIMessage(content=""),
                    ]
                )
        else:
            if not retrieved_chat_history[chat_index].role == "assistant":
                history.extend(
                    [
                        HumanMessage(
                            content=retrieved_chat_history[chat_index].content
                        ),
                        AIMessage(content=""),
                    ]
                )
    logger.info("Formatted chat history")
    return history


# def embedding_exists(embedding_service_type, mongo_logger, logger):
#     if (
#         embedding_service_type
#         not in mappings.azure_embedding_models
#         + mappings.openai_embedding_models
#         + mappings.katonic_embedding_models
#         + list(mappings.replicate_embedding_models.keys())
#     ):
#         if mongo_logger:
#             mongo_logger("Embedding service type not found.", call.filename.split("/")[-1], str(call.lineno), "INFO")
#         else:
#             logger.error("Embedding service type not found.")
#         exit(1)
#     return


# def get_embedding_model(embedding_service_type, mongo_logger, logger):
#     if embedding_service_type in mappings.azure_embedding_models:
#         from embeddings import azure_embeddings

#         if mongo_logger:
#             mongo_logger("Initializing embeddings with Azure Service.", call.filename.split("/")[-1], str(call.lineno), "INFO")
#         else:
#             logger.info("Initializing embeddings with Azure Service.")
#         provider = "Azure OpenAI"
#         embeddings = azure_embeddings.azure_embeds()
#     if embedding_service_type in mappings.openai_embedding_models:
#         # mongo_logger(f"Current File Path: {os.path.abspath(__file__)}", call.filename.split("/")[-1], str(call.lineno), "INFO")
#         from embeddings import openai_embeddings

#         if mongo_logger:
#             mongo_logger("Initializing embeddings with Openai Service.", call.filename.split("/")[-1], str(call.lineno), "INFO")
#         else:
#             logger.info("Initializing embeddings with Openai Service.")
#         provider = "OpenAI"
#         embeddings = openai_embeddings.openai_embeds(embedding_service_type)
#     if embedding_service_type in mappings.katonic_embedding_models:
#         from embeddings import katonic_embeddings

#         if mongo_logger:
#             mongo_logger("Initializing embeddings with base Service.", call.filename.split("/")[-1], str(call.lineno), "INFO")
#             embeddings = katonic_embeddings.katonic_embeds_training(mongo_logger)
#         else:
#             logger.info("Initializing embeddings with base Service.")
#             provider = "katonic"
#             embeddings = katonic_embeddings.katonic_embeds_deploy(logger)
#     if embedding_service_type in mappings.replicate_embedding_models:
#         from embeddings import replicate_embeddings

#         if mongo_logger:
#             mongo_logger("Initializing embeddings with base Service.", call.filename.split("/")[-1], str(call.lineno), "INFO")
#         else:
#             logger.info("Initializing embeddings with base Service.")
#         service_model = mappings.replicate_embedding_models[embedding_service_type]
#         provider = "Replicate"
#         embeddings = replicate_embeddings.replicate_embeds_training(model=service_model)
#     return embeddings, provider


def get_llm_provider(service_type, logger):
    provider = None
    try:
        logger.info(f"Checking for provider and endpoint for {service_type}")
        #logger.info(f"Service type: {service_type}")
        if service_type == "katonicLLM":
            provider = "katonic"
            #logger.info(f"provider:{provider}")
            general_settings = get_general_settings()
            model_name = general_settings["modelConfig"]["ace"]["primaryModel"][
                "modelName"
            ]
        else:
            provider = get_model_provider(service_type)
            #logger.info(f"Provider: {provider}")
            if provider not in ["TGI LLM", "VLLM LLM", "LLAMA", "Custom LLM"]:
                model_name = get_model_endpoint(service_type)
            elif provider in ["LLAMA", "Custom LLM"]:
                provider = "katonic"
                model_name = service_type
            else:
                model_name = service_type
        #logger.info(f"provider: {provider}, model_name: {model_name}")
        return provider, model_name
    except Exception as e:
        if provider == None:
            err = f"The choosen model {service_type} is not available in the backend LLM engine."
            logger.info(err)
            return str(err)
        else:
            logger.info(str(e))
            return str(e)


def create_16_bytes_from_string(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:16]


def create_32_bytes_from_string(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:32]


input_string = "Katonic@U7OS4o0mren8OHsIibbKOvekpJHx3T2020"
key = create_32_bytes_from_string(input_string)
iv = create_16_bytes_from_string(input_string)


def decrypt_seed(text):
    encrypted_data = bytes.fromhex(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode("utf-8")


def increment_rate_limits_data(
    user_id: str, application_id: str, cost_used: float, requests_used: int, logger
):
    try:
        payload = {
            "user_id": user_id,
            "application_id": application_id,
            "cost_used": cost_used,
            "requests_used": requests_used,
        }

        requests.post(EXTRACION_API + "increment_limits", json=payload)
        logger.info(f"Rate limits updated successfully..")
        return None
    except Exception as e:
        logger.info(f"Limit increment failed due to {str(e)}")
