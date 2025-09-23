import requests
import time
import re
import hashlib
import random
from datetime import datetime
from .schemas import PredictSchema
from .models.completion import initialize_model_factory
from .logutils import handle_exception
from typing import Dict, Any, Optional, Union, Generator


def fetch_model_data(model_id):
    """
    Fetch model data from the log ingestor service with comprehensive error handling.
    
    Args:
        model_id: The ID of the model to fetch
        
    Returns:
        dict: Model data from the service
        
    Raises:
        ValueError: If model_id is invalid or missing
        ConnectionError: For network/connection issues
        RuntimeError: For unexpected errors
    """
    # Input validation
    if not model_id or not isinstance(model_id, str):
        raise ValueError(f"Invalid model_id: {model_id}. Must be a non-empty string.")
    
    try:
        # Use localhost for testing - no environment variables
        LOG_INGESTOR_URL = "http://log-ingestor:3000"
        FETCH_MODEL_URL = f"{LOG_INGESTOR_URL}/logs/api/models/get"

        payload = {"model_id": model_id}
        
        # Make request with timeout and retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url=FETCH_MODEL_URL, 
                    json=payload,
                    timeout=30,
                    verify=False
                )
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Timeout after {max_retries} attempts fetching model data for {model_id}")
                time.sleep(1)
            except requests.exceptions.ConnectionError as conn_err:
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Connection error fetching model data for {model_id}: {str(conn_err)}")
                time.sleep(1)
        
        # Parse response
        try:
            data = response.json()
        except ValueError as json_err:
            raise ConnectionError(f"Invalid JSON response for model_id {model_id}: {str(json_err)}")

        # Validate response structure
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict response for model_id {model_id}, got {type(data)}")
            
        if "model" not in data:
            raise ValueError(f"'model' key missing in response for model_id {model_id}: {data}")
            
        return data
        
    except requests.exceptions.RequestException as req_err:
        raise ConnectionError(f"Request error fetching model data for {model_id}: {str(req_err)}")
    except ValueError as val_err:
        raise val_err
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching model data for {model_id}: {str(e)}")

def fetch_model_object(model_id):
    """
    Fetch model object by creating an instance using model data with comprehensive error handling.
    
    Args:
        model_id: The ID of the model to fetch
        
    Returns:
        Model object instance
        
    Raises:
        ValueError: If model_id is invalid or model data is incomplete
        ConnectionError: If model data cannot be fetched
        RuntimeError: If model object creation fails
    """
    # Input validation
    if not model_id or not isinstance(model_id, str):
        raise ValueError(f"Invalid model_id: {model_id}. Must be a non-empty string.")
    
    try:
        model_data = fetch_model_data(model_id)

        # Extract provider and model name with validation
        model_info = model_data.get("model", {})
        if not isinstance(model_info, dict):
            raise ValueError(f"Invalid model info structure for model_id {model_id}: {type(model_info)}")
        
        provider = model_info.get("parent")
        metadata = model_info.get("metadata", {})
        
        if not isinstance(metadata, dict):
            metadata = {}
        
        model_name = metadata.get("endpoint")
        
        # Fallback logic for model name and provider
        if model_name is None:
            model_name = model_info.get("modelName")
            provider = model_info.get("value")
            if provider == "katonicLLM":
                provider = "katonic"
        
        # Validate required fields
        if not provider:
            raise ValueError(f"Missing provider for model_id {model_id}. Available fields: {list(model_info.keys())}")
            
        if not model_name:
            raise ValueError(f"Missing model name for model_id {model_id}. Provider: {provider}")
        
        return get_llm(model_id, provider, model_name)
        
    except ValueError as val_err:
        raise val_err
    except ConnectionError as conn_err:
        raise conn_err
    except Exception as e:
        raise RuntimeError(f"Unexpected error creating model object for {model_id}: {str(e)}")

def get_llm(model_id, provider, model_name):
    """
    Get LLM model instance using the model factory with comprehensive error handling.
    
    Args:
        model_id: The ID of the model
        provider: The provider name (e.g., "OpenAI", "Anthropic", etc.)
        model_name: The name of the model
        
    Returns:
        Model object instance
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If model factory initialization fails
    """
    # Input validation
    if not all([model_id, provider, model_name]):
        raise ValueError(f"Missing required parameters - model_id: {model_id}, provider: {provider}, model_name: {model_name}")
    
    if not all(isinstance(param, str) for param in [model_id, provider, model_name]):
        raise ValueError(f"All parameters must be strings - model_id: {type(model_id)}, provider: {type(provider)}, model_name: {type(model_name)}")
    
    try:
        model_instance = initialize_model_factory(model_id, provider, model_name, None)
        
        if model_instance is None:
            raise RuntimeError(f"Model factory returned None for {provider}/{model_name}")
        
        return model_instance
        
    except Exception as e:
        raise RuntimeError(f"Error initializing model factory for {provider}/{model_name}: {str(e)}")

def fetch_stream_response(provider, model_object, query):
    """
    Fetch streaming response from model object with comprehensive error handling.
    
    Args:
        provider: The provider name
        model_object: The model object instance
        query: The query string
        
    Yields:
        str: Response tokens or complete response
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If streaming fails
    """
    # Input validation
    if not provider or not isinstance(provider, str):
        raise ValueError(f"Invalid provider: {provider}. Must be a non-empty string.")
    
    if model_object is None:
        raise ValueError("Model object cannot be None")
    
    if not query or not isinstance(query, str):
        raise ValueError(f"Invalid query: {query}. Must be a non-empty string.")
    
    try:
        if provider in [
            "alephalpha",
            "huggingface",
            "ai21",
            "replicate",
            "togetherai",
            # "katonic",
            "bedrock",
            "Anyscale",
        ]:
            try:
                response = model_object.invoke(query)
                if hasattr(response, "content"):
                    response = response.content
                yield response
            except Exception as e:
                yield f"Error in non-streaming response: {str(e)}"
        else:
            try:
                previous_token = ""
                for token in model_object.stream(query):
                    try:
                        if hasattr(token, "content"):
                            token = token.content
                            if previous_token != " " and token == "<":
                                token = " <"
                            if previous_token == "(" and token == "<":
                                token = " <"
                            if token == "(<":
                                token = "( <"
                            if token == ">[":
                                token = ">"
                            if token == "]<":
                                token = "<"
                            previous_token = token
                            yield token
                        else:
                            yield token
                    except Exception as token_err:
                        yield f"Error processing token: {str(token_err)}"
            except Exception as stream_err:
                err_msg = handle_exception()
                yield f"Streaming error: {str(err_msg)}"
    except Exception as e:
        yield f"Critical streaming error: {str(e)}"

def _generate_conversation_id(query: str, user: str):
    """Generate unique conversation ID with error handling"""
    try:
        if not query or not isinstance(query, str):
            query = "default_query"
        if not user or not isinstance(user, str):
            user = "default_user"
            
        current_time = time.time()
        timestamp = hex(int(current_time))[2:].zfill(8)
        # Add random component to ensure uniqueness even for rapid calls
        random_component = random.randint(1000, 9999)
        random_part = hashlib.md5(f"{query}{user}{current_time}{random_component}".encode()).hexdigest()[:16]
        return f"{timestamp}{random_part}"
    except Exception as e:
        # Fallback to simple timestamp-based ID
        return f"fallback_{int(time.time())}_{random.randint(1000, 9999)}"

def _get_citation_tokens(text: str):
    """Extract citation tokens from text with error handling"""
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
    except Exception:
        return []

def log_llm_request(
    query: str,
    response: str,
    model_name: str,
    model_id: str,
    user: str = "anonymous",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    processing_time: float = 0.0,
    status: str = "Success",
    answered: bool = True,
    feedback: Optional[str] = None,
    message_id: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    chatmode: Optional[str] = None,
    enable_logging: bool = True
):
    """
    Log LLM request to the platform with comprehensive metrics and error handling.
    This function creates logs similar to what's shown in the dashboard image.
    
    Args:
        query: User input query
        response: Model response
        model_name: Name of the model used
        model_id: The model ID
        user: User identifier
        project_name: Project name
        project_type: Type of project
        product_type: Product type
        start_time: Start time of the request
        end_time: End time of the request
        processing_time: Time taken to process the request
        status: Request status (Success/Failed)
        answered: Whether the query was answered
        feedback: User feedback if any
        message_id: Unique message ID
        embedding_model_name: Embedding model name if used
        chatmode: Chat mode
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
        
    if not model_id or not isinstance(model_id, str):
        raise ValueError(f"Invalid model_id: {model_id}. Must be a non-empty string.")
        
    try:
        # Generate message ID if not provided
        if not message_id:
            message_id = _generate_conversation_id(query, user)
        
        # Use response as prediction (no restricted content handling)
        prediction = response
        
        # Calculate latency with error handling
        try:
            if start_time and end_time:
                if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
                    latency = round(processing_time, 4)
                else:
                    latency = round((end_time - start_time).total_seconds(), 4)
            else:
                latency = round(float(processing_time), 4)
        except Exception:
            latency = 0.0
        
        # Simple token estimation with error handling
        try:
            input_tokens = len(query.split()) * 1.3  # Rough estimation
            output_tokens = len(response.split()) * 1.3  # Rough estimation
        except Exception:
            input_tokens = 0
            output_tokens = 0
        
        # Simple cost calculation with error handling
        try:
            input_cost = input_tokens * 0.0001  # Default cost per token
            output_cost = output_tokens * 0.0002  # Default cost per token
            
            # Handle special cases like Perplexity Online models
            if "32k-online" in model_name:
                output_cost += 0.01  # Additional cost per request
        except Exception:
            input_cost = 0.0
            output_cost = 0.0
        
        # Create payload matching the dashboard structure with error handling
        try:
            payload = {
                "userName": str(user) if user else "anonymous",
                "projectName": str(project_name) if project_name else "katonic-sdk",
                "projectType": str(project_type) if project_type else "llm-query",
                "productType": str(product_type) if product_type else "katonic-sdk",
                "modelName": str(model_name) if model_name else str(project_name),
                "embeddingModelName": str(embedding_model_name) if embedding_model_name else None,
                "inputTokenCost": round(float(input_cost), 4),
                "inputTokens": int(input_tokens),
                "outputTokenCost": round(float(output_cost), 4),
                "outputTokens": int(output_tokens),
                "totalCost": round(float(input_cost + output_cost), 4),
                "totalTokens": int(input_tokens + output_tokens),
                "request": str(query),
                "response": str(prediction),
                "context": str(query),
                "latency": float(latency),
                "feedback": str(feedback) if feedback else None,
                "status": str(status) if status else "Success",
                "answered": bool(answered),
                "messageId": str(message_id),
                "tokenName": "Platform-Token"
            }
        except Exception as payload_err:
            raise RuntimeError(f"Failed to create logging payload: {str(payload_err)}")
        
        # Send to platform with comprehensive error handling
        target_url = "http://log-ingestor:3000/logs/api/message/add"
        
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
            citations = _get_citation_tokens(response)
            if citations:
                try:
                    citation_url = "http://log-ingestor:3000/logs/api/citations/add"
                    citation_payload = {
                        "messageId": str(message_id),
                        "citations": citations
                    }
                    citation_response = requests.post(
                        url=citation_url, 
                        json=citation_payload, 
                        verify=False,
                        timeout=5
                    )
                    if citation_response.status_code != 200:
                        print(f"⚠️ Citation logging failed: {citation_response.status_code}")
                except Exception as citation_err:
                    print(f"⚠️ Citation logging error: {str(citation_err)[:50]}...")
        except Exception as citation_parse_err:
            print(f"⚠️ Citation parsing error: {str(citation_parse_err)[:50]}...")
            
    except Exception as e:
        print(f"⚠️ Logging error: {str(e)[:50]}...")

def generate_completion(
    model_id: str, 
    data: Dict[str, Any], 
    user: Optional[str] = "anonymous",
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    enable_logging: bool = True
) -> Union[str, Generator[str, None, None]]:
    """
    Generate completion using LLM models with integrated platform logging and comprehensive error handling.
    
    Args:
        model_id: The ID of the model to use
        data: Dictionary containing the query and other parameters
        user: User identifier (default: "anonymous")
        project_name: Project name for logging
        project_type: Type of project for logging
        product_type: Product type for logging
        enable_logging: Enable/disable platform logging
    
    Returns:
        Union[str, Generator[str, None, None]]: Either a string response or generator for streaming
        
    Raises:
        ValueError: If required parameters are missing or invalid
        ConnectionError: If model data cannot be fetched
        RuntimeError: If model object creation fails or other critical errors occur
    """
    # Input validation
    if not model_id or not isinstance(model_id, str):
        raise ValueError(f"Invalid model_id: {model_id}. Must be a non-empty string.")
        
    if not data or not isinstance(data, dict):
        raise ValueError(f"Invalid data: {data}. Must be a non-empty dictionary.")
        
    if user is not None and not isinstance(user, str):
        raise ValueError(f"Invalid user: {user}. Must be a string or None.")
        
    start_time = datetime.now()
    start_timestamp = time.time()
    
    try:
        model_data = fetch_model_data(model_id)
        
        # Extract model information with error handling
        try:
            model_info = model_data.get("model", {})
            if not isinstance(model_info, dict):
                raise ValueError(f"Invalid model info structure: {type(model_info)}")
                
            metadata = model_info.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
                
            model_name = metadata.get("endpoint")
            provider = model_info.get("parent")
            
            # Fallback for model name
            if not model_name:
                model_name = model_info.get("modelName")
                if not provider:
                    provider = model_info.get("value")
                    if provider == "katonicLLM":
                        provider = "katonic"
                        
        except Exception as model_err:
            raise RuntimeError(f"Failed to extract model information: {str(model_err)}")

        if "query" not in data:
            raise ValueError("'query' key is missing in the request payload")
        
        query = data["query"]
        if not query or not isinstance(query, str):
            raise ValueError(f"Invalid query: {query}. Must be a non-empty string.")
        
        # Handle vision models with error handling
        if "image_url" in data and provider == "OpenAI":
            try:
                from .multimodal.openai_vision import process_vision_request
                
                image_url = data["image_url"]
                if not image_url or not isinstance(image_url, str):
                    raise ValueError(f"Invalid image_url: {image_url}. Must be a non-empty string.")
                
                result = process_vision_request(
                    image_url,
                    query,
                    model_id,
                    model_name,
                    None
                )
                
                # Log the vision request
                end_time = datetime.now()
                processing_time = time.time() - start_timestamp
                
                try:
                    log_llm_request(
                        query=query,
                        response=str(result),
                        model_name=model_name or "vision-model",
                        model_id=model_id,
                        user=user,
                        project_name=project_name,
                        project_type=project_type,
                        product_type=product_type,
                        start_time=start_time,
                        end_time=end_time,
                        processing_time=processing_time,
                        status="Success",
                        answered=True,
                        enable_logging=enable_logging
                    )
                except Exception as log_err:
                    print(f"⚠️ Vision logging error: {str(log_err)[:50]}...")
                
                return result
                
            except ImportError as import_err:
                raise RuntimeError(f"Vision module not available: {str(import_err)}")
            except Exception as vision_err:
                raise RuntimeError(f"Vision processing failed: {str(vision_err)}")
            
        model_object = fetch_model_object(model_id)
        
        if data.get("stream") == True:
            # Handle streaming response with error handling
            def stream_with_logging():
                response_text = ""
                try:
                    for chunk in fetch_stream_response(provider, model_object, query):
                        chunk_str = str(chunk)
                        response_text += chunk_str
                        yield chunk_str
                    
                    # Log the streaming response
                    end_time = datetime.now()
                    processing_time = time.time() - start_timestamp
                    
                    try:
                        log_llm_request(
                            query=query,
                            response=response_text,
                            model_name=model_name or "streaming-model",
                            model_id=model_id,
                            user=user,
                            project_name=project_name,
                            project_type=project_type,
                            product_type=product_type,
                            start_time=start_time,
                            end_time=end_time,
                            processing_time=processing_time,
                            status="Success",
                            answered=True,
                            enable_logging=enable_logging
                        )
                    except Exception as log_err:
                        print(f"⚠️ Streaming logging error: {str(log_err)[:50]}...")
                        
                except Exception as stream_err:
                    # Yield error message and log the failure
                    error_msg = f"Streaming error: {str(stream_err)}"
                    yield error_msg
                    
                    try:
                        end_time = datetime.now()
                        processing_time = time.time() - start_timestamp
                        
                        log_llm_request(
                            query=query,
                            response=error_msg,
                            model_name=model_name or "streaming-model",
                            model_id=model_id,
                            user=user,
                            project_name=project_name,
                            project_type=project_type,
                            product_type=product_type,
                            start_time=start_time,
                            end_time=end_time,
                            processing_time=processing_time,
                            status="Failed",
                            answered=False,
                            enable_logging=enable_logging
                        )
                    except Exception as log_err:
                        print(f"⚠️ Error logging failed: {str(log_err)[:50]}...")
            
            return stream_with_logging()
            
        # Handle non-streaming response with comprehensive error handling
        try:
            result = model_object.invoke(query)
        except TypeError as e:
            if "coroutine" in str(e):
                # Handle async invoke
                try:
                    import asyncio
                    result = asyncio.run(model_object.ainvoke(query))
                except Exception as async_err:
                    raise RuntimeError(f"Async invoke failed: {str(async_err)}")
            else:
                raise e
        except Exception as invoke_err:
            raise RuntimeError(f"Model invoke failed: {str(invoke_err)}")

        # Extract response text with error handling
        try:
            if hasattr(result, "content"):
                response_text = result.content
            else:
                response_text = str(result)
                
            if not response_text:
                response_text = "Empty response from model"
                
        except Exception as extract_err:
            raise RuntimeError(f"Failed to extract response: {str(extract_err)}")
        
        # Log the completion with error handling
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        try:
            log_llm_request(
                query=query,
                response=response_text,
                model_name=model_name or "completion-model",
                model_id=model_id,
                user=user,
                project_name=project_name,
                project_type=project_type,
                product_type=product_type,
                start_time=start_time,
                end_time=end_time,
                processing_time=processing_time,
                status="Success",
                answered=True,
                enable_logging=enable_logging
            )
        except Exception as log_err:
            print(f"⚠️ Completion logging error: {str(log_err)[:50]}...")
        
        return response_text
            
    except ValueError as ve:
        # Log the error with comprehensive error handling
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        try:
            error_query = data.get("query", "") if data else ""
            if not isinstance(error_query, str):
                error_query = str(error_query)
                
            log_llm_request(
                query=error_query,
                response=f"ValueError: {str(ve)}",
                model_name="error-model",
                model_id=model_id,
                user=user,
                project_name=project_name,
                project_type=project_type,
                product_type=product_type,
                start_time=start_time,
                end_time=end_time,
                processing_time=processing_time,
                status="Failed",
                answered=False,
                enable_logging=enable_logging
            )
        except Exception as log_err:
            print(f"⚠️ Error logging failed: {str(log_err)[:50]}...")
        
        raise ValueError(str(ve))
    except ConnectionError as ce:
        # Log connection errors
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        try:
            error_query = data.get("query", "") if data else ""
            if not isinstance(error_query, str):
                error_query = str(error_query)
                
            log_llm_request(
                query=error_query,
                response=f"ConnectionError: {str(ce)}",
                model_name="error-model",
                model_id=model_id,
                user=user,
                project_name=project_name,
                project_type=project_type,
                product_type=product_type,
                start_time=start_time,
                end_time=end_time,
                processing_time=processing_time,
                status="Failed",
                answered=False,
                enable_logging=enable_logging
            )
        except Exception as log_err:
            print(f"⚠️ Connection error logging failed: {str(log_err)[:50]}...")
        
        raise ConnectionError(str(ce))
    except Exception as e:
        # Log all other errors with comprehensive error handling
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        try:
            error_query = data.get("query", "") if data else ""
            if not isinstance(error_query, str):
                error_query = str(error_query)
                
            log_llm_request(
                query=error_query,
                response=f"RuntimeError: {str(e)}",
                model_name="error-model",
                model_id=model_id,
                user=user,
                project_name=project_name,
                project_type=project_type,
                product_type=product_type,
                start_time=start_time,
                end_time=end_time,
                processing_time=processing_time,
                status="Failed",
                answered=False,
                enable_logging=enable_logging
            )
        except Exception as log_err:
            print(f"⚠️ Runtime error logging failed: {str(log_err)[:50]}...")
        
        raise RuntimeError(f"Internal server error: {str(e)}")


def generate_completion_with_schema(
    elements: PredictSchema,
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    enable_logging: bool = True
) -> Union[str, Generator[str, None, None]]:
    """
    Generate completion using LLM models with PredictSchema and platform logging with comprehensive error handling.
    
    Args:
        elements: PredictSchema object containing model_id, data, and user
        project_name: Project name for logging
        project_type: Type of project for logging
        product_type: Product type for logging
        enable_logging: Enable/disable platform logging
        
    Returns:
        Union[str, Generator[str, None, None]]: Either a string response or generator for streaming
        
    Raises:
        ValueError: If PredictSchema elements are invalid
        RuntimeError: If completion generation fails
    """
    # Input validation
    if not elements:
        raise ValueError("PredictSchema elements cannot be None")
        
    if not hasattr(elements, 'model_id') or not elements.model_id:
        raise ValueError("PredictSchema must have a valid model_id")
        
    if not hasattr(elements, 'data') or not elements.data:
        raise ValueError("PredictSchema must have valid data")
        
    try:
        return generate_completion(
            elements.model_id, 
            elements.data, 
            elements.user,
            project_name=project_name,
            project_type=project_type,
            product_type=product_type,
            enable_logging=enable_logging
        )
    except Exception as e:
        raise RuntimeError(f"Schema-based completion failed: {str(e)}")