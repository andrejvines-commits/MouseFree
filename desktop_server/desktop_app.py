from __future__ import annotations

import socket
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import uvicorn

from app import app, token_manager


PORT = 8765
DESKTOP_DOWNLOAD_URL = (
    "https://github.com/andrejvines-commits/MouseFree/"
    "releases/latest/download/MouseFree-PC.exe"
)


def local_ip_address() -> str:
    """Returns the LAN address most likely reachable by the Android device."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


class MouseFreeDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.server: uvicorn.Server | None = None
        self.server_thread: threading.Thread | None = None
        self._starting_at: float | None = None

        self.address = f"ws://{local_ip_address()}:{PORT}/ws"
        self.connection_code = f"{self.address}|{token_manager.token}"

        root.title("MouseFree PC")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.close)

        frame = ttk.Frame(root, padding=20)
        frame.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ttk.Label(frame, text="MouseFree PC", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            frame,
            text="Conecte o Android e controle este computador pela mesma rede Wi-Fi.",
            wraplength=440,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))

        self.status = tk.StringVar(value="Servidor parado")
        ttk.Label(frame, textvariable=self.status).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        ttk.Label(frame, text="Código de conexão").grid(row=3, column=0, sticky="w")
        self.code_entry = ttk.Entry(frame, width=58)
        self.code_entry.insert(0, self.connection_code)
        self.code_entry.configure(state="readonly")
        self.code_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 8))

        self.start_button = ttk.Button(
            frame, text="Iniciar servidor", command=self.start_server
        )
        self.start_button.grid(row=5, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(frame, text="Copiar código", command=self.copy_code).grid(
            row=5, column=1, sticky="ew", padx=(6, 0)
        )

        ttk.Label(
            frame,
            text="No Android, cole este código no campo Código de conexão e toque em Conectar.",
            wraplength=440,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(16, 12))
        ttk.Button(
            frame, text="Atualizar aplicativo do PC", command=self.open_update
        ).grid(row=7, column=0, columnspan=2, sticky="ew")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def copy_code(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.connection_code)
        self.root.update()
        self.status.set("Código copiado. Cole-o no aplicativo Android.")

    def start_server(self) -> None:
        if self.server_thread and self.server_thread.is_alive():
            return

        self.server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
        )
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()
        self._starting_at = time.monotonic()
        self.start_button.configure(state="disabled")
        self.status.set("Iniciando servidor...")
        self.wait_for_server()

    def wait_for_server(self) -> None:
        if self.server and self.server.started:
            self.status.set(f"Servidor ativo em {self.address}")
            return
        if not self.server_thread or not self.server_thread.is_alive():
            self.status.set("Não foi possível iniciar. A porta 8765 pode estar em uso.")
            self.start_button.configure(state="normal")
            return
        if self._starting_at and time.monotonic() - self._starting_at > 10:
            self.status.set("A inicialização demorou. Verifique a porta 8765.")
            self.start_button.configure(state="normal")
            return
        self.root.after(100, self.wait_for_server)

    def open_update(self) -> None:
        webbrowser.open(DESKTOP_DOWNLOAD_URL)

    def close(self) -> None:
        if self.server:
            self.server.should_exit = True
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    MouseFreeDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
