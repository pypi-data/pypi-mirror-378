"""
Async SKR key cache backed by sidecar.
"""
import asyncio
import os
import time
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import rsa

from ..config import MAA_ENDPOINT, AKV_ENDPOINT, KID, KEY_REFRESH_SECONDS
from ..crypto.jwk import rsa_private_key_from_jwk, jwk_public_only
from .sidecar import SidecarClient

class AsyncSKRKeyCache:
    def __init__(self, sidecar: Optional[SidecarClient] = None):
        self._lock = asyncio.Lock()
        self._priv: Optional[rsa.RSAPrivateKey] = None
        self._pub_jwk: Optional[Dict] = None
        self._exp: float = 0.0
        self._sidecar = sidecar or SidecarClient()

    async def _fetch_from_sidecar(self) -> Tuple[rsa.RSAPrivateKey, Dict]:
        payload = {"maa_endpoint": MAA_ENDPOINT, "akv_endpoint": AKV_ENDPOINT, "kid": KID}
        jwk = await self._sidecar.release_key(payload)
        if not jwk or jwk.get("kty") != "RSA":
            raise RuntimeError("sidecar did not return RSA JWK")
        priv = rsa_private_key_from_jwk(jwk)
        return priv, jwk_public_only(jwk)

    async def _refresh_if_needed(self):
        now = time.time()
        if self._priv is None or now >= self._exp:
            async with self._lock:
                if self._priv is None or time.time() >= self._exp:
                    priv, pub = await self._fetch_from_sidecar()
                    jitter = KEY_REFRESH_SECONDS * 0.05
                    self._priv, self._pub_jwk, self._exp = (
                        priv,
                        pub,
                        time.time() + KEY_REFRESH_SECONDS - jitter + (2 * jitter * os.urandom(1)[0] / 255.0),
                    )

    async def get_priv(self) -> rsa.RSAPrivateKey:
        await self._refresh_if_needed()
        return self._priv  # type: ignore[return-value]

    async def get_pub_jwk(self) -> Dict:
        await self._refresh_if_needed()
        return dict(self._pub_jwk or {})

# shared instance
key_cache = AsyncSKRKeyCache()
