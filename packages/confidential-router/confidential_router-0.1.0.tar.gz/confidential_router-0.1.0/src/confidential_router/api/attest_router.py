"""
Attestation passthrough endpoints to the sidecar (MAA/raw).
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import AttestMAA, AttestRaw
from ..services.sidecar import SidecarClient

router = APIRouter(prefix="/attest", tags=["attest"])
_sidecar = SidecarClient()

@router.post("/maa")
async def attest_maa(payload: AttestMAA):
    try:
        r = await _sidecar.attest_maa(runtime_data=payload.runtime_data)
        try:
            return r.json()
        except Exception:
            return {"result": r.text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"attest/maa failed: {e}")

@router.post("")
async def attest_raw(payload: AttestRaw):
    try:
        r = await _sidecar.attest_raw(runtime_data=payload.runtime_data)
        try:
            return r.json()
        except Exception:
            return {"result": r.text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"attest/raw failed: {e}")
