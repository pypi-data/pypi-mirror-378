#!/usr/bin/env python
# Script              : Main script for handling the cost through an Callback Handler.
# Component           : GenAi model deployment
# Author              : Bijoy Kumar Roy
# Copyright (c)       : 2024 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------

import os
import json
import pandas
import requests
import tiktoken
import pickle
import re
import traceback
from uuid import UUID
from datetime import datetime
from importlib import resources
from langchain_core.outputs import LLMResult
from typing import List, Any, Optional, Dict
from langchain.callbacks.base import BaseCallbackHandler
from tokenizers import Tokenizer
from llm.models import mappings
from distutils.util import strtobool
from pathlib import Path
from ..utilities.constants import SERVER_DOMAIN, SERVICE_TYPE
from ..utilities.logutils import handle_exception
from ..utilities.utils import (
    get_llm_provider,
    dict_based_prompt_to_langchain_prompt,
    extract_validity,
    answer_validation,
    increment_rate_limits_data,
)

from ..utilities.config import initialize_llm_models
from ..utilities.mongo_init import (
    get_local_mongo_cost_collection,
    get_model_provider,
    get_general_settings
)
from ..utilities.cost_handler import populate_model_cost

# Logger removed

PricesMongoCollection = get_local_mongo_cost_collection()

pricing_df = pandas.DataFrame(PricesMongoCollection.find({}))


class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        input_query,
        st,
        user,
        model,
        project_type,
        chatmode=None
    ):
        self.input_query = input_query
        self.input_text = None
        self.input_token_length = None
        self.output_text = None
        self.output_token_length = None
        self.input_cost = None
        self.output_cost = None
        self.total_cost = None
        self.encoding = None
        self.start_time = None
        self.end_time = None
        self.status = None
        self.latency = None
        self.start_time = st
        self.feedback = None
        self.user_name = user
        self.model_name = model
        self.project_name = "Ace"
        self.producttype = "Ace"
        self.validity = True
        self.project_type = project_type
        # self.answer_validation = answer_validaty
        # self.restricted_items_pattern = restricted_items_pattern
        # self.RESTRICTION_MESSAGE = restriction_message
        # self.message_id = message_id
        self.prediction = None
        self.embedding_modelName = None
        self.chatmode = None

        def safe_strtobool(value:str)->bool:
            try:
                return bool(strtobool(value.strip()))
            except (ValueError,AttributeError):
                return False  
                  
    #if not safe_strtobool(os.getenv("OFFLINE_ENVIRONMENT","False")):
        #self.encoding = tiktoken.get_encoding("cl100k_base")
        
        if get_model_provider(self.model_name) == "Cohere":
            #self.encoding = Tokenizer.from_pretrained("Cohere/command-nightly")
            with resources.files("routes.models").joinpath("cohere_command_nightly.pkl").open("rb") as f:
                self.encoding = pickle.load(f)
        elif "llama-2" in self.model_name.lower():
            #self.encoding = Tokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
            with resources.files("routes.models").joinpath("hf_internal_testing_llama_tokenizer.pkl").open("rb") as f:
                self.encoding  = pickle.load(f)
        elif "llama-3" in self.model_name.lower():
            #self.encoding = Tokenizer.from_pretrained("Xenova/llama-3-tokenizer")
             with resources.files("routes.models").joinpath("Xenova_llama_3_tokenizer.pkl").open("rb") as f:
                self.encoding = pickle.load(f)
        elif get_model_provider(self.model_name) == "Anthropic":
            with resources.open_text("routes.models", "anthropic_tokenizer.json") as f:
                json_data = json.load(f)
            json_str = json.dumps(json_data)
            self.encoding = Tokenizer.from_str(json_str)
        elif  "4o" in self.model_name.lower():
            with resources.files("routes.models").joinpath("o200k_base.pkl").open("rb") as f:
                self.encoding = pickle.load(f)
        else:
             with resources.files("routes.models").joinpath("cl100k_base.pkl").open("rb") as f:
                self.encoding = pickle.load(f)


        provider, _ = get_llm_provider(self.model_name, None)
        # Logger removed
        PricesMongoCollection = get_local_mongo_cost_collection()
        pricing_df = pandas.DataFrame(PricesMongoCollection.find({}))
        general_settings = get_general_settings()
        if self.chatmode=="search knowledge" or self.chatmode=="ace copilot":
            self.embedding_modelName = general_settings["modelConfig"]["ace"]["embeddingModel"]["modelName"]

        try:
            if provider != "katonic":
                self.model_pricing_dict = pricing_df[
                    pricing_df["modelName"] == self.model_name
                ]["metadata"].values[0]
            else:
                api_endpoint = general_settings["modelConfig"]["ace"]["primaryModel"]["metadata"]["apiRoute"]
                self.project_name = general_settings["modelConfig"]["ace"]["primaryModel"]["metadata"].get("projectName")
                provider_pricing_df = pricing_df[pricing_df["value"] == "katonicLLM"]
                self.model_pricing_dict = provider_pricing_df[
                    provider_pricing_df.metadata.apply(
                        lambda x: x["apiRoute"] == api_endpoint
                    )
                ]["metadata"].values[0]
            self.IS_COST_AVAILABLE = "inputCostPerToken" in self.model_pricing_dict
            # Logger removed
        except Exception:
            # Log the traceback without exposing sensitive information
            error_traceback = traceback.format_exc()
            error_message = "An error occurred. Traceback:\n" + error_traceback
            self.IS_COST_AVAILABLE = False
            # Logger removed

    def get_answer_validity(self, input, output):
        # Logger removed
        messages = answer_validation(None, query=input, response=output)
        self.llm_prompt = dict_based_prompt_to_langchain_prompt(messages)
        llm = initialize_llm_models(self.model_name, None)
        # Logger removed
        
        self.s_time_validation = datetime.now()
        
        self.model_output = llm.invoke(self.llm_prompt, config={"callbacks":[]})
    
        
        self.e_time_validation = datetime.now()
        
        self.validity = extract_validity(self.model_output.content)
        # Logger removed
        return self.validity

    def get_citation_token(self, doc):
        doc_references = re.findall(r"<span>(\d+)</span>", doc)
        final_doc_references = list(set(int(i) for i in doc_references))

        return final_doc_references

    def push_data(self):
        try:
            if len(self.output_text) > 0:
                try:
                    self.validity = self.get_answer_validity(
                        input=self.input_query, output=self.output_text
                    )
                    # self.validity = True
                    populate_model_cost(
                        input_text=self.llm_prompt[0].content,
                        output_text=self.model_output.content,
                        model_name=self.model_name,
                        user_name=self.user_name,
                        end_time=self.e_time_validation,
                        start_time=self.s_time_validation,
                        status="Success",
                        project_name="Ace",
                        project_type="Answer Validation",
                        product_type="Ace"
                    )
                except Exception as e:
                    pass  # Error - no action needed
        except Exception as e:
            pass  # Error - no action needed
        try:
            if self.restricted_items_pattern is not None:
                matches = self.restricted_items_pattern.search(self.output_text)
                if matches:
                    self.prediction = self.RESTRICTION_MESSAGE
                else:
                    self.prediction = self.output_text
            else:
                self.prediction = self.output_text
            target_url = f"{SERVER_DOMAIN}/logs/api/message/add"
            if "32k-online" in self.model_name:
                # Logger removed
                self.output_cost += float(self.model_pricing_dict["costPerRequest"])

            # Logger removed    
            payload = {
                "userName": self.user_name,
                "projectName": "Ace",
                "projectType": self.project_type,
                "productType": "Ace",
                "modelName": self.model_name if self.model_name is not None else self.project_name,
                "embeddingModelName": self.embedding_modelName,
                "inputTokenCost": self.input_cost,
                "inputTokens": self.input_token_length,
                "outputTokenCost": self.output_cost,
                "outputTokens": self.output_token_length,
                "totalCost": round(self.input_cost + self.output_cost, 4),
                "totalTokens": self.input_token_length + self.output_token_length,
                "request": self.input_query,
                "response": self.output_text,
                "context": self.input_text,
                "latency": round((self.end_time - self.start_time).total_seconds(), 4),
                "feedback": None,
                "status": self.status,
                "answered": self.validity,
                "conversationId": self.message_id,
                "tokenName": "Platform-Token"
            }
            # Logger removed
            increment_rate_limits_data(
                user_id=os.getenv("USER_EMAIL", self.user_name),
                application_id="Ace",
                cost_used=round(float(self.input_cost + self.output_cost),4),
                requests_used=0 if self.project_type == "Search Summary" else 1,
                logger=None,
            )

            response = requests.post(url=target_url, json=payload)
            if response.json()["status"] == 200:
                pass  # Success - no action needed
            else:
                pass  # Error - no action needed

        except Exception as e:
            pass  # Error - no action needed

    def save_citations(self):
        try:
            target_url = f"{SERVER_DOMAIN}/logs/api/citations/add"

            payload = {"messageId": self.message_id, "citations": self.citation}
            response = requests.post(url=target_url, json=payload, verify=False)
            if response.status_code == 200:
                pass  # Success - no action needed
            else:
                pass  # Error - no action needed
        except Exception as e:
            pass  # Error - no action needed

    def on_llm_start(
        self,
        serialized: "Dict[str, Any]",
        prompts: "List[str]",
        *,
        run_id: "UUID",
        parent_run_id: "Optional[UUID]" = None,
        tags: "Optional[List[str]]" = None,
        metadata: "Optional[Dict[str, Any]]" = None,
        **kwargs: "Any",
    ) -> "Any":
        self.input_text = prompts[0]
        # print(f"prompts: {self.input_text}")
        encode = []

        try:
            encode = self.encoding.encode(self.input_text, disallowed_special=())
        except Exception as e:
            encode = self.encoding.encode(self.input_text)    


        self.input_token_length = len(encode) if self.encoding else 0
        self.input_cost = (
            self.input_token_length
            * float(self.model_pricing_dict["inputCostPerToken"])
            if self.IS_COST_AVAILABLE
            else 0
        )
        self.end_time = datetime.now()

    def on_llm_end(
        self,
        response: "LLMResult",
        *,
        run_id: "UUID",
        parent_run_id: "Optional[UUID]" = None,
        **kwargs: "Any",
    ) -> "Any":
        
        self.output_text = response.generations[0][0].text
        # print(f"output_text: {self.output_text}")
        self.output_token_length = len(
            self.encoding.encode(self.output_text, disallowed_special=())
        ) if self.encoding else 0
        self.citation = self.get_citation_token(self.output_text)
        self.output_cost = (
            self.output_token_length
            * float(self.model_pricing_dict["outputCostPerToken"])
            if self.IS_COST_AVAILABLE
            else 0
        )
        self.status = "Success"
        self.push_data()
        self.save_citations()

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:

        self.output_text = str(error)
        self.output_token_length = 0
        self.output_cost = 0
        self.end_time = datetime.now()
        self.status = "Failed"
        self.push_data()
