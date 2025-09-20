"""
Image endpoint: decrypt request, call provider, re-encrypt response.
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import RawEncryptRequest, ImageRequest
from ..crypto.envelope import decrypt_request_payload, encrypt_for_client
from ..services.key_cache import key_cache

# Reuse existing provider class from user's codebase
from ..provider.image import CRFal  # type: ignore

router = APIRouter(prefix="/v1/images", tags=["images"])

@router.post("/generations")
async def call_image(body: RawEncryptRequest):
    payload = await decrypt_request_payload(body.encrypted_payload, key_cache.get_priv)
    try:
        img = ImageRequest(**payload)
        provider, _ = img.split_provider()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"invalid image payload: {e}")
    if provider == "fal":
        client = CRFal()
        try:
            result: dict = await client(**img.model_dump())
            return await encrypt_for_client(body.encode_response_pub, result)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"image provider error: {e}")
    raise HTTPException(status_code=400, detail=f"unsupported provider '{provider}'")
