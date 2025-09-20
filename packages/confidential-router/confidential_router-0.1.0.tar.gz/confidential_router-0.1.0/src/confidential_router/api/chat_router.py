"""
Chat endpoint: decrypt request, call provider, re-encrypt response.
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import RawEncryptRequest, ChatRequest
from ..crypto.envelope import decrypt_request_payload, encrypt_for_client
from ..services.key_cache import key_cache

# Reuse existing provider class from user's codebase
from ..provider.chat import CROpenAI  # type: ignore

router = APIRouter(prefix="/v1/chat", tags=["chat"])

@router.post("/completions")
async def call_chat(body: RawEncryptRequest):
    payload = await decrypt_request_payload(body.encrypted_payload, key_cache.get_priv)
    try:
        chat = ChatRequest(**payload)
        provider, _ = chat.split_provider()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"invalid chat payload: {e}")
    client = CROpenAI(provider)
    try:
        result: dict = await client(**chat.model_dump())
        return await encrypt_for_client(body.encode_response_pub, result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"chat provider error: {e}")
