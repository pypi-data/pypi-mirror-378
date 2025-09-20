"""
Pydantic request/response schemas.
"""
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field, field_validator

class RawEncryptRequest(BaseModel):
    encrypted_payload: str = Field(..., description="Base64 (std or urlsafe) RSA-OAEP ciphertext")
    encode_response_pub: str

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str
    max_tokens: int = 128
    temperature: float = 1.0

    @field_validator("model")
    @classmethod
    def _has_provider_prefix(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("model must be in 'provider:model_name' format")
        return v

    def split_provider(self) -> Tuple[str, str]:
        provider, model = self.model.split(":", 1)
        self.model = model
        return provider, model

class ImageRequest(BaseModel):
    prompt: str
    model: str

    @field_validator("model")
    @classmethod
    def _has_provider_prefix(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("model must be in 'provider:model_name' format")
        return v

    def split_provider(self) -> Tuple[str, str]:
        provider, model = self.model.split(":", 1)
        self.model = model
        return provider, model

class AttestMAA(BaseModel):
    runtime_data: str

class AttestRaw(BaseModel):
    runtime_data: str
