"""
Base LLM provider interface.

This module defines the abstract base class for all LLM providers,
ensuring a consistent interface across different AI services.
"""

import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ...exceptions.exceptions import ExternalServiceError, ValidationError
from ...logging.utils import get_logger


logger = get_logger(__name__)


class LLMProviderError(Exception):
    """Exception raised by LLM providers."""

    def __init__(
        self,
        message: str,
        provider: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code
        self.details = details or {}


class LLMProviderResponse(BaseModel):
    """Standardized LLM provider response."""

    id: UUID = Field(default_factory=uuid4)
    content: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    model: str
    provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class LLMProviderRequest(BaseModel):
    """Standardized LLM provider request."""

    messages: List[Dict[str, str]]
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    stream: bool = False
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement,
    ensuring consistency across different AI services.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for the provider
            base_url: Base URL for the provider API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Rate limiting
        self._request_times: List[datetime] = []
        self._token_usage: List[int] = []

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """Get list of supported models."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Get list of provider capabilities."""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMProviderResponse:
        """
        Generate a chat completion.

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM provider response

        Raises:
            LLMProviderError: If the request fails
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.

        Returns:
            List of available models with their information
        """
        pass

    @abstractmethod
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model: Model name

        Returns:
            Model information
        """
        pass

    async def validate_request(self, request: LLMProviderRequest) -> bool:
        """
        Validate a request before sending it.

        Args:
            request: Request to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If the request is invalid
        """
        if not request.messages:
            raise ValidationError("Messages cannot be empty")

        if not request.model:
            raise ValidationError("Model must be specified")

        if request.model not in self.supported_models:
            raise ValidationError(
                f"Model {request.model} is not supported by {self.provider_name}"
            )

        # Validate message format
        for message in request.messages:
            if not isinstance(message, dict):
                raise ValidationError("Each message must be a dictionary")
            if "role" not in message or "content" not in message:
                raise ValidationError(
                    "Each message must have 'role' and 'content' keys"
                )
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValidationError("Role must be 'system', 'user', or 'assistant'")

        # Validate parameters
        if not 0.0 <= request.temperature <= 2.0:
            raise ValidationError("Temperature must be between 0.0 and 2.0")

        if request.max_tokens < 1:
            raise ValidationError("Max tokens must be at least 1")

        return True

    async def check_rate_limit(self, estimated_tokens: int = 0) -> bool:
        """
        Check if the request would exceed rate limits.

        Args:
            estimated_tokens: Estimated number of tokens for the request

        Returns:
            True if within rate limits
        """
        now = datetime.utcnow()

        # Remove old entries (older than 1 minute)
        self._request_times = [
            t for t in self._request_times if (now - t).total_seconds() < 60
        ]
        self._token_usage = self._token_usage[-len(self._request_times) :]

        # Check request rate limit (assuming 60 requests per minute)
        if len(self._request_times) >= 60:
            return False

        # Check token rate limit (assuming 100k tokens per minute)
        total_tokens = sum(self._token_usage) + estimated_tokens
        if total_tokens >= 100000:
            return False

        return True

    async def wait_for_rate_limit(self, estimated_tokens: int = 0) -> None:
        """
        Wait if necessary to respect rate limits.

        Args:
            estimated_tokens: Estimated number of tokens for the request
        """
        while not await self.check_rate_limit(estimated_tokens):
            await asyncio.sleep(1)

    def _generate_cache_key(self, request: LLMProviderRequest) -> str:
        """
        Generate a cache key for the request.

        Args:
            request: Request to generate cache key for

        Returns:
            Cache key string
        """
        # Create a hash of the request parameters
        request_data = {
            "messages": request.messages,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "stop": request.stop,
            "user": request.user,
        }

        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()

    def _mask_api_key(self, api_key: Optional[str]) -> Optional[str]:
        """
        Mask API key for logging.

        Args:
            api_key: API key to mask

        Returns:
            Masked API key
        """
        if not api_key:
            return None

        if len(api_key) <= 8:
            return "*" * len(api_key)

        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the provider.

        Returns:
            Health check results
        """
        try:
            models = await self.list_models()
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_count": len(models),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
