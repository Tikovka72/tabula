from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

if TYPE_CHECKING:
    from manager import Manager
    from object_class import ObjectClass

from grid import Grid


class GridManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.grid = Grid(show=True, core_size=(self.manager.core.width(), self.manager.core.height()),
                         zero_pos=self.manager.zero_point_dot)
