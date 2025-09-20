from __future__ import annotations

from typing import Tuple

try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore


class AirMouse:
    def __init__(self) -> None:
        if pyautogui is None:
            raise RuntimeError("pyautogui is required. Install dependencies from requirements.txt")
        pyautogui.FAILSAFE = False

    def position(self) -> Tuple[int, int]:
        p = pyautogui.position()
        return int(p.x), int(p.y)

    def move_to(self, x: int, y: int) -> None:
        pyautogui.moveTo(int(x), int(y), duration=0)

    def move_rel(self, dx: int, dy: int) -> None:
        pyautogui.moveRel(int(dx), int(dy), duration=0)

    def click(self, *, button: str = "left", clicks: int = 1, x: int | None = None, y: int | None = None) -> None:
        button_map = {"left": "left", "right": "right", "middle": "middle"}
        b = button_map.get(button, "left")
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), clicks=int(clicks), button=b)
        else:
            pyautogui.click(clicks=int(clicks), button=b)

    def scroll(self, *, dx: int = 0, dy: int = 0) -> None:
        if dy:
            pyautogui.scroll(int(dy))
        if dx:
            pyautogui.hscroll(int(dx))
