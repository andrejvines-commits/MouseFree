from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ProtocolError(Exception):
    """Erro relacionado ao formato ou ao conteúdo da mensagem."""


class BaseMessage(BaseModel):
    """
    Configuração comum das mensagens.

    Campos extras são proibidos para evitar comandos não documentados.
    """

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class AuthenticateMessage(BaseMessage):
    type: Literal["authenticate"]
    token: str = Field(min_length=1, max_length=512)


class PingMessage(BaseMessage):
    type: Literal["ping"]
    timestamp: int | float | None = None


class MouseMoveMessage(BaseMessage):
    type: Literal["mouse_move"]
    x: float = Field(ge=-500, le=500)
    y: float = Field(ge=-500, le=500)


class MouseClickMessage(BaseMessage):
    type: Literal["mouse_click"]
    button: Literal["left", "right"]


class AuthenticateResponse(BaseModel):
    type: Literal["response"] = "response"
    success: bool
    message: str


class PingResponse(BaseModel):
    type: Literal["pong"] = "pong"
    success: bool
    message: str
    timestamp: int | float | None = None


AllowedMessage = AuthenticateMessage | PingMessage | MouseMoveMessage | MouseClickMessage


def parse_message(raw_message: str) -> AllowedMessage:
    """
    Converte uma string JSON em uma mensagem validada.

    Apenas os tipos authenticate e ping são permitidos nesta etapa.
    """

    try:
        decoded: Any = json.loads(raw_message)
    except json.JSONDecodeError as error:
        raise ProtocolError("A mensagem não contém um JSON válido.") from error

    if not isinstance(decoded, dict):
        raise ProtocolError("A mensagem JSON deve ser um objeto.")

    message_type = decoded.get("type")

    if message_type == "authenticate":
        model_type = AuthenticateMessage
    elif message_type == "ping":
        model_type = PingMessage
    elif message_type == "mouse_move":
        model_type = MouseMoveMessage
    elif message_type == "mouse_click":
        model_type = MouseClickMessage
    else:
        raise ProtocolError(
            f"Tipo de mensagem não permitido: {message_type!r}"
        )

    try:
        return model_type.model_validate(decoded)
    except ValidationError as error:
        raise ProtocolError(
            f"Campos inválidos na mensagem: {error.errors()}"
        ) from error
