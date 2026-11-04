from __future__ import annotations

import logging
import os

from fastapi import FastAPI, WebSocket

from security import TokenManager
from websocket_server import handle_websocket


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mouse Controller Server",
    version="1.2.0",
)

token_manager = TokenManager()


@app.on_event("startup")
async def on_startup() -> None:
    """
    Exibe informações importantes no terminal local.

    O token é exibido apenas no computador que está executando
    o servidor. Não o compartilhe publicamente.
    """

    host = os.getenv("MOUSE_SERVER_HOST", "0.0.0.0")
    port = os.getenv("MOUSE_SERVER_PORT", "8765")

    logger.info("Servidor Mouse Controller iniciado.")
    logger.info("Endereço de escuta: %s:%s", host, port)
    logger.info("Token de pareamento: %s", token_manager.token)
    logger.info(
        "Digite esse token no aplicativo Android para autorizar a conexão."
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Endpoint simples para verificar se o servidor está ativo.
    """

    return {
        "status": "ok",
        "service": "mouse-controller-server",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Endpoint principal do WebSocket.
    """

    await handle_websocket(
        websocket=websocket,
        token_manager=token_manager,
    )
