import os
import json
import pandas
import requests
import tiktoken
import traceback
import pickle
from pathlib import Path
from importlib import resources
from distutils.util import strtobool
from fastapi import HTTPException
from routes.models import mappings
# Logger removed
from routes.utilities.mongo_init import get_model_provider
from routes.utilities.utils import get_llm_provider, increment_rate_limits_data
from routes.utilities.mongo_init import (
    get_local_mongo_cost_collection,
    get_general_settings,
)
from routes.utilities.constants import SERVER_DOMAIN, PERSONALIZED_PROMPTS_API
from tokenizers import Tokenizer

# Logger removed


def fetch_model_config(general_settings, module_key):
    return {
        "api_endpoint": general_settings.get(module_key, {})
        .get("modelMeta", {})
        .get("metadata", {})
        .get("apiRoute"),
        "model_name": general_settings.get(module_key, {})
        .get("modelMeta", {})
        .get("metadata", {})
        .get("projectName"),
        "framework": general_settings.get(module_key, {})
        .get("modelMeta", {})
        .get("metadata", {})
        .get("chatFramework"),
    }


def populate_model_cost(
    input_text,
    output_text,
    model_name,
    user_name,
    end_time,
    start_time,
    status,
    project_name,
    project_type,
    product_type,
    messageid=None,
    module=None,
):  
    encoding = None
    def safe_strtobool(value:str)->bool:
            try:
                return bool(strtobool(value.strip()))
            except (ValueError,AttributeError):
                return False
    def get_project_name(service_type):
        return pricing_df[pricing_df["modelName"]==service_type]["metadata"].values[0].get("projectName")
    def get_api_route(service_type):
        return pricing_df[pricing_df["modelName"]==service_type]["metadata"].values[0].get("apiRoute")
    def get_chat_framework(service_type):
        return pricing_df[pricing_df["modelName"]==service_type]["metadata"].values[0].get("chatFramework")
                  
     #if not safe_strtobool(os.getenv("OFFLINE_ENVIRONMENT","False")):
            #self.encoding = tiktoken.get_encoding("cl100k_base")
    
    if get_model_provider(model_name) == "Cohere":
        #self.encoding = Tokenizer.from_pretrained("Cohere/command-nightly")
        with resources.files("routes.models").joinpath("cohere_command_nightly.pkl").open("rb") as f:
            encoding = pickle.load(f)
    elif "llama-2" in model_name.lower():
        #self.encoding = Tokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
        with resources.files("routes.models").joinpath("hf_internal_testing_llama_tokenizer.pkl").open("rb") as f:
            encoding  = pickle.load(f)
    elif "llama-3" in model_name.lower():
        #self.encoding = Tokenizer.from_pretrained("Xenova/llama-3-tokenizer")
        with resources.files("routes.models").joinpath("Xenova_llama_3_tokenizer.pkl").open("rb") as f:
            encoding = pickle.load(f)
    elif get_model_provider(model_name) == "Anthropic":
        with resources.open_text("routes.models", "anthropic_tokenizer.json") as f:
            json_data = json.load(f)
        json_str = json.dumps(json_data)
        encoding = Tokenizer.from_str(json_str)
    elif  "4o" in model_name.lower():
        with resources.files("routes.models").joinpath("o200k_base.pkl").open("rb") as f:
            encoding = pickle.load(f)    
    else:
        with resources.files("routes.models").joinpath("cl100k_base.pkl").open("rb") as f:
            encoding = pickle.load(f)    

    provider, model = get_llm_provider(model_name, logger)
    # Logger removed

    PricesMongoCollection = get_local_mongo_cost_collection()
    pricing_df = pandas.DataFrame()
    if PricesMongoCollection is not None:
        pricing_df = pandas.DataFrame(PricesMongoCollection.find({}))
    else:
        error_message = "No pricing information found in the database"
        # Logger removed 
        raise HTTPException(status_code=500, detail=error_message)

    general_settings = get_general_settings()
    if not general_settings:
        error_message = f"Failed to load general setting, Please check the configuration."
        # Logger removed
        raise HTTPException(status_code=500, detail=error_message)

    peronalization_settings = requests.get(PERSONALIZED_PROMPTS_API).json()
    if not peronalization_settings:
        error_message = f"Failed to load personalised prompt configuration, Please check the configuration."
        # Logger removed
        raise HTTPException(status_code=500, detail=error_message)
    embedding_settings = general_settings.get("modelConfig",{}).get("ace",{}).get("embeddingModel",{})
    if not embedding_settings:
        error_message = f"Embedding model settings are missing in the configuration."
        # Logger removed
        raise HTTPException(status_code=500, detail=error_message)
    embedding_modelName = embedding_settings.get("modelName",None)
    try:
        if provider != "katonic":
            model_pricing_dict = pricing_df[pricing_df["modelName"] == model_name][
                "metadata"
            ].values[0]
        else:
            if module is None:
                api_endpoint = general_settings["modelConfig"]["ace"]["primaryModel"][
                    "metadata"
                ]["apiRoute"]
                project_name = general_settings["modelConfig"]["ace"]["primaryModel"][
                    "metadata"
                ].get("projectName")
            else:
                model_config = fetch_model_config(peronalization_settings, module)
                api_endpoint = model_config["api_endpoint"]
                framework = model_config["framework"]
                project_name = get_project_name(model_name)
                if project_name:
                    project_name = project_name
                    api_endpoint = get_api_route(model_name)
            provider_pricing_df = pricing_df[pricing_df["value"] == "katonicLLM"]
            model_pricing_dict = provider_pricing_df[
                provider_pricing_df["metadata"].apply(
                    lambda x: isinstance(x, dict) and x.get("apiRoute") == api_endpoint
                )
            ]["metadata"].values[0]
        IS_COST_AVAILABLE = "inputCostPerToken" in model_pricing_dict
        # Logger removed
    except Exception:
        # Log the traceback without exposing sensitive information
        error_traceback = traceback.format_exc()
        message = "An error occurred. Traceback:\n" + error_traceback
        IS_COST_AVAILABLE = False
        error_message = f"Cost information is not available in metadata.{message}"
        # Logger removed
        raise HTTPException(status_code=500,detail=error_message)
    if any(
        model_name in key for key in (mappings.openai_models, mappings.azure_models)
    ):
        input_token_length = len(encoding.encode(input_text)) if encoding else 0
    else:
        input_token_length = len(encoding.encode(input_text)) if encoding else 0
    input_cost = (
        input_token_length * float(model_pricing_dict["inputCostPerToken"])
        if IS_COST_AVAILABLE
        else 0
    )

    if model_name in mappings.openai_models:
        output_token_length = len(encoding.encode(output_text)) if encoding else 0
    else:
        output_token_length = len(encoding.encode(output_text)) if encoding else 0
    output_cost = (
        output_token_length * float(model_pricing_dict["outputCostPerToken"])
        if IS_COST_AVAILABLE
        else 0
    )

    try:
        target_url = f"{SERVER_DOMAIN}/logs/api/message/add"
        payload = {
            "userName": user_name,
            "projectName": project_name,
            "projectType": project_type,
            "productType": product_type,
            "modelName": model_name if model_name is not None else project_name,
            "embeddingModelName": embedding_modelName,
            "inputTokenCost": input_cost,
            "inputTokens": input_token_length,
            "outputTokenCost": output_cost,
            "outputTokens": output_token_length,
            "totalCost": round(input_cost + output_cost, 4),
            "totalTokens": input_token_length + output_token_length,
            "request": input_text,
            "response": output_text,
            "context": input_text,
            "latency": round((end_time - start_time).total_seconds(), 4),
            "feedback": None,
            "status": status,
            "answered": True,
            "tokenName": "Platform-Token",
            "conversationId": messageid,
        }
        # Logger removed

        increment_rate_limits_data(
            user_id=os.getenv("USER_EMAIL", user_name),
            application_id="Ace",
            cost_used=round(float(input_cost + output_cost),4),
            requests_used=1 if project_type == "Search Results" else 0,
            logger=None,
        )

        response = requests.post(url=target_url, json=payload, verify=False)
        if response.json()["status"] == 200:
            pass  # Success - no action needed
        else:
            # Logger removed
            pass  # Error - no action needed
    except Exception as e:
        error_message = f"failed while posting cost data: {str(e)}"
        # Logger removed
        raise HTTPException(status_code=500,detail=error_message)