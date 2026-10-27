from __future__ import annotations

import logging

from fastapi import WebSocket, WebSocketDisconnect

from protocol import (
    AuthenticateMessage,
    AuthenticateResponse,
    PingMessage,
    PingResponse,
    MouseClickMessage,
    MouseMoveMessage,
    ProtocolError,
    parse_message,
)
from mouse_controller import MouseController
from security import TokenManager


logger = logging.getLogger(__name__)


async def send_error(
    websocket: WebSocket,
    message: str,
) -> None:
    """
    Envia uma resposta de erro sem incluir informações sensíveis.
    """

    await websocket.send_json(
        AuthenticateResponse(
            success=False,
            message=message,
        ).model_dump()
    )


async def handle_websocket(
    websocket: WebSocket,
    token_manager: TokenManager,
) -> None:
    """
    Gerencia uma conexão WebSocket individual.

    O cliente precisa autenticar antes de utilizar comandos protegidos.
    """

    await websocket.accept()

    is_authenticated = False
    client_address = websocket.client
    mouse = MouseController()

    logger.info("Nova conexão WebSocket recebida de %s", client_address)

    try:
        while True:
            raw_message = await websocket.receive_text()

            try:
                message = parse_message(raw_message)
            except ProtocolError as error:
                logger.warning(
                    "Mensagem inválida recebida de %s: %s",
                    client_address,
                    error,
                )

                await send_error(
                    websocket,
                    "Mensagem inválida.",
                )
                continue

            if isinstance(message, AuthenticateMessage):
                if is_authenticated:
                    await send_error(
                        websocket,
                        "A conexão já está autenticada.",
                    )
                    continue

                if not token_manager.is_valid(message.token):
                    logger.warning(
                        "Tentativa de autenticação inválida de %s",
                        client_address,
                    )

                    await send_error(
                        websocket,
                        "Token inválido.",
                    )

                    await websocket.close(code=1008)
                    return

                is_authenticated = True

                await websocket.send_json(
                    AuthenticateResponse(
                        success=True,
                        message="Autenticado com sucesso.",
                    ).model_dump()
                )

                logger.info(
                    "Cliente autenticado com sucesso: %s",
                    client_address,
                )

            elif isinstance(message, PingMessage):
                if not is_authenticated:
                    await send_error(
                        websocket,
                        "Autenticação necessária antes do ping.",
                    )
                    continue

                await websocket.send_json(
                    PingResponse(
                        success=True,
                        message="pong",
                        timestamp=message.timestamp,
                    ).model_dump()
                )

            elif isinstance(message, MouseMoveMessage):
                if not is_authenticated:
                    await send_error(websocket, "Authentication required before command.")
                    continue
                mouse.move(message.x, message.y)

            elif isinstance(message, MouseClickMessage):
                if not is_authenticated:
                    await send_error(websocket, "Authentication required before command.")
                    continue
                mouse.click(message.button)

    except WebSocketDisconnect:
        logger.info("Cliente desconectado: %s", client_address)

    except Exception:
        logger.exception(
            "Erro inesperado ao processar conexão de %s",
            client_address,
        )

        try:
            await websocket.close(code=1011)
        except Exception:
            pass
