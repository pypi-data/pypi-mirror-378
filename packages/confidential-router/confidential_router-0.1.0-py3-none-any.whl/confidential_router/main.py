"""
FastAPI factory that wires all routers together.
Keep this thin so the app can be embedded or extended easily.
"""
from fastapi import FastAPI
from .api.crypto_router import router as crypto_router
from .api.chat_router import router as chat_router
from .api.image_router import router as image_router
from .api.attest_router import router as attest_router

def create_app() -> FastAPI:
    app = FastAPI(title="Confidential Router")
    app.include_router(crypto_router)
    app.include_router(chat_router)
    app.include_router(image_router)
    app.include_router(attest_router)
    return app

# For uvicorn entry points like: uvicorn confidential_router.main:app
app = create_app()
