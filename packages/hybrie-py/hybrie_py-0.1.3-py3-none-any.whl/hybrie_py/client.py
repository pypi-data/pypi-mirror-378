"""
HybrIE Python Client

Async gRPC client for HybrIE server with streaming support.
"""

import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, Optional, Union, Dict, Any, List
from contextlib import asynccontextmanager

import grpc
from grpc import aio
from PIL import Image
import aiofiles

from .proto import hybrie_sdk_pb2, hybrie_sdk_pb2_grpc, hybrie_llm_pb2, hybrie_llm_pb2_grpc
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
    ConnectionError as HybrieConnectionError,
    ModelNotFoundError,
    GenerationError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class HybrieClient:
    """
    Async client for HybrIE server.
    
    Provides streaming image generation with real-time progress updates,
    model management, and system information.
    
    Example:
        >>> async with HybrieClient("localhost:9090") as client:
        ...     async for update in client.generate("A beautiful sunset"):
        ...         if update.progress:
        ...             print(f"Progress: {update.progress.percentage:.1f}%")
        ...         elif update.result:
        ...             print(f"Generated: {update.result.image_path}")
        ...             break
    """

    def __init__(
        self,
        server_url: str,
        *,
        timeout: float = 300.0,
        max_message_length: int = 100 * 1024 * 1024,  # 100MB
        compression: Optional[grpc.Compression] = grpc.Compression.Gzip,
    ):
        """
        Initialize HybrIE client.

        Args:
            server_url: HybrIE server address (e.g., "localhost:9090")
            timeout: Default timeout for requests in seconds
            max_message_length: Maximum gRPC message size
            compression: gRPC compression method
        """
        self.server_url = server_url
        self.timeout = timeout
        self.compression = compression
        
        # gRPC channel options
        self.channel_options = [
            ("grpc.max_receive_message_length", max_message_length),
            ("grpc.max_send_message_length", max_message_length),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
        ]
        
        self._channel: Optional[aio.Channel] = None
        self._stub: Optional[hybrie_sdk_pb2_grpc.HybrieSdkServiceStub] = None
        self._llm_stub: Optional[hybrie_llm_pb2_grpc.HybrieLLMServiceStub] = None

    async def __aenter__(self) -> "HybrieClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Establish connection to HybrIE server."""
        if self._channel is not None:
            return

        try:
            self._channel = aio.insecure_channel(
                self.server_url,
                options=self.channel_options,
                compression=self.compression,
            )
            self._stub = hybrie_sdk_pb2_grpc.HybrieSdkServiceStub(self._channel)
            self._llm_stub = hybrie_llm_pb2_grpc.HybrieLLMServiceStub(self._channel)
            
            # Test connection
            await self.health_check()
            logger.info(f"Connected to HybrIE server at {self.server_url}")
            
        except Exception as e:
            await self.close()
            raise HybrieConnectionError(
                f"Failed to connect to HybrIE server at {self.server_url}: {e}"
            ) from e

    async def close(self) -> None:
        """Close connection to HybrIE server."""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None
            self._llm_stub = None
            logger.info("Disconnected from HybrIE server")

    def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if self._stub is None:
            raise HybrieConnectionError(
                "Client not connected. Use 'await client.connect()' or async context manager."
            )

    async def generate(
        self,
        prompt: str,
        *,
        model: str = "flux-1-schnell",
        width: int = 1024,
        height: int = 1024,
        steps: int = 4,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        guidance_scale: float = 7.5,
        conditioning_image: Optional[Union[str, Path, bytes]] = None,
        strength: float = 0.7,
        advanced_params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[GenerateResponse]:
        """
        Generate images from text prompts with streaming progress.

        Args:
            prompt: Text description of the image to generate
            model: Model to use ("flux-1-dev", "flux-1-schnell", "flux-1-kontext-dev")
            width: Image width in pixels
            height: Image height in pixels
            steps: Number of inference steps
            seed: Random seed for reproducibility
            negative_prompt: What to avoid in the generated image
            guidance_scale: Guidance strength (1.0-20.0)
            conditioning_image: Image for Kontext models (path, bytes, or PIL Image)
            strength: Image-to-image strength (0.0-1.0)
            advanced_params: Additional model-specific parameters
            timeout: Request timeout in seconds

        Yields:
            GenerateResponse: Progress updates and final result

        Raises:
            ValidationError: Invalid parameters
            ModelNotFoundError: Model not available
            GenerationError: Generation failed
        """
        self._ensure_connected()
        
        # Validate parameters
        if not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        if width % 64 != 0 or height % 64 != 0:
            raise ValidationError("Width and height must be multiples of 64")
        if not (64 <= width <= 2048 and 64 <= height <= 2048):
            raise ValidationError("Width and height must be between 64 and 2048")
        if not (1 <= steps <= 100):
            raise ValidationError("Steps must be between 1 and 100")
        if not (1.0 <= guidance_scale <= 20.0):
            raise ValidationError("Guidance scale must be between 1.0 and 20.0")

        # Handle conditioning image
        conditioning_image_data = None
        if conditioning_image is not None:
            conditioning_image_data = await self._process_conditioning_image(
                conditioning_image
            )

        # Build request
        request = hybrie_sdk_pb2.GenerateRequest(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
        )
        
        if seed is not None:
            request.seed = seed
        if negative_prompt:
            request.negative_prompt = negative_prompt
        if conditioning_image_data:
            request.conditioning_image = conditioning_image_data
            request.strength = strength
        if advanced_params:
            request.advanced_params.update(advanced_params)

        # Make streaming request
        timeout_val = timeout or self.timeout
        try:
            response_stream = self._stub.Generate(
                request, timeout=timeout_val, compression=self.compression
            )
            
            async for response in response_stream:
                if response.HasField("progress"):
                    yield GenerateResponse.from_proto_progress(response.progress)
                elif response.HasField("result"):
                    yield GenerateResponse.from_proto_result(response.result)
                elif response.HasField("error"):
                    error = ErrorResponse.from_proto(response.error)
                    if error.code == "MODEL_NOT_LOADED":
                        raise ModelNotFoundError(error.message)
                    else:
                        raise GenerationError(error.message)
                        
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise ModelNotFoundError(f"Model '{model}' not found")
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise ValidationError(e.details())
            else:
                raise GenerationError(f"Generation failed: {e.details()}") from e

    async def list_models(self, timeout: Optional[float] = None) -> List[ModelInfo]:
        """
        List available models.

        Args:
            timeout: Request timeout in seconds

        Returns:
            List of available models with metadata

        Raises:
            ConnectionError: Server connection failed
        """
        self._ensure_connected()
        
        timeout_val = timeout or self.timeout
        try:
            request = hybrie_sdk_pb2.ListModelsRequest()
            response = await self._stub.ListModels(
                request, timeout=timeout_val, compression=self.compression
            )
            
            return [ModelInfo.from_proto(model) for model in response.models]
            
        except grpc.RpcError as e:
            raise HybrieConnectionError(f"Failed to list models: {e.details()}") from e

    async def load_model(
        self, model_id: str, timeout: Optional[float] = None
    ) -> bool:
        """
        Load a model into server memory.

        Args:
            model_id: Model identifier to load
            timeout: Request timeout in seconds

        Returns:
            True if model loaded successfully

        Raises:
            ModelNotFoundError: Model not found
            ConnectionError: Server connection failed
        """
        self._ensure_connected()
        
        timeout_val = timeout or self.timeout
        try:
            request = hybrie_sdk_pb2.LoadModelRequest(model_id=model_id)
            response = await self._stub.LoadModel(
                request, timeout=timeout_val, compression=self.compression
            )
            
            if not response.success:
                if "not found" in response.error_message.lower():
                    raise ModelNotFoundError(response.error_message)
                else:
                    raise GenerationError(response.error_message)
            
            return response.success
            
        except grpc.RpcError as e:
            raise HybrieConnectionError(f"Failed to load model: {e.details()}") from e

    async def unload_model(
        self, model_id: str, timeout: Optional[float] = None
    ) -> bool:
        """
        Unload a model from server memory.

        Args:
            model_id: Model identifier to unload
            timeout: Request timeout in seconds

        Returns:
            True if model unloaded successfully

        Raises:
            ModelNotFoundError: Model not loaded
            ConnectionError: Server connection failed
        """
        self._ensure_connected()
        
        timeout_val = timeout or self.timeout
        try:
            request = hybrie_sdk_pb2.UnloadModelRequest(model_id=model_id)
            response = await self._stub.UnloadModel(
                request, timeout=timeout_val, compression=self.compression
            )
            
            if not response.success:
                if "not loaded" in response.error_message.lower():
                    raise ModelNotFoundError(response.error_message)
                else:
                    raise GenerationError(response.error_message)
            
            return response.success
            
        except grpc.RpcError as e:
            raise HybrieConnectionError(f"Failed to unload model: {e.details()}") from e

    async def get_system_info(self, timeout: Optional[float] = None) -> SystemInfo:
        """
        Get server system information.

        Args:
            timeout: Request timeout in seconds

        Returns:
            System information including version, capabilities, devices

        Raises:
            ConnectionError: Server connection failed
        """
        self._ensure_connected()
        
        timeout_val = timeout or self.timeout
        try:
            request = hybrie_sdk_pb2.SystemInfoRequest()
            response = await self._stub.GetSystemInfo(
                request, timeout=timeout_val, compression=self.compression
            )
            
            return SystemInfo.from_proto(response)
            
        except grpc.RpcError as e:
            raise HybrieConnectionError(f"Failed to get system info: {e.details()}") from e

    async def health_check(self, timeout: Optional[float] = None) -> bool:
        """
        Check server health.

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if server is healthy

        Raises:
            ConnectionError: Server not healthy
        """
        self._ensure_connected()
        
        timeout_val = timeout or 10.0  # Short timeout for health check
        try:
            request = hybrie_sdk_pb2.HealthCheckRequest()
            response = await self._stub.HealthCheck(
                request, timeout=timeout_val, compression=self.compression
            )
            
            return response.status == "SERVING"
            
        except grpc.RpcError as e:
            raise HybrieConnectionError(f"Health check failed: {e.details()}") from e

    async def save_image(
        self, 
        image_data: bytes, 
        output_path: Union[str, Path],
        *,
        format: str = "PNG"
    ) -> None:
        """
        Save image data to file.

        Args:
            image_data: Raw image bytes
            output_path: Where to save the image
            format: Image format (PNG, JPEG, etc.)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(image_data)
        
        logger.info(f"Image saved to {output_path}")

    async def chat(
        self,
        messages: List[Union[ChatMessage, Dict[str, str]]],
        *,
        model: str = "qwen3-4b",
        max_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = -1,
        repetition_penalty: float = 1.0,
        stop_tokens: Optional[List[str]] = None,
        stream: bool = True,
        thinking_mode: str = "auto",
        timeout: Optional[float] = None,
    ) -> AsyncIterator[ChatResponse]:
        """
        Chat with LLM models with streaming responses.

        Args:
            messages: Conversation history as ChatMessage objects or dicts
            model: LLM model to use ("qwen3-4b", etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling (-1 to disable)
            repetition_penalty: Repetition penalty (1.0 = no penalty)
            stop_tokens: List of stop token strings
            stream: Whether to stream responses
            thinking_mode: Thinking mode ("auto", "force", "disable")
            timeout: Request timeout in seconds

        Yields:
            ChatResponse: Streaming text chunks and completion info

        Raises:
            ValidationError: Invalid parameters
            ModelNotFoundError: Model not available
            GenerationError: Generation failed
        """
        self._ensure_connected()

        # Convert messages to ChatMessage objects if needed
        chat_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                chat_messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
            else:
                chat_messages.append(msg)

        # Build conversation prompt (simple implementation)
        conversation_parts = []
        for msg in chat_messages:
            if msg.role == "system":
                conversation_parts.append(f"<|system|>\n{msg.content}\n")
            elif msg.role == "user":
                conversation_parts.append(f"<|user|>\n{msg.content}\n")
            elif msg.role == "assistant":
                conversation_parts.append(f"<|assistant|>\n{msg.content}\n")

        conversation_parts.append("<|assistant|>\n")
        conversation_prompt = "".join(conversation_parts)

        # Use completion method internally
        async for response in self.complete(
            prompt=conversation_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            stop_tokens=stop_tokens,
            stream=stream,
            thinking_mode=thinking_mode,
            timeout=timeout,
        ):
            yield response

    async def complete(
        self,
        prompt: str,
        *,
        model: str = "qwen3-4b",
        max_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = -1,
        repetition_penalty: float = 1.0,
        stop_tokens: Optional[List[str]] = None,
        stream: bool = True,
        thinking_mode: str = "auto",
        timeout: Optional[float] = None,
    ) -> AsyncIterator[ChatResponse]:
        """
        Generate text completion with streaming responses.

        Args:
            prompt: Text prompt to complete
            model: LLM model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling (-1 to disable)
            repetition_penalty: Repetition penalty (1.0 = no penalty)
            stop_tokens: List of stop token strings
            stream: Whether to stream responses
            thinking_mode: Thinking mode ("auto", "force", "disable")
            timeout: Request timeout in seconds

        Yields:
            ChatResponse: Streaming text chunks and completion info

        Raises:
            ValidationError: Invalid parameters
            ModelNotFoundError: Model not available
            GenerationError: Generation failed
        """
        self._ensure_connected()

        if not self._llm_stub:
            raise HybrieConnectionError("LLM service not available")

        # Validate parameters
        if not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        if not (0.0 <= temperature <= 2.0):
            raise ValidationError("Temperature must be between 0.0 and 2.0")
        if not (0.0 <= top_p <= 1.0):
            raise ValidationError("Top-p must be between 0.0 and 1.0")
        if not (1 <= max_tokens <= 4096):
            raise ValidationError("Max tokens must be between 1 and 4096")

        # Create sampling parameters
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            stop_tokens=stop_tokens,
            thinking_mode=thinking_mode,
        )

        timeout_val = timeout or self.timeout

        try:
            # For now, use a simple tokenization approach
            # In a real implementation, you'd use proper tokenization
            input_tokens = [1] + [hash(prompt) % 32000 for _ in range(min(len(prompt.split()), 100))]

            # Step 1: Prefill
            prefill_request = hybrie_llm_pb2.PrefillRequest(
                model_id=model,
                input_ids=input_tokens,
                seed=42,  # Could be parameterized
                sampling=sampling_params.to_proto(),
            )

            prefill_response = await self._llm_stub.Prefill(
                prefill_request, timeout=timeout_val, compression=self.compression
            )

            session_id = prefill_response.session_id

            # Step 2: Generate streaming response
            generate_request = hybrie_llm_pb2.GenerateRequest(
                session_id=session_id,
                max_new_tokens=max_tokens,
                sampling=sampling_params.to_proto(),
            )

            response_stream = self._llm_stub.StreamGenerate(
                generate_request, timeout=timeout_val, compression=self.compression
            )

            async for chunk in response_stream:
                yield ChatResponse.from_proto_chunk(chunk, session_id)

            # Signal completion
            yield ChatResponse.completion(session_id, "stop")

            # Step 3: Release session
            release_request = hybrie_llm_pb2.ReleaseRequest(session_id=session_id)
            await self._llm_stub.ReleaseSession(
                release_request, timeout=timeout_val, compression=self.compression
            )

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise ModelNotFoundError(f"Model '{model}' not found")
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise ValidationError(e.details())
            else:
                raise GenerationError(f"Generation failed: {e.details()}") from e

    async def _process_conditioning_image(
        self, conditioning_image: Union[str, Path, bytes]
    ) -> bytes:
        """Process conditioning image for Kontext models."""
        if isinstance(conditioning_image, bytes):
            return conditioning_image
        
        elif isinstance(conditioning_image, (str, Path)):
            path = Path(conditioning_image)
            if not path.exists():
                raise ValidationError(f"Conditioning image not found: {path}")
            
            async with aiofiles.open(path, "rb") as f:
                return await f.read()
        
        else:
            raise ValidationError(
                "Conditioning image must be file path or bytes"
            )


@asynccontextmanager
async def create_client(server_url: str, **kwargs) -> AsyncIterator[HybrieClient]:
    """
    Async context manager for HybrIE client.
    
    Args:
        server_url: HybrIE server address
        **kwargs: Additional client options
    
    Example:
        >>> async with create_client("localhost:9090") as client:
        ...     models = await client.list_models()
    """
    client = HybrieClient(server_url, **kwargs)
    try:
        await client.connect()
        yield client
    finally:
        await client.close()