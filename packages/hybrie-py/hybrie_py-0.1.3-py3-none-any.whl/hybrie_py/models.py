"""
HybrIE Python SDK Data Models

Type-safe Python models for HybrIE API requests and responses.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from .proto import hybrie_sdk_pb2, hybrie_llm_pb2


@dataclass
class ProgressUpdate:
    """Progress update during image generation."""
    
    percentage: float
    stage: str
    message: str
    eta_seconds: Optional[float] = None

    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.ProgressUpdate) -> "ProgressUpdate":
        """Create from protobuf message."""
        return cls(
            percentage=proto.percentage,
            stage=proto.stage,
            message=proto.message,
            eta_seconds=proto.eta_seconds if proto.HasField("eta_seconds") else None,
        )


@dataclass
class GenerationMetadata:
    """Metadata about the generation process."""
    
    model_used: str
    device_used: str
    total_time_seconds: float
    memory_peak_gb: float
    actual_steps: int
    timing_breakdown: Dict[str, float]
    seed_used: int

    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.GenerationMetadata) -> "GenerationMetadata":
        """Create from protobuf message."""
        return cls(
            model_used=proto.model_used,
            device_used=proto.device_used,
            total_time_seconds=proto.total_time_seconds,
            memory_peak_gb=proto.memory_peak_gb,
            actual_steps=proto.actual_steps,
            timing_breakdown=dict(proto.timing_breakdown),
            seed_used=proto.seed_used,
        )


@dataclass
class ImageResult:
    """Final image generation result."""
    
    image_data: bytes
    image_path: Optional[str]
    metadata: Optional[GenerationMetadata]
    request_id: str

    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.ImageResult) -> "ImageResult":
        """Create from protobuf message."""
        metadata = None
        if proto.HasField("metadata"):
            metadata = GenerationMetadata.from_proto(proto.metadata)
        
        return cls(
            image_data=proto.image_data,
            image_path=proto.image_path if proto.HasField("image_path") else None,
            metadata=metadata,
            request_id=proto.request_id,
        )


@dataclass
class ErrorResponse:
    """Error response from server."""
    
    code: str
    message: str
    details: Optional[str] = None
    request_id: Optional[str] = None

    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.ErrorResponse) -> "ErrorResponse":
        """Create from protobuf message."""
        return cls(
            code=proto.code,
            message=proto.message,
            details=proto.details if proto.HasField("details") else None,
            request_id=proto.request_id if proto.HasField("request_id") else None,
        )


@dataclass
class GenerateResponse:
    """
    Response from generate request - can contain progress, result, or error.
    
    Only one field will be set per response.
    """
    
    progress: Optional[ProgressUpdate] = None
    result: Optional[ImageResult] = None
    error: Optional[ErrorResponse] = None

    @classmethod
    def from_proto_progress(cls, proto: hybrie_sdk_pb2.ProgressUpdate) -> "GenerateResponse":
        """Create response with progress update."""
        return cls(progress=ProgressUpdate.from_proto(proto))

    @classmethod
    def from_proto_result(cls, proto: hybrie_sdk_pb2.ImageResult) -> "GenerateResponse":
        """Create response with result."""
        return cls(result=ImageResult.from_proto(proto))

    @classmethod
    def from_proto_error(cls, proto: hybrie_sdk_pb2.ErrorResponse) -> "GenerateResponse":
        """Create response with error."""
        return cls(error=ErrorResponse.from_proto(proto))


@dataclass
class ModelInfo:
    """Information about an available model."""
    
    id: str
    name: str
    type: str
    variant: str
    is_loaded: bool
    size_gb: Optional[float]
    description: Optional[str]
    supported_sizes: List[str]
    recommended_steps: Optional[int]

    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.ModelInfo) -> "ModelInfo":
        """Create from protobuf message."""
        return cls(
            id=proto.id,
            name=proto.name,
            type=proto.type,
            variant=proto.variant,
            is_loaded=proto.is_loaded,
            size_gb=proto.size_gb if proto.size_gb > 0 else None,
            description=proto.description if proto.description else None,
            supported_sizes=list(proto.supported_sizes),
            recommended_steps=proto.recommended_steps if proto.recommended_steps > 0 else None,
        )


@dataclass
class DeviceInfo:
    """Information about available hardware devices."""
    
    name: str
    type: str
    memory_gb: float
    available: bool

    @classmethod
    def from_proto(cls, proto: Any) -> "DeviceInfo":
        """Create from protobuf message."""
        # TODO: Update when DeviceInfo is added to proto
        return cls(
            name="Unknown",
            type="Unknown", 
            memory_gb=0.0,
            available=False,
        )


@dataclass
class SystemInfo:
    """Server system information."""
    
    version: str
    devices: List[DeviceInfo]
    
    @classmethod
    def from_proto(cls, proto: hybrie_sdk_pb2.SystemInfoResponse) -> "SystemInfo":
        """Create from protobuf message."""
        return cls(
            version=proto.version,
            devices=[],  # TODO: Update when devices are added to proto
        )


@dataclass
class GenerateRequest:
    """
    Request for image generation.
    
    This is a convenience class for building requests programmatically.
    """
    
    prompt: str
    model: str = "flux-1-schnell"
    width: int = 1024
    height: int = 1024
    steps: int = 4
    seed: Optional[int] = None
    negative_prompt: Optional[str] = None
    guidance_scale: float = 7.5
    conditioning_image_path: Optional[Union[str, Path]] = None
    strength: float = 0.7
    advanced_params: Optional[Dict[str, str]] = None

    def validate(self) -> None:
        """Validate request parameters."""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if self.width % 64 != 0 or self.height % 64 != 0:
            raise ValueError("Width and height must be multiples of 64")
        if not (64 <= self.width <= 2048 and 64 <= self.height <= 2048):
            raise ValueError("Width and height must be between 64 and 2048")
        if not (1 <= self.steps <= 100):
            raise ValueError("Steps must be between 1 and 100")
        if not (1.0 <= self.guidance_scale <= 20.0):
            raise ValueError("Guidance scale must be between 1.0 and 20.0")
        if not (0.0 <= self.strength <= 1.0):
            raise ValueError("Strength must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "prompt": self.prompt,
            "model": self.model,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "guidance_scale": self.guidance_scale,
            "strength": self.strength,
        }
        
        if self.seed is not None:
            data["seed"] = self.seed
        if self.negative_prompt:
            data["negative_prompt"] = self.negative_prompt
        if self.conditioning_image_path:
            data["conditioning_image_path"] = str(self.conditioning_image_path)
        if self.advanced_params:
            data["advanced_params"] = self.advanced_params
            
        return data


# ============================================================================
# LLM Chat Models
# ============================================================================

@dataclass
class ChatMessage:
    """A single message in a chat conversation."""

    role: str  # "system", "user", "assistant"
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ChatMessage":
        """Create from dictionary."""
        return cls(role=data["role"], content=data["content"])


@dataclass
class SamplingParams:
    """Parameters for LLM text generation."""

    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = -1
    repetition_penalty: float = 1.0
    stop_tokens: Optional[List[str]] = None
    thinking_mode: str = "auto"  # "auto", "force", "disable"

    def to_proto(self) -> hybrie_llm_pb2.SamplingParams:
        """Convert to protobuf message."""
        params = hybrie_llm_pb2.SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
        )

        if self.thinking_mode == "force":
            params.thinking_mode = hybrie_llm_pb2.ThinkingMode.FORCE
        elif self.thinking_mode == "disable":
            params.thinking_mode = hybrie_llm_pb2.ThinkingMode.DISABLE
        else:
            params.thinking_mode = hybrie_llm_pb2.ThinkingMode.AUTO

        return params


@dataclass
class ChatChunk:
    """A chunk of streaming chat response."""

    token_id: int
    text: str
    finish_reason: Optional[str] = None

    @classmethod
    def from_proto(cls, proto: hybrie_llm_pb2.GenerateChunk) -> "ChatChunk":
        """Create from protobuf message."""
        return cls(
            token_id=proto.token_id,
            text=proto.text,
        )


@dataclass
class ChatResponse:
    """Response from chat request - can contain chunk or completion."""

    chunk: Optional[ChatChunk] = None
    complete: bool = False
    finish_reason: Optional[str] = None
    session_id: Optional[str] = None

    @classmethod
    def from_proto_chunk(cls, proto: hybrie_llm_pb2.GenerateChunk, session_id: str) -> "ChatResponse":
        """Create response with text chunk."""
        return cls(
            chunk=ChatChunk.from_proto(proto),
            session_id=session_id
        )

    @classmethod
    def completion(cls, session_id: str, finish_reason: str = "stop") -> "ChatResponse":
        """Create completion response."""
        return cls(
            complete=True,
            finish_reason=finish_reason,
            session_id=session_id
        )

    @property
    def text(self) -> Optional[str]:
        """Get text from chunk if available."""
        return self.chunk.text if self.chunk else None


@dataclass
class CompletionRequest:
    """Request for text completion."""

    prompt: str
    model: str = "qwen3-4b"
    max_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = -1
    repetition_penalty: float = 1.0
    stop_tokens: Optional[List[str]] = None
    stream: bool = True
    thinking_mode: str = "auto"

    def get_sampling_params(self) -> SamplingParams:
        """Get sampling parameters."""
        return SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            stop_tokens=self.stop_tokens,
            thinking_mode=self.thinking_mode,
        )


@dataclass
class ChatRequest:
    """Request for chat conversation."""

    messages: List[ChatMessage]
    model: str = "qwen3-4b"
    max_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = -1
    repetition_penalty: float = 1.0
    stop_tokens: Optional[List[str]] = None
    stream: bool = True
    thinking_mode: str = "auto"

    def get_sampling_params(self) -> SamplingParams:
        """Get sampling parameters."""
        return SamplingParams(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            stop_tokens=self.stop_tokens,
            thinking_mode=self.thinking_mode,
        )