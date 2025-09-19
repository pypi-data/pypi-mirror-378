"""
Pydantic schemas for LLM operations.

This module provides Pydantic models for LLM request/response validation,
conversation management, and provider configuration.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LLMUsage(BaseModel):
    """LLM usage statistics."""

    prompt_tokens: int = Field(ge=0, description="Number of prompt tokens")
    completion_tokens: int = Field(ge=0, description="Number of completion tokens")
    total_tokens: int = Field(ge=0, description="Total number of tokens")
    cost: Optional[float] = Field(None, ge=0, description="Cost in USD")


class LLMError(BaseModel):
    """LLM error information."""

    error_type: str = Field(description="Type of error")
    error_message: str = Field(description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class LLMProvider(BaseModel):
    """LLM provider information."""

    name: str = Field(description="Provider name (openai, deepseek, llama, anthropic)")
    version: Optional[str] = Field(None, description="Provider version")
    base_url: str = Field(description="Provider base URL")
    api_key: Optional[str] = Field(None, description="API key (masked)")
    models: List[str] = Field(default_factory=list, description="Available models")
    capabilities: List[str] = Field(
        default_factory=list, description="Provider capabilities"
    )
    is_active: bool = Field(default=True, description="Whether provider is active")


class LLMModel(BaseModel):
    """LLM model information."""

    name: str = Field(description="Model name")
    provider: str = Field(description="Provider name")
    version: Optional[str] = Field(None, description="Model version")
    max_tokens: int = Field(ge=1, description="Maximum tokens")
    context_length: int = Field(ge=1, description="Context length")
    capabilities: List[str] = Field(
        default_factory=list, description="Model capabilities"
    )
    cost_per_token: Optional[float] = Field(None, ge=0, description="Cost per token")
    is_active: bool = Field(default=True, description="Whether model is active")


class LLMRequest(BaseModel):
    """LLM request model."""

    id: UUID = Field(description="Request ID")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID")
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: List[Dict[str, str]] = Field(description="Chat messages")
    temperature: float = Field(ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(ge=1, description="Maximum tokens")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p value")
    frequency_penalty: Optional[float] = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: Optional[float] = Field(
        None, ge=-2.0, le=2.0, description="Presence penalty"
    )
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    stream: bool = Field(default=False, description="Whether to stream response")
    user: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tenant_id: Optional[str] = Field(None, description="Tenant ID")
    service_name: Optional[str] = Field(None, description="Service name")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class LLMResponse(BaseModel):
    """LLM response model."""

    id: UUID = Field(description="Response ID")
    request_id: UUID = Field(description="Request ID")
    content: str = Field(description="Response content")
    finish_reason: Optional[str] = Field(None, description="Finish reason")
    usage: Optional[LLMUsage] = Field(None, description="Usage statistics")
    error: Optional[LLMError] = Field(None, description="Error information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class LLMConversation(BaseModel):
    """LLM conversation model."""

    id: UUID = Field(description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: List[Dict[str, str]] = Field(
        default_factory=list, description="All messages"
    )
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used")
    total_cost: Optional[float] = Field(None, ge=0, description="Total cost")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tenant_id: Optional[str] = Field(None, description="Tenant ID")
    service_name: Optional[str] = Field(None, description="Service name")
    is_active: bool = Field(default=True, description="Whether conversation is active")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


# Create schemas
class LLMRequestCreate(BaseModel):
    """Schema for creating LLM requests."""

    conversation_id: Optional[UUID] = None
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: List[Dict[str, str]] = Field(description="Chat messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=1)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    stream: bool = False
    user: Optional[str] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None
    service_name: Optional[str] = None

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate messages format."""
        if not v:
            raise ValueError("Messages cannot be empty")

        for message in v:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary")
            if "role" not in message or "content" not in message:
                raise ValueError("Each message must have 'role' and 'content' keys")
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError("Role must be 'system', 'user', or 'assistant'")

        return v


class LLMResponseCreate(BaseModel):
    """Schema for creating LLM responses."""

    request_id: UUID = Field(description="Request ID")
    content: str = Field(description="Response content")
    finish_reason: Optional[str] = None
    usage: Optional[LLMUsage] = None
    error: Optional[LLMError] = None
    llm_metadata: Optional[Dict[str, Any]] = None


class LLMConversationCreate(BaseModel):
    """Schema for creating LLM conversations."""

    title: Optional[str] = None
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: List[Dict[str, str]] = Field(default_factory=list)
    llm_metadata: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None
    service_name: Optional[str] = None


# Update schemas
class LLMRequestUpdate(BaseModel):
    """Schema for updating LLM requests."""

    llm_metadata: Optional[Dict[str, Any]] = None


class LLMResponseUpdate(BaseModel):
    """Schema for updating LLM responses."""

    content: Optional[str] = None
    finish_reason: Optional[str] = None
    usage: Optional[LLMUsage] = None
    error: Optional[LLMError] = None
    llm_metadata: Optional[Dict[str, Any]] = None


class LLMConversationUpdate(BaseModel):
    """Schema for updating LLM conversations."""

    title: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
