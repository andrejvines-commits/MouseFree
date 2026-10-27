from __future__ import annotations

import os
import secrets
import hmac


class TokenManager:
    """
    Gerencia o token usado para autenticar o aplicativo Android.

    Se a variável de ambiente MOUSE_PAIRING_TOKEN existir,
    ela será usada. Caso contrário, um token seguro será gerado.
    """

    def __init__(self) -> None:
        configured_token = os.getenv("MOUSE_PAIRING_TOKEN")

        if configured_token:
            self._token = configured_token
        else:
            self._token = secrets.token_urlsafe(32)

    @property
    def token(self) -> str:
        """
        Retorna o token atual.

        O servidor exibe este token apenas no terminal local,
        para que o usuário possa digitá-lo no aplicativo.
        """
        return self._token

    def is_valid(self, received_token: str) -> bool:
        """
        Compara tokens usando comparação resistente a timing attacks.
        """
        if not isinstance(received_token, str):
            return False

        return hmac.compare_digest(self._token, received_token)