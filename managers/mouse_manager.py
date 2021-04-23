from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manager import Manager

from mouse import Mouse


class MouseManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.mouse = Mouse()

    def get_mouse_pos(self) -> tuple:
        """
        :return: mouse position
        """
        return self.mouse.get_pos()

    def change_mouse_pos(self, x: int, y: int):
        """
        changes mouse (mouse.Mouse) position to (x, y)
        """
        self.mouse.change_pos(x, y)
