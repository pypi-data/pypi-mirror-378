import requests
import time
import re
import hashlib
from datetime import datetime
from .schemas import PredictSchema
from .models.completion import initialize_model_factory
from .logutils import handle_exception
from typing import Dict, Any, Optional, Union, AsyncGenerator


def fetch_model_data(model_id):
    """
    Fetch model data from the log ingestor service.
    
    Args:
        model_id: The ID of the model to fetch
        
    Returns:
        dict: Model data from the service
        
    Raises:
        ConnectionError: For various error conditions
    """
    try:
        # Use localhost for testing - no environment variables
        LOG_INGESTOR_URL = "http://log-ingestor:3000"
        FETCH_MODEL_URL = f"{LOG_INGESTOR_URL}/logs/api/models/get"

        payload = {"model_id": model_id}
        response = requests.post(url=FETCH_MODEL_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "model" not in data:
            raise ValueError(
                f"'model data'is missing in response for model_id {model_id}: {data}"
            )
        return data
    except requests.exceptions.RequestException as req_err:
        raise ConnectionError(f"Error fetching model data: {str(req_err)}")
    except ValueError as val_err:
        raise ValueError(str(val_err))
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")

def fetch_model_object(model_id):
    """
    Fetch model object by creating an instance using model data.
    
    Args:
        model_id: The ID of the model to fetch
        
    Returns:
        Model object instance
        
    Raises:
        RuntimeError: If model object creation fails
    """
    try:
        model_data = fetch_model_data(model_id)

        provider = model_data["model"].get("parent")
        model_name = model_data["model"]["metadata"].get("endpoint")
        if model_name is None:
            model_name = model_data["model"]["modelName"]
            provider = model_data["model"]["value"]
            if provider == "katonicLLM":
                provider = "katonic"
        if not provider or not model_name:
            raise ValueError(f"Missing provider or endpoint for model_id {model_id}")
        return get_llm(model_id, provider, model_name)
    except Exception as e:
        raise RuntimeError(f"Error creating model object: {str(e)}")

def get_llm(model_id, provider, model_name):
    """
    Get LLM model instance using the model factory.
    
    Args:
        model_id: The ID of the model
        provider: The provider name (e.g., "OpenAI", "Anthropic", etc.)
        model_name: The name of the model
        
    Returns:
        Model object instance
    """
    return initialize_model_factory(model_id, provider, model_name, None)

async def fetch_stream_response(provider, model_object, query):
    """
    Fetch streaming response from model object.
    
    Args:
        provider: The provider name
        model_object: The model object instance
        query: The query string
        
    Yields:
        str: Response tokens or complete response
    """
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
        response = model_object.invoke(query)
        if hasattr(response, "content"):
            response = response.content
        yield response
    else:
        try:
            previous_token = ""
            async for token in model_object.astream(query):
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
        except Exception:
            err_msg = handle_exception()
            yield str(err_msg)

def _generate_conversation_id(query: str, user_email: str):
    """Generate unique conversation ID"""
    timestamp = hex(int(time.time()))[2:].zfill(8)
    random_part = hashlib.md5(f"{query}{user_email}{time.time()}".encode()).hexdigest()[:16]
    return f"{timestamp}{random_part}"

def _get_citation_tokens(text: str):
    """Extract citation tokens from text"""
    try:
        doc_references = re.findall(r"<span>(\d+)</span>", text)
        final_doc_references = list(set(int(i) for i in doc_references))
        return final_doc_references
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
    conversation_id: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    restricted_items_pattern: Optional[Any] = None,
    restriction_message: Optional[str] = None,
    chatmode: Optional[str] = None,
    enable_logging: bool = True
):
    """
    Log LLM request to the platform with comprehensive metrics.
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
        conversation_id: Unique conversation ID
        embedding_model_name: Embedding model name if used
        restricted_items_pattern: Pattern for restricted content
        restriction_message: Message for restricted content
        chatmode: Chat mode
        enable_logging: Enable/disable logging
    """
    if not enable_logging:
        return
        
    try:
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = _generate_conversation_id(query, user)
        
        # Handle restricted content
        prediction = response
        if restricted_items_pattern is not None:
            matches = restricted_items_pattern.search(response)
            if matches:
                prediction = restriction_message or "Content restricted"
        
        # Calculate latency
        if start_time and end_time:
            latency = round((end_time - start_time).total_seconds(), 4)
        else:
            latency = round(processing_time, 4)
        
        # Simple token estimation (no external dependencies)
        input_tokens = len(query.split()) * 1.3  # Rough estimation
        output_tokens = len(response.split()) * 1.3  # Rough estimation
        
        # Simple cost calculation (no external pricing data)
        input_cost = input_tokens * 0.0001  # Default cost per token
        output_cost = output_tokens * 0.0002  # Default cost per token
        
        # Handle special cases like Perplexity Online models
        if "32k-online" in model_name:
            output_cost += 0.01  # Additional cost per request
        
        # Create payload matching the dashboard structure
        payload = {
            "userName": user,
            "projectName": project_name,
            "projectType": project_type,
            "productType": product_type,
            "modelName": model_name if model_name is not None else project_name,
            "embeddingModelName": embedding_model_name,
            "inputTokenCost": round(input_cost, 4),
            "inputTokens": int(input_tokens),
            "outputTokenCost": round(output_cost, 4),
            "outputTokens": int(output_tokens),
            "totalCost": round(input_cost + output_cost, 4),
            "totalTokens": int(input_tokens + output_tokens),
            "request": query,
            "response": prediction,
            "context": query,
            "latency": latency,
            "feedback": feedback,
            "status": status,
            "answered": answered,
            "conversationId": conversation_id,
            "tokenName": "Platform-Token"
        }
        
        # Send to platform (using localhost for testing)
        target_url = "http://log-ingestor:3000/logs/api/message/add"
        
        try:
            response = requests.post(
                url=target_url,
                json=payload,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200 and response.json().get("status") == 200:
                print(f"✅ Logged request to platform: {conversation_id}")
            else:
                print(f"⚠️ Logging response: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Logging failed (expected in test environment): {str(e)[:50]}...")
        
        # Handle citations if available
        citations = _get_citation_tokens(response)
        if citations:
            try:
                citation_url = "http://log-ingestor:3000/logs/api/citations/add"
                citation_payload = {
                    "messageId": conversation_id,
                    "citations": citations
                }
                requests.post(url=citation_url, json=citation_payload, verify=False)
            except Exception:
                pass  # Citation logging failed
            
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
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Generate completion using LLM models with integrated platform logging.
    
    Args:
        model_id: The ID of the model to use
        data: Dictionary containing the query and other parameters
        user: User identifier (default: "anonymous")
        project_name: Project name for logging
        project_type: Type of project for logging
        product_type: Product type for logging
        enable_logging: Enable/disable platform logging
    
    Returns:
        Union[str, AsyncGenerator[str, None]]: Either a string response or async generator for streaming
        
    Raises:
        ValueError: If required parameters are missing
        ConnectionError: If model data cannot be fetched
        RuntimeError: If model object creation fails
    """
    start_time = datetime.now()
    start_timestamp = time.time()
    
    try:
        model_data = fetch_model_data(model_id)
        model_name = model_data["model"]["metadata"].get("endpoint")
        provider = model_data["model"].get("parent")

        if "query" not in data:
            raise ValueError("'query' key is missing in the request payload")
        
        query = data["query"]
        
        # Handle vision models
        if "image_url" in data and provider == "OpenAI":
            from .multimodal.openai_vision import process_vision_request
            result = process_vision_request(
                data["image_url"],
                data["query"],
                model_id,
                model_name,
                None
            )
            
            # Log the vision request
            end_time = datetime.now()
            processing_time = time.time() - start_timestamp
            
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
            
            return result
            
        model_object = fetch_model_object(model_id)
        
        if data.get("stream") == True:
            # Handle streaming response
            async def stream_with_logging():
                response_text = ""
                async for chunk in fetch_stream_response(provider, model_object, query):
                    response_text += str(chunk)
                    yield chunk
                
                # Log the streaming response
                end_time = datetime.now()
                processing_time = time.time() - start_timestamp
                
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
            
            return stream_with_logging()
            
        # Handle non-streaming response
        result = model_object.invoke(query)
        if hasattr(result, "content"):
            response_text = result.content
        else:
            response_text = str(result)
        
        # Log the completion
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
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
        
        return response_text
            
    except ValueError as ve:
        # Log the error
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        log_llm_request(
            query=data.get("query", ""),
            response=f"Error: {str(ve)}",
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
        
        raise ValueError(str(ve))
    except Exception as e:
        # Log the error
        end_time = datetime.now()
        processing_time = time.time() - start_timestamp
        
        log_llm_request(
            query=data.get("query", ""),
            response=f"Error: {str(e)}",
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
        
        raise RuntimeError(f"Internal server error: {str(e)}")


def generate_completion_with_schema(
    elements: PredictSchema,
    project_name: str = "katonic-sdk",
    project_type: str = "llm-query",
    product_type: str = "katonic-sdk",
    enable_logging: bool = True
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Generate completion using LLM models with PredictSchema and platform logging.
    
    Args:
        elements: PredictSchema object containing model_id, data, and user
        project_name: Project name for logging
        project_type: Type of project for logging
        product_type: Product type for logging
        enable_logging: Enable/disable platform logging
        
    Returns:
        Union[str, AsyncGenerator[str, None]]: Either a string response or async generator for streaming
    """
    return generate_completion(
        elements.model_id, 
        elements.data, 
        elements.user,
        project_name=project_name,
        project_type=project_type,
        product_type=product_type,
        enable_logging=enable_logging
    )