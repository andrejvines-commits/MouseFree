from __future__ import annotations

import json
import socket
import threading
import time
import tkinter as tk
import urllib.request
import webbrowser
from tkinter import messagebox, ttk

import qrcode
import uvicorn
from PIL import ImageTk

from app import app, token_manager


APP_VERSION = "1.3.0"
PORT = 8765
LATEST_RELEASE_API = (
    "https://api.github.com/repos/andrejvines-commits/MouseFree/releases/latest"
)
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


def is_newer_version(latest: str, current: str) -> bool:
    def parts(version: str) -> list[int]:
        return [int(part) if part.isdigit() else 0 for part in version.split(".")]

    left, right = parts(latest), parts(current)
    for index in range(3):
        latest_part = left[index] if index < len(left) else 0
        current_part = right[index] if index < len(right) else 0
        if latest_part != current_part:
            return latest_part > current_part
    return False


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

        ttk.Label(frame, text="QR Code de conexão").grid(
            row=3, column=0, columnspan=2
        )
        qr = qrcode.make(self.connection_code).resize((220, 220))
        self.qr_image = ImageTk.PhotoImage(qr)
        ttk.Label(frame, image=self.qr_image).grid(
            row=4, column=0, columnspan=2, pady=(6, 12)
        )

        ttk.Label(frame, text="Código de conexão").grid(row=5, column=0, sticky="w")
        self.code_entry = ttk.Entry(frame, width=58)
        self.code_entry.insert(0, self.connection_code)
        self.code_entry.configure(state="readonly")
        self.code_entry.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 8))

        self.start_button = ttk.Button(
            frame, text="Iniciar servidor", command=self.start_server
        )
        self.start_button.grid(row=7, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(frame, text="Copiar código", command=self.copy_code).grid(
            row=7, column=1, sticky="ew", padx=(6, 0)
        )

        ttk.Label(
            frame,
            text="No Android, toque em Ler QR Code e aponte a câmera para este código.",
            wraplength=440,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(16, 12))
        self.update_button = ttk.Button(
            frame, text="Verificar atualização", command=self.check_for_update
        )
        self.update_button.grid(row=9, column=0, columnspan=2, sticky="ew")

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

    def check_for_update(self) -> None:
        self.update_button.configure(state="disabled")
        self.status.set("Procurando atualizações...")
        threading.Thread(target=self._fetch_update, daemon=True).start()

    def _fetch_update(self) -> None:
        try:
            request = urllib.request.Request(
                LATEST_RELEASE_API, headers={"User-Agent": "MouseFree-PC"}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                release = json.load(response)
            latest = str(release["tag_name"]).removeprefix("v")
            self.root.after(0, self._show_update_result, latest)
        except Exception as exception:
            self.root.after(0, self._show_update_error, str(exception))

    def _show_update_result(self, latest: str) -> None:
        self.update_button.configure(state="normal")
        if not is_newer_version(latest, APP_VERSION):
            self.status.set("App atualizado")
            messagebox.showinfo("MouseFree", "App atualizado.")
            return
        self.status.set(f"Nova versão disponível: {latest}")
        if messagebox.askyesno(
            "Atualização disponível",
            f"A versão {latest} está disponível. Deseja baixar agora?",
        ):
            webbrowser.open(DESKTOP_DOWNLOAD_URL)

    def _show_update_error(self, error: str) -> None:
        self.update_button.configure(state="normal")
        self.status.set("Não foi possível procurar atualizações.")
        messagebox.showerror("MouseFree", f"Não foi possível procurar atualizações.\n{error}")

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
