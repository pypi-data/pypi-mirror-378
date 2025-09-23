import json
import pickle
import requests
import pandas as pd
from importlib import resources
from tokenizers import Tokenizer
from bson import ObjectId
from katonic.llm.utilities.utils import (
    get_llm_provider,
    get_model_provider,
    get_local_mongo_cost_collection,
)


def calculate_input_output_token_cost(
    input_text: str,
    output_text: str,
    encoding,
    model_pricing_dict: dict,
    is_cost_available: bool,
):
    """Calculate input/output token counts and costs."""
    def safe_encode(text: str):
        try:
            return encoding.encode(text, disallowed_special=())
        except Exception:
            return encoding.encode(text) if encoding else []

    input_tokens = safe_encode(input_text)
    output_tokens = safe_encode(output_text)

    input_token_length = len(input_tokens) if encoding else 0
    output_token_length = len(output_tokens) if encoding else 0

    input_cost = (
        input_token_length * float(model_pricing_dict.get("inputCostPerToken", 0))
        if is_cost_available
        else 0
    )
    output_cost = (
        output_token_length * float(model_pricing_dict.get("outputCostPerToken", 0))
        if is_cost_available
        else 0
    )

    return input_token_length, input_cost, output_token_length, output_cost


def load_encoding(model_name: str):
    """Load appropriate tokenizer/encoder based on the model name."""
    provider = get_model_provider(model_name)

    try:
        if provider == "Cohere":
            with resources.files("katonic.llm.encoders").joinpath("cohere_command_nightly.pkl").open("rb") as f:
                return pickle.load(f)
        elif "llama-2" in model_name.lower():
            with resources.files("katonic.llm.encoders").joinpath("hf_internal_testing_llama_tokenizer.pkl").open("rb") as f:
                return pickle.load(f)
        elif "llama-3" in model_name.lower():
            with resources.files("katonic.llm.encoders").joinpath("Xenova_llama_3_tokenizer.pkl").open("rb") as f:
                return pickle.load(f)
        elif provider == "Anthropic":
            with resources.open_text("katonic.llm.encoders", "anthropic_tokenizer.json") as f:
                return Tokenizer.from_str(json.dumps(json.load(f)))
        elif "4o" in model_name.lower():
            with resources.files("katonic.llm.encoders").joinpath("o200k_base.pkl").open("rb") as f:
                return pickle.load(f)
        else:
            with resources.files("katonic.llm.encoders").joinpath("cl100k_base.pkl").open("rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load encoding for {model_name}: {e}")
        return None


def log_request_to_platform(
    input_query: str,
    response: str,
    user_name: str,
    model_name: str,
    product_type: str,
    product_name: str,
    project_name: str,
    latency: float,
    status: str,
    embedding_model_name: str = None,
):
    """Log request/response metadata and cost details to platform, return conversationId if successful."""
    conversation_id = str(ObjectId())
    encoding = load_encoding(model_name)

    provider, _ = get_llm_provider(model_name)
    prices_collection = get_local_mongo_cost_collection()
    pricing_df = pd.DataFrame(prices_collection.find({}))

    model_pricing_dict = {}
    if provider != "katonic" and not pricing_df.empty:
        row = pricing_df.loc[pricing_df["modelName"] == model_name, "metadata"]
        if not row.empty:
            model_pricing_dict = row.values[0]

    is_cost_available = "inputCostPerToken" in model_pricing_dict
    (
        input_token_length,
        input_cost,
        output_token_length,
        output_cost,
    ) = calculate_input_output_token_cost(
        input_query, response, encoding, model_pricing_dict, is_cost_available
    )

    payload = {
        "userName": user_name,
        "projectName": product_name,
        "projectType": project_name,
        "productType": product_type,
        "modelName": model_name or project_name,
        "embeddingModelName": embedding_model_name,
        "inputTokens": input_token_length,
        "inputTokenCost": input_cost,
        "outputTokens": output_token_length,
        "outputTokenCost": output_cost,
        "totalTokens": input_token_length + output_token_length,
        "totalCost": round(input_cost + output_cost, 4),
        "request": input_query,
        "response": response,
        "context": input_query,
        "latency": latency,
        "feedback": None,
        "status": status,
        "answered": None,
        "conversationId": conversation_id,
        "tokenName": "Platform-Token",
    }

    try:
        resp = requests.post("http://log-ingestor:3000/logs/api/message/add", json=payload, timeout=10)
        resp_data = resp.json()

        if resp_data.get("status") == 200:
            print("✅ Cost has been added successfully.")
            return f"Details added with ID: {conversation_id}"
        else:
            print(f"❌ Failed to log cost details: {resp.text}")
            return None
    except Exception as e:
        print(f"⚠️ Error while sending request log: {e}")
        return None
