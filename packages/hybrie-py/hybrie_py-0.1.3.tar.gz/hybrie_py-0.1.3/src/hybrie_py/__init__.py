"""
HybrIE Python SDK

A Python client for HybrIE - Hybrid Inference Engine for FLUX image generation.
Provides async streaming support for real-time generation progress.
"""

from .client import HybrieClient
from .models import (
    GenerateRequest,
    GenerateResponse,
    ProgressUpdate,
    ImageResult,
    ErrorResponse,
    ModelInfo,
    SystemInfo,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatChunk,
    CompletionRequest,
    SamplingParams,
)
from .exceptions import (
    HybrieError,
    ConnectionError,
    ModelNotFoundError,
    GenerationError,
    ValidationError,
)

__version__ = "0.1.0"
__author__ = "HybrIE Team"
__license__ = "MIT OR Apache-2.0"

__all__ = [
    "HybrieClient",
    "GenerateRequest",
    "GenerateResponse",
    "ProgressUpdate",
    "ImageResult",
    "ErrorResponse",
    "ModelInfo",
    "SystemInfo",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatChunk",
    "CompletionRequest",
    "SamplingParams",
    "HybrieError",
    "ConnectionError",
    "ModelNotFoundError",
    "GenerationError",
    "ValidationError",
]