import os
import json
import time
from typing import Dict, List, Optional, Union, Any, Iterator
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .types import (
    ChatMessage, ChatCompletion, ChatCompletionChunk, ChatChoice, Usage,
    StreamChoice, StreamDelta, Image, ImagesResponse, Embedding, EmbeddingsResponse, 
    Transcription, APIError, AuthenticationError, RateLimitError, MessageParam
)


class A4F:
    """A4F Python SDK — your unified AI gateway."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        Initialize A4F client
        
        Args:
            api_key: API key (defaults to A4F_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key or os.getenv("A4F_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key is required. Set A4F_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.a4f.co/v1"
        self.timeout = timeout
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Resources
        self.chat = ChatResource(self)
        self.images = ImagesResource(self)
        self.embeddings = EmbeddingsResource(self)
        self.audio = AudioResource(self)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], Iterator[str]]:
        """Make HTTP request to API"""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "python-sdk/v1.0.5",
        }
        
        if not files:
            headers["Content-Type"] = "application/json"
        
        try:
            if stream:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    files=files,
                    timeout=self.timeout,
                    stream=True,
                )
                response.raise_for_status()
                return self._handle_stream_response(response)
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    files=files,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def _handle_http_error(self, error: requests.exceptions.HTTPError):
        """Handle HTTP errors and convert to appropriate exceptions"""
        response = error.response
        status_code = response.status_code
        
        try:
            error_data = response.json()
            message = error_data.get("error", {}).get("message", str(error))
        except:
            message = str(error)
        
        if status_code == 401:
            raise AuthenticationError(message, status_code)
        elif status_code == 429:
            raise RateLimitError(message, status_code)
        else:
            raise APIError(message, status_code)
    
    def _handle_stream_response(self, response) -> Iterator[str]:
        """Handle streaming response"""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                line = line.strip()
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data.strip() == '[DONE]':
                        break
                    if data.strip():  # Only yield non-empty data
                        yield data
                elif line.startswith('data:'):
                    data = line[5:]  # Remove 'data:' prefix (no space)
                    if data.strip() == '[DONE]':
                        break
                    if data.strip():  # Only yield non-empty data
                        yield data


class ChatResource:
    """Chat completions resource - Enhanced for easy use"""
    
    def __init__(self, client: A4F):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[MessageParam],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """
        Create a chat completion
        
        Args:
            model: Model to use
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters
        """
        # Convert ChatMessage objects to dicts
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    **({"name": msg.name} if msg.name else {})
                })
            else:
                formatted_messages.append(msg)
        
        data = {
            "model": model,
            "messages": formatted_messages,
            **kwargs
        }
        
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if stream:
            data["stream"] = True
        
        if stream:
            response_stream = self.client._make_request("POST", "/chat/completions", data, stream=True)
            return self._parse_stream_response(response_stream)
        else:
            response = self.client._make_request("POST", "/chat/completions", data)
            return self._parse_completion_response(response)
    
    def _parse_completion_response(self, data: Dict[str, Any]) -> ChatCompletion:
        """Parse non-streaming completion response - No .get() calls!"""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})
            message = ChatMessage(
                role=message_data.get("role", "assistant"),
                content=message_data.get("content", ""),
                name=message_data.get("name")
            )
            choice = ChatChoice(
                index=choice_data.get("index", 0),
                message=message,
                finish_reason=choice_data.get("finish_reason")
            )
            choices.append(choice)
        
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        ) if usage_data else None
        
        return ChatCompletion(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", int(time.time())),
            model=data.get("model", ""),
            choices=choices,
            usage=usage
        )
    
    def _parse_stream_response(self, stream: Iterator[str]) -> Iterator[ChatCompletionChunk]:
        """Parse streaming completion response - Enhanced for easy use!"""
        for chunk_data in stream:
            try:
                chunk_json = json.loads(chunk_data)
                
                # Parse choices with enhanced StreamChoice objects
                choices = []
                for choice_data in chunk_json.get("choices", []):
                    delta_data = choice_data.get("delta", {})
                    delta = StreamDelta(
                        role=delta_data.get("role"),
                        content=delta_data.get("content")
                    )
                    choice = StreamChoice(
                        index=choice_data.get("index", 0),
                        delta=delta,
                        finish_reason=choice_data.get("finish_reason")
                    )
                    choices.append(choice)
                
                yield ChatCompletionChunk(
                    id=chunk_json.get("id", ""),
                    object=chunk_json.get("object", "chat.completion.chunk"),
                    created=chunk_json.get("created", int(time.time())),
                    model=chunk_json.get("model", ""),
                    choices=choices
                )
            except json.JSONDecodeError:
                continue


class ImagesResource:
    """Images generation resource - Enhanced for easy use"""
    
    def __init__(self, client: A4F):
        self.client = client
    
    def generate(
        self,
        prompt: str,
        model: str = "dall-e-3",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        response_format: str = "url",
        **kwargs
    ) -> ImagesResponse:
        """
        Generate images from text prompt
        
        Args:
            prompt: Text description of the desired image
            model: Model to use
            n: Number of images to generate
            size: Size of generated images
            quality: Quality of generated images
            response_format: Format of response ("url" or "b64_json")
            **kwargs: Additional parameters
        """
        data = {
            "prompt": prompt,
            "model": model,
            "n": n,
            "size": size,
            "quality": quality,
            "response_format": response_format,
            **kwargs
        }
        
        response = self.client._make_request("POST", "/images/generations", data)
        return self._parse_images_response(response)
    
    def _parse_images_response(self, data: Dict[str, Any]) -> ImagesResponse:
        """Parse images response - Enhanced for easy use!"""
        images = []
        for img_data in data.get("data", []):
            image = Image(
                url=img_data.get("url"),
                b64_json=img_data.get("b64_json"),
                revised_prompt=img_data.get("revised_prompt")
            )
            images.append(image)
        
        return ImagesResponse(
            created=data.get("created", int(time.time())),
            data=images
        )


class EmbeddingsResource:
    """Text embeddings resource - Enhanced for easy use"""
    
    def __init__(self, client: A4F):
        self.client = client
    
    def create(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> EmbeddingsResponse:
        """
        Create embeddings for input text
        
        Args:
            input: Text or list of texts to embed
            model: Model to use
            **kwargs: Additional parameters
        """
        data = {
            "input": input,
            "model": model,
            **kwargs
        }
        
        response = self.client._make_request("POST", "/embeddings", data)
        return self._parse_embeddings_response(response)
    
    def _parse_embeddings_response(self, data: Dict[str, Any]) -> EmbeddingsResponse:
        """Parse embeddings response - Enhanced for easy use!"""
        embeddings = []
        for emb_data in data.get("data", []):
            embedding = Embedding(
                object=emb_data.get("object", "embedding"),
                embedding=emb_data.get("embedding", []),
                index=emb_data.get("index", 0)
            )
            embeddings.append(embedding)
        
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        return EmbeddingsResponse(
            object=data.get("object", "list"),
            data=embeddings,
            model=data.get("model", ""),
            usage=usage
        )


class AudioResource:
    """Audio processing resource - Enhanced for easy use"""
    
    def __init__(self, client: A4F):
        self.client = client
    
    def transcribe(
        self,
        file: Union[str, bytes],
        model: str = "whisper-1",
        language: Optional[str] = None,
        response_format: str = "json",
        **kwargs
    ) -> Transcription:
        """
        Transcribe audio to text
        
        Args:
            file: Audio file path or bytes
            model: Model to use
            language: Language of the audio
            response_format: Format of response
            **kwargs: Additional parameters
        """
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file_data = f.read()
            filename = os.path.basename(file)
        else:
            file_data = file
            filename = "audio.wav"
        
        files = {
            "file": (filename, file_data, "audio/wav")
        }
        
        data = {
            "model": model,
            "response_format": response_format,
            **kwargs
        }
        
        if language:
            data["language"] = language
        
        response = self.client._make_request("POST", "/audio/transcriptions", data, files=files)
        return self._parse_transcription_response(response)
    
    def _parse_transcription_response(self, data: Dict[str, Any]) -> Transcription:
        """Parse transcription response - Enhanced for easy use!"""
        return Transcription(
            text=data.get("text", ""),
            language=data.get("language"),
            duration=data.get("duration"),
            segments=data.get("segments")
        )


# Alias for backwards compatibility
Client = A4F