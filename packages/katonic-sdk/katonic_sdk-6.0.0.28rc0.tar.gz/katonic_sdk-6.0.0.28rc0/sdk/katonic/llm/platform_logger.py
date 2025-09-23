#!/usr/bin/env python
#
# Copyright (c) 2024 Katonic Pty Ltd. All rights reserved.
#

import asyncio
import hashlib
import json
import os
import re
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    import warnings
    warnings.warn(
        "tiktoken not available. Token counting will be disabled. "
        "Install with 'pip install katonic[llm_deps]' to enable token counting.",
        UserWarning
    )

# Logger removed

def _get_model_provider(model_name: str) -> str:
    """Get model provider based on model name with comprehensive error handling"""
    try:
        if not model_name or not isinstance(model_name, str):
            return "Unknown"
            
        model_name_lower = model_name.lower()
        
        if "cohere" in model_name_lower:
            return "Cohere"
        elif "anthropic" in model_name_lower or "claude" in model_name_lower:
            return "Anthropic"
        elif "openai" in model_name_lower or "gpt" in model_name_lower:
            return "OpenAI"
        elif "llama" in model_name_lower:
            return "Llama"
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

def _get_encoding_for_model(model_name: str, offline_environment: bool = False):
    """Get appropriate encoding for the model with comprehensive error handling"""
    try:
        if not model_name or not isinstance(model_name, str):
            return None
            
        if offline_environment or not TIKTOKEN_AVAILABLE:
            return None
            
        provider = _get_model_provider(model_name)
        
        try:
            if provider == "Cohere":
                # For Cohere models, use cl100k_base as fallback
                return tiktoken.get_encoding("cl100k_base")
            elif "llama-2" in model_name.lower():
                # For Llama-2 models
                return tiktoken.get_encoding("cl100k_base")
            elif "llama-3" in model_name.lower():
                # For Llama-3 models
                return tiktoken.get_encoding("cl100k_base")
            elif provider == "Anthropic":
                # For Anthropic models
                return tiktoken.get_encoding("cl100k_base")
            elif "4o" in model_name.lower():
                # For GPT-4o models
                return tiktoken.get_encoding("o200k_base")
            else:
                # Default to cl100k_base
                return tiktoken.get_encoding("cl100k_base")
        except Exception as encoding_err:
            # Fallback to cl100k_base if specific encoding fails
            try:
                return tiktoken.get_encoding("cl100k_base")
            except Exception:
                return None
            
    except Exception as e:
        return None

def _calculate_tokens_and_cost(input_text: str, output_text: str, model_name: str, model_pricing: Optional[Dict] = None, offline_environment: bool = False):
    """Calculate tokens and costs based on model pricing with comprehensive error handling"""
    # Input validation
    if not input_text or not isinstance(input_text, str):
        input_text = ""
    if not output_text or not isinstance(output_text, str):
        output_text = ""
    if not model_name or not isinstance(model_name, str):
        model_name = "unknown"
        
    encoding = _get_encoding_for_model(model_name, offline_environment)
    
    input_token_length = 0
    output_token_length = 0
    input_cost = 0.0
    output_cost = 0.0
    
    if encoding:
        try:
            # Try with disallowed_special first, fallback to regular encode
            try:
                input_tokens = encoding.encode(input_text, disallowed_special=())
                output_tokens = encoding.encode(output_text, disallowed_special=())
            except Exception:
                try:
                    input_tokens = encoding.encode(input_text)
                    output_tokens = encoding.encode(output_text)
                except Exception:
                    # Fallback to simple word count estimation
                    input_token_length = len(input_text.split()) * 1.3
                    output_token_length = len(output_text.split()) * 1.3
                    return int(input_token_length), int(output_token_length), 0.0, 0.0
                
            input_token_length = len(input_tokens)
            output_token_length = len(output_tokens)
            
        except Exception as e:
            # Fallback to simple word count estimation
            input_token_length = len(input_text.split()) * 1.3
            output_token_length = len(output_text.split()) * 1.3
    else:
        # Fallback to simple word count estimation
        input_token_length = len(input_text.split()) * 1.3
        output_token_length = len(output_text.split()) * 1.3
    
    # Calculate costs with error handling
    try:
        if model_pricing and isinstance(model_pricing, dict) and "inputCostPerToken" in model_pricing and "outputCostPerToken" in model_pricing:
            try:
                input_cost = input_token_length * float(model_pricing["inputCostPerToken"])
                output_cost = output_token_length * float(model_pricing["outputCostPerToken"])
                
                # Handle special cases like Perplexity Online models
                if "32k-online" in model_name and "costPerRequest" in model_pricing:
                    output_cost += float(model_pricing["costPerRequest"])
            except (ValueError, TypeError) as pricing_err:
                # Fallback to default rates
                input_cost_per_token = 0.005 / 1000
                output_cost_per_token = 0.015 / 1000
                input_cost = input_token_length * input_cost_per_token
                output_cost = output_token_length * output_cost_per_token
        else:
            # Default GPT-4o rates if no pricing available
            input_cost_per_token = 0.005 / 1000  # $0.005 per 1K tokens
            output_cost_per_token = 0.015 / 1000  # $0.015 per 1K tokens
            input_cost = input_token_length * input_cost_per_token
            output_cost = output_token_length * output_cost_per_token
    except Exception as cost_err:
        input_cost = 0.0
        output_cost = 0.0
    
    return int(input_token_length), int(output_token_length), float(input_cost), float(output_cost)

def _generate_conversation_id(query: str, user_email: str):
    """Generate unique conversation ID with comprehensive error handling"""
    try:
        if not query or not isinstance(query, str):
            query = "default_query"
        if not user_email or not isinstance(user_email, str):
            user_email = "default_user"
            
        timestamp = hex(int(time.time()))[2:].zfill(8)
        random_part = hashlib.md5(f"{query}{user_email}{time.time()}".encode()).hexdigest()[:16]
        return f"{timestamp}{random_part}"
    except Exception as e:
        # Fallback to simple timestamp-based ID
        return f"fallback_{int(time.time())}_{hash(str(time.time())) % 10000}"

def _get_citation_tokens(text: str) -> List[int]:
    """Extract citation tokens from text with comprehensive error handling"""
    try:
        if not text or not isinstance(text, str):
            return []
            
        doc_references = re.findall(r"<span>(\d+)</span>", text)
        if not doc_references:
            return []
            
        final_doc_references = []
        for ref in doc_references:
            try:
                final_doc_references.append(int(ref))
            except ValueError:
                continue  # Skip invalid references
                
        return list(set(final_doc_references))
    except Exception as e:
        return []

def _save_citations(conversation_id: str, citations: List[int], server_domain: str):
    """Save citations to the platform with comprehensive error handling"""
    try:
        if not conversation_id or not isinstance(conversation_id, str):
            return
            
        if not citations or not isinstance(citations, list):
            return
            
        if not server_domain or not isinstance(server_domain, str):
            return
            
        target_url = f"{server_domain}/logs/api/citations/add"
        payload = {
            "messageId": str(conversation_id),
            "citations": citations
        }
        
        try:
            response = requests.post(
                url=target_url, 
                json=payload, 
                verify=False,
                timeout=5
            )
            
            if response.status_code == 200:
                pass  # Success case
            else:
                print(f"⚠️ Citation save failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Citation save timeout for message: {conversation_id}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Citation save connection error for message: {conversation_id}")
        except requests.exceptions.RequestException as req_err:
            print(f"⚠️ Citation save request error: {str(req_err)[:50]}...")
            
    except Exception as e:
        print(f"⚠️ Citation save error: {str(e)[:50]}...")

def log_to_platform(
    query: str,
    response: str,
    model_name: str,
    save_messages_api: str = "",
    server_domain: str = "http://log-ingestor:3000",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    user_email: str = "anonymous",
    processing_time: float = 0.0,
    context: Optional[str] = None,
    status: str = "Success",
    answered: bool = True,
    feedback: Optional[str] = None,
    message_id: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    chatmode: Optional[str] = None,
    offline_environment: bool = False,
    enable_logging: bool = True
) -> None:
    """
    Log request to Katonic platform with comprehensive error handling
    
    Args:
        query: User input query
        response: Model response
        model_name: Name of the model used
        save_messages_api: Platform API endpoint
        server_domain: Server domain for API calls (default: http://log-ingestor:3000)
        token_name: Token identifier
        project_name: Project identifier
        project_type: Type of project
        product_type: Product type
        user_email: User email/identifier
        processing_time: Time taken to process the request
        context: Additional context information
        status: Request status (Success/Failed)
        answered: Whether the query was answered
        feedback: User feedback if any
        message_id: Unique message ID (auto-generated if not provided)
        embedding_model_name: Embedding model name if used
        start_time: Start time of the request
        end_time: End time of the request
        chatmode: Chat mode (e.g., "search knowledge", "ace copilot")
        offline_environment: Skip token counting in offline mode
        enable_logging: Enable/disable logging
        
    Raises:
        ValueError: If required parameters are invalid
        RuntimeError: If logging fails critically
    """
    # Input validation
    if not enable_logging:
        return
        
    if not query or not isinstance(query, str):
        raise ValueError(f"Invalid query: {query}. Must be a non-empty string.")
        
    if not response or not isinstance(response, str):
        raise ValueError(f"Invalid response: {response}. Must be a non-empty string.")
        
    if not model_name or not isinstance(model_name, str):
        raise ValueError(f"Invalid model_name: {model_name}. Must be a non-empty string.")
        
    try:
        # Define variables upfront - matching callback.py structure
        input_text = query
        output_text = response
        
        # Calculate tokens and costs (fetch model pricing from MongoDB) with error handling
        try:
            input_token_length, output_token_length, input_cost, output_cost = _calculate_tokens_and_cost(
                input_text, output_text, model_name, None, offline_environment
            )
        except Exception as token_err:
            print(f"⚠️ Token calculation error: {str(token_err)[:50]}...")
            input_token_length, output_token_length, input_cost, output_cost = 0, 0, 0.0, 0.0
        
        # Generate message ID if not provided with error handling
        if not message_id:
            try:
                message_id = _generate_conversation_id(query, user_email)
            except Exception as id_err:
                print(f"⚠️ Message ID generation error: {str(id_err)[:50]}...")
                message_id = f"fallback_{int(time.time())}"
        
        # Use response as prediction (no restricted content handling)
        prediction = output_text
        
        # Calculate latency with error handling
        try:
            if start_time and end_time:
                if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
                    latency = round(float(processing_time), 4)
                else:
                    latency = round((end_time - start_time).total_seconds(), 4)
            else:
                latency = round(float(processing_time), 4)
        except Exception:
            latency = 0.0
        
        # Create payload with comprehensive error handling
        try:
            payload = {
                "userName": str(user_email) if user_email else "anonymous",
                "projectName": str(project_name) if project_name else "katonic-sdk",
                "projectType": str(project_type) if project_type else "llm-query",
                "productType": str(product_type) if product_type else "katonic-sdk",
                "modelName": str(model_name) if model_name else str(project_name),
                "embeddingModelName": str(embedding_model_name) if embedding_model_name else None,
                "inputTokenCost": round(float(input_cost), 4),
                "inputTokens": int(input_token_length),
                "outputTokenCost": round(float(output_cost), 4),
                "outputTokens": int(output_token_length),
                "totalCost": round(float(input_cost + output_cost), 4),
                "totalTokens": int(input_token_length + output_token_length),
                "request": str(input_text),
                "response": str(output_text),
                "context": str(context) if context else str(input_text),
                "latency": float(latency),
                "feedback": str(feedback) if feedback else None,
                "status": str(status) if status else "Success",
                "answered": bool(answered),
                "messageId": str(message_id),
                "tokenName": str(token_name) if token_name else "Platform-Token",
            }
        except Exception as payload_err:
            raise RuntimeError(f"Failed to create logging payload: {str(payload_err)}")
        
        
        # Determine API endpoint with error handling
        try:
            if server_domain:
                target_url = f"{server_domain}/logs/api/message/add"
            else:
                target_url = save_messages_api
            
            if not target_url:
                print("⚠️ No target URL available for logging")
                return
        except Exception as url_err:
            print(f"⚠️ URL construction error: {str(url_err)[:50]}...")
            return
            
        # API call to Katonic with comprehensive error handling
        try:
            response = requests.post(
                url=target_url,
                json=payload,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get("status") == 200:
                        print(f"✅ Logged request to platform: {message_id}")
                    else:
                        print(f"⚠️ Logging response status: {response_data.get('status')}")
                except Exception as json_err:
                    print(f"⚠️ Invalid JSON response: {str(json_err)[:50]}...")
            else:
                print(f"⚠️ Logging HTTP response: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Logging timeout for message: {message_id}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Logging connection error for message: {message_id}")
        except requests.exceptions.RequestException as req_err:
            print(f"⚠️ Logging request error: {str(req_err)[:50]}...")
        except Exception as e:
            print(f"⚠️ Logging failed: {str(e)[:50]}...")
        
        # Handle citations if available with error handling
        try:
            citations = _get_citation_tokens(output_text)
            if citations and server_domain:
                _save_citations(message_id, citations, server_domain)
        except Exception as citation_err:
            print(f"⚠️ Citation handling error: {str(citation_err)[:50]}...")
            
    except ValueError as ve:
        print(f"⚠️ Validation error: {str(ve)[:50]}...")
        raise ve
    except RuntimeError as re:
        print(f"⚠️ Runtime error: {str(re)[:50]}...")
        raise re
    except Exception as e:
        print(f"⚠️ Unexpected logging error: {str(e)[:50]}...")
        # Don't re-raise to avoid breaking the main flow

def log_to_platform_sync(
    query: str,
    response: str,
    model_name: str,
    save_messages_api: str = "",
    server_domain: str = "http://log-ingestor:3000",
    token_name: str = "Platform-Token",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    user_email: str = "anonymous",
    processing_time: float = 0.0,
    context: Optional[str] = None,
    status: str = "Success",
    answered: bool = True,
    feedback: Optional[str] = None,
    message_id: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    chatmode: Optional[str] = None,
    offline_environment: bool = False,
    enable_logging: bool = True
) -> None:
    """
    Synchronous version of log_to_platform with comprehensive error handling
    """
    try:
        # Call the synchronous log_to_platform function directly
        log_to_platform(
            query, response, model_name, save_messages_api, server_domain,
            token_name, project_name, project_type, product_type, user_email,
            processing_time, context, status, answered, feedback, message_id,
            embedding_model_name, start_time, end_time, chatmode,
            offline_environment, enable_logging
        )
    except ValueError as ve:
        print(f"⚠️ Sync logging validation error: {str(ve)[:50]}...")
        # Don't re-raise to avoid breaking the main flow
    except RuntimeError as re:
        print(f"⚠️ Sync logging runtime error: {str(re)[:50]}...")
        # Don't re-raise to avoid breaking the main flow
    except Exception as e:
        print(f"⚠️ Sync logging error: {str(e)[:50]}...")
        # Don't re-raise to avoid breaking the main flow