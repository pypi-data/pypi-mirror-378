from typing import Dict, List, Optional, Union, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime


# Base Exception Classes
class A4FError(Exception):
    """Base exception for all A4F errors"""
    pass


class APIError(A4FError):
    """API related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication failed"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass


@dataclass
class ChatMessage:
    """A chat message with easy access"""
    role: Literal["system", "user", "assistant", "developer"]
    content: str
    name: Optional[str] = None
    
    def __str__(self) -> str:
        return self.content
    
    @property
    def text(self) -> str:
        """Alias for content"""
        return self.content


@dataclass
class StreamDelta:
    """Streaming delta with direct access"""
    role: Optional[str] = None
    content: Optional[str] = None
    
    def __str__(self) -> str:
        return self.content or ""
    
    @property
    def text(self) -> str:
        """Get content text directly"""
        return self.content or ""
    
    @property
    def has_content(self) -> bool:
        """Check if delta has content"""
        return bool(self.content)


@dataclass
class StreamChoice:
    """Streaming choice with easy access"""
    index: int = 0
    delta: StreamDelta = field(default_factory=StreamDelta)
    finish_reason: Optional[str] = None
    
    @property
    def content(self) -> str:
        """Get content directly"""
        return self.delta.content or ""
    
    @property
    def text(self) -> str:
        """Alias for content"""
        return self.content
    
    @property
    def has_content(self) -> bool:
        """Check if choice has content"""
        return self.delta.has_content


@dataclass
class ChatChoice:
    """A chat completion choice with easy access"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None
    
    @property
    def content(self) -> str:
        """Get message content directly"""
        return self.message.content
    
    @property
    def text(self) -> str:
        """Alias for content"""
        return self.content
    
    def __str__(self) -> str:
        return self.content


@dataclass
class Usage:
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    def __str__(self) -> str:
        return f"{self.total_tokens} tokens ({self.prompt_tokens} prompt + {self.completion_tokens} completion)"


@dataclass
class ChatCompletion:
    """Chat completion response with easy access"""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[Usage] = None
    
    @property
    def content(self) -> str:
        """Get first choice content directly"""
        return self.choices[0].content if self.choices else ""
    
    @property
    def text(self) -> str:
        """Alias for content"""
        return self.content
    
    @property
    def message(self) -> ChatMessage:
        """Get first choice message directly"""
        return self.choices[0].message if self.choices else ChatMessage(role="assistant", content="")
    
    def __str__(self) -> str:
        return self.content


@dataclass
class ChatCompletionChunk:
    """Streaming chat completion chunk with easy access"""
    id: str
    object: str
    created: int
    model: str
    choices: List[StreamChoice] = field(default_factory=list)
    
    @property
    def content(self) -> str:
        """Get first choice content directly"""
        return self.choices[0].content if self.choices else ""
    
    @property
    def text(self) -> str:
        """Alias for content"""
        return self.content
    
    @property
    def delta(self) -> StreamDelta:
        """Get first choice delta directly"""
        return self.choices[0].delta if self.choices else StreamDelta()
    
    @property
    def has_content(self) -> bool:
        """Check if chunk has content"""
        return bool(self.content)
    
    def __str__(self) -> str:
        return self.content


@dataclass
class Image:
    """Generated image with easy access"""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    
    @property
    def link(self) -> str:
        """Alias for url"""
        return self.url or ""
    
    @property
    def base64(self) -> str:
        """Alias for b64_json"""
        return self.b64_json or ""


@dataclass
class ImagesResponse:
    """Images generation response with easy access"""
    created: int
    data: List[Image]
    
    @property
    def images(self) -> List[Image]:
        """Alias for data"""
        return self.data
    
    @property
    def first_image(self) -> Image:
        """Get first image directly"""
        return self.data[0] if self.data else Image()
    
    @property
    def url(self) -> str:
        """Get first image URL directly"""
        return self.first_image.url or ""
    
    @property
    def urls(self) -> List[str]:
        """Get all image URLs"""
        return [img.url for img in self.data if img.url]


@dataclass
class Embedding:
    """Text embedding with easy access"""
    object: str
    embedding: List[float]
    index: int
    
    @property
    def vector(self) -> List[float]:
        """Alias for embedding"""
        return self.embedding
    
    @property
    def dimensions(self) -> int:
        """Get embedding dimensions"""
        return len(self.embedding)


@dataclass
class EmbeddingsResponse:
    """Embeddings response with easy access"""
    object: str
    data: List[Embedding]
    model: str
    usage: Usage
    
    @property
    def embeddings(self) -> List[Embedding]:
        """Alias for data"""
        return self.data
    
    @property
    def first_embedding(self) -> Embedding:
        """Get first embedding directly"""
        return self.data[0] if self.data else Embedding(object="embedding", embedding=[], index=0)
    
    @property
    def vector(self) -> List[float]:
        """Get first embedding vector directly"""
        return self.first_embedding.vector
    
    @property
    def vectors(self) -> List[List[float]]:
        """Get all embedding vectors"""
        return [emb.vector for emb in self.data]


@dataclass
class Transcription:
    """Audio transcription with easy access"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None
    
    @property
    def content(self) -> str:
        """Alias for text"""
        return self.text
    
    def __str__(self) -> str:
        return self.text


# Request parameter types
MessageParam = Union[Dict[str, Any], ChatMessage]