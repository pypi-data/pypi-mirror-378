"""
JWK parsing and conversion helpers.
"""
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from ..utils.base64utils import b64url_to_int

def rsa_private_key_from_jwk(jwk: Dict) -> rsa.RSAPrivateKey:
    if jwk.get("kty") != "RSA":
        raise ValueError("Expected RSA JWK")
    n = b64url_to_int(jwk["n"])
    e = b64url_to_int(jwk["e"])
    d = b64url_to_int(jwk["d"])
    p = b64url_to_int(jwk["p"])
    q = b64url_to_int(jwk["q"])
    dp = b64url_to_int(jwk["dp"])
    dq = b64url_to_int(jwk["dq"])
    qi = b64url_to_int(jwk["qi"])
    numbers = rsa.RSAPrivateNumbers(
        p=p, q=q, d=d, dmp1=dp, dmq1=dq, iqmp=qi,
        public_numbers=rsa.RSAPublicNumbers(e=e, n=n),
    )
    return numbers.private_key()

def jwk_public_only(jwk: Dict) -> Dict:
    out = {k: jwk[k] for k in ("kty", "n", "e") if k in jwk}
    if "kid" in jwk:
        out["kid"] = jwk["kid"]
    return out

def rsa_public_key_from_jwk(jwk: Dict) -> Tuple[rsa.RSAPublicKey, Optional[str]]:
    if jwk.get("kty") != "RSA":
        raise ValueError("Expected RSA JWK")
    n = b64url_to_int(jwk["n"])
    e = b64url_to_int(jwk["e"])
    pub = rsa.RSAPublicNumbers(e=e, n=n).public_key()
    return pub, jwk.get("kid")

def parse_response_pub(s: str) -> Tuple[rsa.RSAPublicKey, Optional[str]]:
    import json, base64
    try:
        obj = json.loads(s)
        if isinstance(obj, dict) and obj.get("kty") == "RSA":
            return rsa_public_key_from_jwk(obj)
    except Exception:
        pass
    try:
        pub = serialization.load_pem_public_key(s.encode("utf-8"))
        if not isinstance(pub, rsa.RSAPublicKey):
            raise ValueError("Not an RSA public key")
        return pub, None
    except Exception:
        try:
            der = base64.b64decode(s, validate=False)
            pub = serialization.load_der_public_key(der)
            if not isinstance(pub, rsa.RSAPublicKey):
                raise ValueError("Not an RSA public key")
            return pub, None
        except Exception as e:
            raise ValueError(f"invalid encode_response_pub: {e}")
