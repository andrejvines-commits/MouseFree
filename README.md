# mouse-controller

Estrutura inicial de um cliente Flutter para Android e servidor desktop Python/WebSocket. O servidor recebe e valida mensagens com autenticação, mas não executa movimentos ou cliques nesta versão.

## Conteúdo

- `android_app/`: fontes Flutter e ponto de partida do cliente.
- `desktop_server/`: servidor local autenticado e validador do protocolo.
- `docs/protocol.md`: formato das mensagens.

Consulte os READMEs de cada parte antes de executar. O padrão é permanecer local (`127.0.0.1`); conectar dispositivos na LAN exige configuração explícita e cuidados adicionais.
