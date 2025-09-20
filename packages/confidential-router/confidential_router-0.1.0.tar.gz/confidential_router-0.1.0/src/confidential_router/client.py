#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CRClient:
    """
    Confidential Router Async Client.

    This class provides an ergonomic, fully-async interface to a Confidential Router
    deployment that expects:
      • Requests encrypted to the server's current RSA public key (fetched as a JWK).
      • Responses returned as a hybrid envelope: a random CEK (AES-GCM) encrypted to
        the client's RSA public key with RSA-OAEP-256, and the payload encrypted with AES-GCM.
      • Optional attestation calls before use.

    Design goals:
      • Clean separation: application workflows (chat, image) are distinct from cryptography.
      • Async-first: all network I/O is via httpx.AsyncClient.
      • Ergonomic defaults with escape hatches for advanced use (custom headers, timeouts, etc.).

    Typical usage:
        async with CRClient(base_url="http://localhost:8000") as cli:
            await cli.attest(mode="maa", runtime_data="...")  # optional
            data = await cli.chat(
                model="openai:gpt-4o-mini",
                message="Hello",
                max_tokens=64,
                temperature=0.7,
            )
            img = await cli.image(model="fal:flux-pro", prompt="A neon koi over waves")

    Public methods:
      • attest: call attestation endpoint ("/attest/maa" or "/attest").
      • jwk: fetch current server JWK ("/v1/crypto/jwk").
      • chat: POST encrypted chat request to "/v1/chat/completions".
      • image: POST encrypted image request to "/v1/images/generations".

    Errors:
      • Raises ValueError for invalid inputs.
      • Raises httpx.HTTPError for transport-level failures.
      • Raises RuntimeError for cryptographic envelope issues.
    """

    class _Crypto:
        """
        Cryptography utilities for RSA-JWK, RSA-OAEP-256, and AES-GCM.

        This nested class isolates all crypto concerns so the high-level client
        methods (chat/image) stay focused on application logic.

        Provided utilities:
          • Base64url encode/decode helpers without padding.
          • JWK (RSA) to cryptography public key conversion.
          • RSA-OAEP-256 encrypt/decrypt and max-plaintext calculation.
          • AES-GCM decrypt of the server's envelope.
          • Client key management: load PEM or generate ephemeral, and export public PEM.
        """

        @staticmethod
        def _b64u(data: bytes) -> str:
            """Base64url-encode bytes without padding."""
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

        @staticmethod
        def _b64u_dec(s: str) -> bytes:
            """Base64url-decode string accepting missing padding."""
            pad = "=" * (-len(s) % 4)
            return base64.urlsafe_b64decode(s + pad)

        @staticmethod
        def _b64url_to_int(data: str) -> int:
            """Convert base64url-encoded big-endian integer into Python int."""
            rem = len(data) % 4
            if rem:
                data += "=" * (4 - rem)
            return int.from_bytes(base64.urlsafe_b64decode(data), "big")

        @staticmethod
        def rsa_pub_from_jwk(jwk: Dict[str, Any]) -> rsa.RSAPublicKey:
            """Build an RSA public key from a JWK dict with kty='RSA'."""
            if jwk.get("kty") != "RSA":
                raise ValueError("Server JWK is not RSA")
            n = CRClient._Crypto._b64url_to_int(jwk["n"])
            e = CRClient._Crypto._b64url_to_int(jwk["e"])
            return rsa.RSAPublicNumbers(e=e, n=n).public_key()

        @staticmethod
        def rsa_oaep_max_plain_bytes(pub: rsa.RSAPublicKey) -> int:
            """Compute maximum plaintext size for RSA-OAEP with SHA-256."""
            k = (pub.key_size + 7) // 8
            hlen = 32
            return k - 2 * hlen - 2

        @staticmethod
        def rsa_oaep_encrypt(pub: rsa.RSAPublicKey, payload: Dict[str, Any]) -> str:
            """RSA-OAEP-256 encrypt a JSON payload and return base64url ciphertext."""
            raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            max_len = CRClient._Crypto.rsa_oaep_max_plain_bytes(pub)
            if len(raw) > max_len:
                raise ValueError(f"Payload too large for RSA-OAEP: {len(raw)} > {max_len}")
            ct = pub.encrypt(
                raw,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                             algorithm=hashes.SHA256(),
                             label=None),
            )
            return CRClient._Crypto._b64u(ct)

        @staticmethod
        def load_or_generate_private(pem_path: Optional[Union[str, Path]]) -> rsa.RSAPrivateKey:
            """Load an RSA private key from PEM file or generate a 2048-bit ephemeral key."""
            if pem_path:
                data = Path(pem_path).read_bytes()
                return serialization.load_pem_private_key(data, password=None)
            return rsa.generate_private_key(public_exponent=65537, key_size=2048)

        @staticmethod
        def public_pem_from_private(priv: rsa.RSAPrivateKey) -> str:
            """Export the SubjectPublicKeyInfo PEM for a given RSA private key."""
            pub = priv.public_key()
            pem = pub.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem.decode("utf-8")

        @staticmethod
        def decrypt_envelope(priv: rsa.RSAPrivateKey, env: Dict[str, Any]) -> Dict[str, Any]:
            """
            Decrypt a hybrid envelope {"alg","enc","ek","iv","tag","ciphertext"} into a JSON dict.

            Steps:
              • RSA-OAEP-256 decrypt 'ek' with the client's private key to obtain the CEK.
              • AES-GCM decrypt 'ciphertext'||'tag' using 'iv' and CEK.
              • Parse the resulting UTF-8 JSON plaintext.

            Returns the parsed JSON object.
            """
            required = {"alg", "enc", "ek", "iv", "tag", "ciphertext"}
            if not required.issubset(env.keys()):
                raise RuntimeError("Response is not an encrypted envelope")
            cek = priv.decrypt(
                CRClient._Crypto._b64u_dec(env["ek"]),
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                             algorithm=hashes.SHA256(),
                             label=None),
            )
            iv = CRClient._Crypto._b64u_dec(env["iv"])
            tag = CRClient._Crypto._b64u_dec(env["tag"])
            ct = CRClient._Crypto._b64u_dec(env["ciphertext"])
            aead = AESGCM(cek)
            pt = aead.decrypt(iv, ct + tag, None)
            return json.loads(pt.decode("utf-8"))

    def __init__(
        self,
        base_url: str,
        *,
        client_priv_pem_path: Optional[Union[str, Path]] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        verify_tls: bool = True,
    ) -> None:
        """
        Initialize the client.

        Parameters
        ----------
        base_url
            Server root, e.g., "http://localhost:8000" or "https://router.example.com".
        client_priv_pem_path
            Optional path to a PEM-encoded RSA private key for decrypting responses.
            If omitted, an ephemeral 2048-bit key is generated per process.
        timeout
            Default request timeout in seconds for connect+read operations.
        headers
            Optional default headers for all requests.
        verify_tls
            Whether to verify HTTPS certificates. Keep True in production.
        """
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._headers = headers or {}
        self._verify = verify_tls

        self._client: Optional[httpx.AsyncClient] = None
        self._server_pub: Optional[rsa.RSAPublicKey] = None
        self._client_priv: rsa.RSAPrivateKey = self._Crypto.load_or_generate_private(client_priv_pem_path)
        self._client_pub_pem: str = self._Crypto.public_pem_from_private(self._client_priv)

    async def __aenter__(self) -> "CRClient":
        """
        Enter async context and create an httpx.AsyncClient.

        Returns
        -------
        Self, ready to issue requests.
        """
        self._client = httpx.AsyncClient(
            base_url=self._base,
            timeout=self._timeout,
            headers=self._headers,
            verify=self._verify,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Exit async context and close the underlying HTTP client.

        Ensures a clean shutdown even when exceptions occur.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def attest(self, *, mode: str, runtime_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Call the attestation endpoint and return the server's JSON response.

        Parameters
        ----------
        mode
            One of "maa" or "raw". "maa" POSTs to "/attest/maa", "raw" POSTs to "/attest".
        runtime_data
            Opaque runtime data to embed or validate as part of attestation, if applicable.

        Returns
        -------
        The JSON response as a dict. If the server replies with non-JSON, a dict
        of the form {"result": "<raw text>"} is returned.

        Raises
        ------
        httpx.HTTPError
            On transport or non-2xx responses with raise_for_status semantics.
        """
        if self._client is None:
            raise RuntimeError("Client not started. Use 'async with CRClient(...) as c:'")

        path = "/attest/maa" if mode == "maa" else "/attest" if mode == "raw" else None
        if path is None:
            raise ValueError("attest mode must be 'maa' or 'raw'")

        r = await self._client.post(path, json={"runtime_data": runtime_data} if runtime_data else {})
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"result": r.text}

    async def jwk(self) -> Dict[str, Any]:
        """
        Fetch the server's current public JWK used to encrypt requests.

        Returns
        -------
        A dict representing the JWK, typically containing "kty", "n", and "e".

        Raises
        ------
        httpx.HTTPError
            On transport or non-2xx responses.
        ValueError
            If the JWK is not RSA when converted later.
        """
        if self._client is None:
            raise RuntimeError("Client not started. Use 'async with CRClient(...) as c:'")
        r = await self._client.get("/v1/crypto/jwk")
        r.raise_for_status()
        return r.json()

    async def chat(
        self,
        *,
        model: str,
        message: str,
        max_tokens: int = 128,
        temperature: float = 1.0,
        return_envelope: bool = False,
    ) -> Dict[str, Any]:
        """
        Send an encrypted chat request and decrypt the encrypted response.

        Parameters
        ----------
        model
            Provider:model identifier, e.g., "openai:gpt-4o-mini".
        message
            User message for the completion API.
        max_tokens
            Maximum tokens for the generation.
        temperature
            Sampling temperature for the generation.
        return_envelope
            If True, include the raw encrypted envelope under key "_envelope" in the result.

        Returns
        -------
        The decrypted response dict. If return_envelope=True, the result includes
        an additional "_envelope" key containing the raw encrypted envelope.

        Behavior
        --------
        • Fetches the server JWK if needed, encrypts payload via RSA-OAEP-256.
        • Sends to "/v1/chat/completions" with {"encrypted_payload","encode_response_pub"}.
        • If a 400 occurs mentioning "bad encrypted payload", automatically refetches JWK
          and retries once.
        • Decrypts the returned hybrid envelope using the client's RSA key and AES-GCM.
        """
        payload = {
            "messages": [{"role": "user", "content": message}],
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        data, env = await self._call_encrypted("/v1/chat/completions", payload)
        if return_envelope:
            data["_envelope"] = env
        return data

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        return_envelope: bool = False,
    ) -> Dict[str, Any]:
        """
        Send an encrypted image-generation request and decrypt the encrypted response.

        Parameters
        ----------
        model
            Provider:model identifier, e.g., "fal:flux-pro".
        prompt
            Text prompt for image generation.
        return_envelope
            If True, include the raw encrypted envelope under key "_envelope" in the result.

        Returns
        -------
        The decrypted response dict. If return_envelope=True, the result includes
        an additional "_envelope" key containing the raw encrypted envelope.

        Behavior
        --------
        • Same flow as chat() but posts to "/v1/images/generations".
        """
        payload = {"prompt": prompt, "model": model}
        data, env = await self._call_encrypted("/v1/images/generations", payload)
        if return_envelope:
            data["_envelope"] = env
        return data

    async def _call_encrypted(self, path: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Encrypt a payload to the server, POST to path, and decrypt the returned envelope.

        Parameters
        ----------
        path
            API path (e.g., "/v1/chat/completions").
        payload
            JSON-serializable dict to encrypt with RSA-OAEP-256.

        Returns
        -------
        A tuple (decrypted_data, envelope_dict).

        Raises
        ------
        httpx.HTTPError
            On transport errors. If server returns 400 due to stale JWK, a single refresh+retry is attempted.
        RuntimeError
            If the response body is not a valid encrypted envelope.
        """
        if self._client is None:
            raise RuntimeError("Client not started. Use 'async with CRClient(...) as c:'")

        if self._server_pub is None:
            jwk = await self.jwk()
            self._server_pub = self._Crypto.rsa_pub_from_jwk(jwk)

        enc = self._Crypto.rsa_oaep_encrypt(self._server_pub, payload)

        res = await self._post_encrypted(path, enc, self._client_pub_pem)
        status_ok, body = res

        if not status_ok and "bad encrypted payload" in json.dumps(body, ensure_ascii=False).lower():
            jwk = await self.jwk()
            self._server_pub = self._Crypto.rsa_pub_from_jwk(jwk)
            enc = self._Crypto.rsa_oaep_encrypt(self._server_pub, payload)
            status_ok, body = await self._post_encrypted(path, enc, self._client_pub_pem)

        if not status_ok:
            raise httpx.HTTPStatusError(
                "Server returned error",
                request=None,
                response=None,
            )

        if isinstance(body, dict) and {"ek", "iv", "tag", "ciphertext"}.issubset(body.keys()):
            decrypted = self._Crypto.decrypt_envelope(self._client_priv, body)
            return decrypted, body

        raise RuntimeError("Expected encrypted envelope in response")

    async def _post_encrypted(self, path: str, enc_b64: str, client_pub_pem: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Low-level encrypted POST helper.

        Parameters
        ----------
        path
            API path.
        enc_b64
            Base64url-encoded ciphertext of the request payload.
        client_pub_pem
            PEM-encoded client public key for the server to target in its envelope.

        Returns
        -------
        A pair (status_ok, body_dict). status_ok is True for HTTP 200; False otherwise.
        """
        if self._client is None:
            raise RuntimeError("Client not started. Use 'async with CRClient(...) as c:'")
        r = await self._client.post(
            path,
            json={"encrypted_payload": enc_b64, "encode_response_pub": client_pub_pem},
        )
        status_ok = r.status_code == 200
        try:
            body = r.json()
        except Exception:
            body = {"raw": r.text}
        return status_ok, body


# Example manual test
# async def _demo():
#     async with CRClient("http://localhost:8000") as cli:
#         await cli.attest(mode="maa", runtime_data="optional")
#         resp = await cli.chat(model="openai:gpt-4o-mini", message="Hello from async client")
#         print(json.dumps(resp, indent=2, ensure_ascii=False))
#
# if __name__ == "__main__":
#     asyncio.run(_demo())
