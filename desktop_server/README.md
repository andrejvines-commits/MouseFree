# Mouse Controller - Desktop Server

Servidor WebSocket para controlar futuramente o mouse de um computador
a partir de um aplicativo Android.

## Requisitos

- Python 3.11 ou superior
- VS Code
- Windows inicialmente

## Criar ambiente virtual

No diretório `desktop_server`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

## Instalar dependências

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Executar o servidor

```bash
uvicorn app:app --host 0.0.0.0 --port 8765
```

O terminal exibirá um token semelhante a:

```text
Token de pareamento: um-token-gerado-pelo-servidor
```

Esse token deverá ser informado no aplicativo Android.

## Testar o endpoint HTTP

Abra no navegador:

```text
http://127.0.0.1:8765/health
```

A resposta esperada é:

```json
{
  "status": "ok",
  "service": "mouse-controller-server"
}
```

## Variáveis de ambiente

É possível definir uma porta diferente:

PowerShell:

```powershell
$env:MOUSE_SERVER_PORT="9000"
uvicorn app:app --host 0.0.0.0 --port 9000
```

Também é possível definir um token manualmente:

PowerShell:

```powershell
$env:MOUSE_PAIRING_TOKEN="meu-token-local-seguro"
uvicorn app:app --host 0.0.0.0 --port 8765
```

Não compartilhe o token com pessoas não autorizadas.