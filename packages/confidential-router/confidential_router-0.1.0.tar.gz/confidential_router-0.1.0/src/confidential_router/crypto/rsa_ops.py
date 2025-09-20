"""
Low-level RSA OAEP helpers.
"""
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

def rsa_oaep_decrypt(priv: rsa.RSAPrivateKey, ct: bytes) -> bytes:
    return priv.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

def rsa_oaep_max_plaintext_bytes(pub: rsa.RSAPublicKey) -> int:
    k = (pub.key_size + 7) // 8
    hlen = 32
    return k - 2 * hlen - 2
