"""
Base64 helpers (std + urlsafe) and ints for JWK fields.
"""
import base64

def b64url_to_int(data: str) -> int:
    rem = len(data) % 4
    if rem:
        data += "=" * (4 - rem)
    return int.from_bytes(base64.urlsafe_b64decode(data), "big")

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def b64d_any(s: str) -> bytes:
    try:
        return base64.b64decode(s, validate=False)
    except Exception:
        rem = len(s) % 4
        if rem:
            s += "=" * (4 - rem)
        return base64.urlsafe_b64decode(s)
