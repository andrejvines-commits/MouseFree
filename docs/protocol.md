# Protocolo WebSocket

## Endpoint

```text
ws://IP_DO_COMPUTADOR:8765/ws
```

Exemplo:

```text
ws://192.168.1.25:8765/ws
```

## Autenticação

O cliente deve enviar:

```json
{
  "type": "authenticate",
  "token": "TOKEN_DE_PAREAMENTO"
}
```

Resposta de sucesso:

```json
{
  "type": "response",
  "success": true,
  "message": "Autenticado com sucesso."
}
```

Resposta de erro:

```json
{
  "type": "response",
  "success": false,
  "message": "Token inválido."
}
```

## Ping

Depois da autenticação, o cliente pode enviar:

```json
{
  "type": "ping",
  "timestamp": 1710000000
}
```

Resposta:

```json
{
  "type": "pong",
  "success": true,
  "message": "pong",
  "timestamp": 1710000000
}
```

## Controle do mouse

Depois da autenticação, o cliente pode enviar movimentos relativos, com cada
eixo limitado a 500 pixels por mensagem:

```json
{"type":"mouse_move","x":12.5,"y":-8}
```

Para clicar, use `left` ou `right`:

```json
{"type":"mouse_click","button":"left"}
```

## Mensagens permitidas nesta etapa

- `authenticate`
- `ping`

Mensagens como `mouse_move`, `mouse_click` e `mouse_scroll` serão adicionadas
nas próximas etapas.
