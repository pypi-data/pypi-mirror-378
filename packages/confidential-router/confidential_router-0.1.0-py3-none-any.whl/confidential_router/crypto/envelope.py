"""
Hybrid envelope encryption for responses and request decryption.
"""
import json
import os
from typing import Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .jwk import parse_response_pub
from .rsa_ops import rsa_oaep_decrypt
from ..utils.base64utils import b64u, b64d_any

async def encrypt_for_client(encode_response_pub: str, data: dict) -> dict:
    pub, kid = parse_response_pub(encode_response_pub)
    cek = os.urandom(32)
    iv = os.urandom(12)
    aead = AESGCM(cek)
    pt = json.dumps(data, separators=(",", ":")).encode("utf-8")
    ct_with_tag = aead.encrypt(iv, pt, None)
    ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
    ek = pub.encrypt(
        cek,
        padding=__import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["padding"]).padding.OAEP(
            mgf=__import__("cryptography.hazmat.primitives.asymmetric.padding", fromlist=["padding"]).padding.MGF1(
                algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["hashes"]).hashes.SHA256()
            ),
            algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["hashes"]).hashes.SHA256(),
            label=None,
        ),
    )
    out = {
        "alg": "RSA-OAEP",
        "enc": "A256GCM",
        "ek": b64u(ek),
        "iv": b64u(iv),
        "tag": b64u(tag),
        "ciphertext": b64u(ct),
    }
    if kid:
        out["kid"] = kid
    return out

async def decrypt_request_payload(encrypted_b64: str, priv_key_provider) -> dict:
    try:
        priv = await priv_key_provider()
        ct = b64d_any(encrypted_b64)
        pt = rsa_oaep_decrypt(priv, ct)
        return json.loads(pt.decode("utf-8"))
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, (ValueError, json.JSONDecodeError)):
            raise HTTPException(status_code=400, detail=f"bad encrypted payload: {e}")
        raise HTTPException(status_code=500, detail=f"decrypt failed: {e}")
