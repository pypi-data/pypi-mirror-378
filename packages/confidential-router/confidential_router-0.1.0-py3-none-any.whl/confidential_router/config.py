"""
Centralized configuration (env-based) and constants.
"""
import os
from typing import Final

SIDECAR_URL: Final = os.getenv("SIDECAR_URL", "http://localhost:8080")
MAA_ENDPOINT: Final = os.getenv("MAA_ENDPOINT", "")
AKV_ENDPOINT: Final = os.getenv("AKV_ENDPOINT", "")
KID: Final = os.getenv("KID", "")
KEY_REFRESH_SECONDS: Final = int(os.getenv("KEY_REFRESH_SECONDS", "600"))

HTTPX_TIMEOUT_SECONDS: Final = float(os.getenv("HTTPX_TIMEOUT_SECONDS", "15"))
