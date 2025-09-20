"""
Public crypto endpoints (e.g., expose public JWK).
"""
from fastapi import APIRouter, HTTPException
from ..services.key_cache import key_cache

router = APIRouter(prefix="/v1/crypto", tags=["crypto"])

@router.get("/jwk")
async def get_public_jwk():
    try:
        return await key_cache.get_pub_jwk()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to load JWK: {e}")
