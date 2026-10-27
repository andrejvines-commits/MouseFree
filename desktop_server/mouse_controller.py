from __future__ import annotations

import ctypes
import platform


class MouseController:
    """Executes local mouse commands on Windows."""

    _MOVE = 0x0001
    _LEFT_DOWN = 0x0002
    _LEFT_UP = 0x0004
    _RIGHT_DOWN = 0x0008
    _RIGHT_UP = 0x0010

    def __init__(self) -> None:
        if platform.system() != "Windows":
            raise RuntimeError("Mouse control is supported only on Windows.")
        self._user32 = ctypes.windll.user32

    def move(self, x: float, y: float) -> None:
        self._user32.mouse_event(self._MOVE, round(x), round(y), 0, 0)

    def click(self, button: str) -> None:
        down, up = {
            "left": (self._LEFT_DOWN, self._LEFT_UP),
            "right": (self._RIGHT_DOWN, self._RIGHT_UP),
        }[button]
        self._user32.mouse_event(down, 0, 0, 0, 0)
        self._user32.mouse_event(up, 0, 0, 0, 0)
