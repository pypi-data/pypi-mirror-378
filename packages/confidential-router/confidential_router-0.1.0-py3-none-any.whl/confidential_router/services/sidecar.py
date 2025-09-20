"""
HTTP client for the sidecar (SKR and attestation).
"""
import json
import httpx
from typing import Any, Dict

from ..config import SIDECAR_URL, MAA_ENDPOINT, HTTPX_TIMEOUT_SECONDS

class SidecarClient:
    def __init__(self, base_url: str = SIDECAR_URL, timeout: float = HTTPX_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def release_key(self, payload: Dict[str, Any]) -> Dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/key/release", json=payload)
        if r.status_code != 200:
            raise RuntimeError(f"sidecar release failed: {r.status_code} {r.text}")
        return json.loads(json.loads(r.content.decode())["key"])

    async def attest_maa(self, runtime_data: str, maa_endpoint: str | None = None) -> httpx.Response:
        data = {"runtime_data": runtime_data, "maa_endpoint": maa_endpoint or MAA_ENDPOINT}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(f"{self.base_url}/attest/maa", json=data)

    async def attest_raw(self, runtime_data: str) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(f"{self.base_url}/attest/raw", json={"runtime_data": runtime_data})
