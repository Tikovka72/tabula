from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from managers.arrow_manager import ArrowManager

from PyQt5.QtCore import QLine
from PyQt5.QtGui import QPainter

import math
from numpy import arctan2

from objects.settings_widget import SettingsWindow

from constants import FROM_AND_TO_NEAREST_LINE, DEFAULT_ARROW_COLOR, DEFAULT_SELECTED_ARROW_COLOR

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


class Arrow:
    """
    class for arrows in tabula
    """

    def __init__(self, manager: ArrowManager = None,
                 start_pos: tuple or list or None = None,
                 end_pos: tuple or list or None = None,
                 color: str = DEFAULT_ARROW_COLOR,
                 need_arrow: bool = False,
                 arrow_type: int = FROM_AND_TO_NEAREST_LINE):
        """
        :param manager: main class containing all information
        :param start_pos: position of start in (x, y) format
        :param end_pos: position of end in (x, y) format
        :param color: color of arrow in hex format
        :param need_arrow: needs arrow on end
               ---> with arrow
               ---- without arrow
        :param arrow_type: integer of arrow's type
               ^ clear this if don't use
        """
        if not manager:
            exit(1)
        self.arrow_manager = manager
        self.start_pos = tuple(start_pos) if start_pos else None
        self.start_pos_by_obj = (0, 0)
        self.end_pos_by_obj = (0, 0)
        self.end_pos = tuple(end_pos) if end_pos else None
        self.color = color
        self.obj1 = None
        self.obj2 = None
        self.selected = False
        self.selected_color = DEFAULT_SELECTED_ARROW_COLOR
        self.need_arrow = need_arrow
        self.arrow_type = arrow_type
        self.arrow_manager.manager.settings_window.hide_all_sett()

        self.arrow_manager.manager.settings_window.add_settings(
            self,
            SettingsWindow.Title,
            name="Положение стрелки")

        self.arrow_manager.manager.settings_window.add_settings(
            self,
            SettingsWindow.SettTwoLineEdit,
            name="Позиция на первом объекте",
            standard_values=(0, 0),
            int_only=True,
            default_values_to_return=(0, 0),
            callback=(self.callback_x1, self.callback_y1),
            call_update_all=self.call_set_xy1)

        self.arrow_manager.manager.settings_window.add_settings(
            self,
            SettingsWindow.SettTwoLineEdit,
            name="Позиция на втором объекте",
            standard_values=(0, 0),
            int_only=True,
            default_values_to_return=(0, 0),
            callback=(self.callback_x2, self.callback_y2),
            call_update_all=self.call_set_xy2)

        self.arrow_manager.manager.settings_window.add_settings(
            self,
            SettingsWindow.SettCheckbox,
            name="Стрелка",
            standard_values=(("вкл", True),),
            default_values_to_return=(True,),
            callback=(self.callback_arrow,),
            call_update_all=self.call_set_arrow)

        self.arrow_manager.manager.settings_window.show_sett(self)

    def callback_arrow(self, need: bool):
        """
        callback for settings window. This is necessary to change arrow type:
        ---> to ---- and back
        settings window -> arrow
        """
        self.need_arrow = bool(need)

    def call_set_arrow(self) -> bool:
        """
        gives if line haves arrow
        arrow -> settings window
        """
        return self.need_arrow

    def callback_x1(self, x1: int):
        """
        callback for settings window. This is necessary to change x coordinate of line's starting
        settings window -> arrow
        """
        if not self.start_pos or not self.obj1:
            return
        if -(self.obj1.size().width() // 2) >= x1:
            x1 = -(self.obj1.size().width() // 2)
        elif self.obj1.size().width() // 2 <= x1:
            x1 = self.obj1.size().width() // 2

        self.start_pos_by_obj = x1, self.start_pos_by_obj[1]
        self.set_start_and_end()

    def callback_y1(self, y1: int):
        """
        callback for settings window. This is necessary to change Y coordinate of line's starting
        settings window -> arrow
        """
        if not self.start_pos or not self.obj1:
            return
        if -(self.obj1.size().height() // 2) >= y1:
            y1 = -(self.obj1.size().height() // 2)
        elif self.obj1.size().height() // 2 <= y1:
            y1 = self.obj1.size().height() // 2
        self.start_pos_by_obj = self.start_pos_by_obj[0], y1
        self.set_start_and_end()

    def callback_x2(self, x2: int):
        """
        callback for settings window. This is necessary to change x coordinate of line's ending
        settings window -> arrow
        """
        if not self.end_pos or not self.obj2:
            return
        if -(self.obj2.size().width() // 2) >= x2:
            x2 = -(self.obj2.size().width() // 2)
        elif self.obj2.size().width() // 2 <= x2:
            x2 = self.obj2.size().width() // 2
        self.end_pos_by_obj = x2, self.end_pos_by_obj[1]
        self.set_start_and_end()

    def callback_y2(self, y2: int):
        """
        callback for settings window. This is necessary to change y coordinate of line's ending
        settings window -> arrow
        """
        if not self.end_pos or not self.obj2:
            return
        if -(self.obj2.size().height() // 2) >= y2:
            y2 = -(self.obj2.size().height() // 2)
        elif self.obj2.size().height() // 2 <= y2:
            y2 = self.obj2.size().height() // 2
        self.end_pos_by_obj = self.end_pos_by_obj[0], y2
        self.set_start_and_end()

    def call_set_xy1(self) -> Tuple[int, int]:
        """
        gives line's start position by self.obj1 object
        arrow -> settings window
        """
        if not self.start_pos or not self.obj1:
            return 0, 0
        return self.start_pos_by_obj

    def call_set_xy2(self) -> Tuple[int, int]:
        """
        gives line's end position by self.obj2 object
        arrow -> settings window
        """
        if not self.end_pos or not self.obj2:
            return 0, 0
        return self.end_pos_by_obj

    def set_start_and_end(self) -> Tuple[Tuple[int, int], Tuple[int, int]] or None:
        """
        sets self.start_pos and self.end_pos by position on objects
        :return: start and end pos in tuple like ((x start, y start), (x end, y end))
                 or None if objects is None
        """
        if not (self.obj1 and self.obj2):
            return

        self.start_pos = (self.obj1.x() + self.obj1.width() // 2 + self.start_pos_by_obj[0],
                          self.obj1.y() + self.obj1.height() // 2 + self.start_pos_by_obj[1])

        self.end_pos = (self.obj2.x() + self.obj2.width() // 2 + self.end_pos_by_obj[0],
                        self.obj2.y() + self.obj2.height() // 2 + self.end_pos_by_obj[1])

        return self.start_pos, self.end_pos

    def get_start_and_end(self, end_pos: Tuple[int, int] or List[int, int]) \
            -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        generates start_pos by position on object1 and end pos by parameter end_pos
        :param end_pos: your end position
        :return: start and end pos in tuple like ((x start, y start), (x end, y end))
                 or ((0, 0), (0, 0)) if object1 is None
        """
        if not self.obj1:
            return (0, 0), (0, 0)
        return (self.obj1.x() + self.obj1.width() // 2 + self.start_pos_by_obj[0],
                self.obj1.y() + self.obj1.height() // 2 + self.start_pos_by_obj[1]), end_pos

    def create_arrow(self, end_pos: Tuple[int, int] or List[int, int] = None) -> Tuple[QLine, QLine]:
        """
        creates arrow's lines and returns them in QLine format
        :param end_pos: position of line's top
        :return: two QLine in tuple
        """
        if self.start_pos:
            start = self.start_pos
            end = self.end_pos or end_pos
        else:
            start, end = self.get_start_and_end(end_pos or self.end_pos)
        ul = arctan2(-(start[0] - end[0]), -(start[1] - end[1]))
        s1 = int(end[0] + 20 * math.sin(ul - 40)), int(end[1] + 20 * math.cos(ul - 40))
        s2 = int(end[0] + 20 * math.sin(ul + 40)), int(end[1] + 20 * math.cos(ul + 40))
        return QLine(*s1, *end), QLine(*s2, *end)

    def set_focus(self):
        """
        sets focus for this arrow
        """
        self.selected = True
        self.arrow_manager.manager.settings_window.hide_all_sett()
        self.arrow_manager.manager.settings_window.show_sett(self)

    def clear_focus(self):
        """
        clears focus from this arrow
        """
        self.selected = False

    def get_color(self) -> str:
        """
        :return: color of line at the moment
        """
        return self.selected_color if self.selected else self.color

    def draw(self, qp: QPainter, end_pos: tuple or list = None) -> bool:
        """
        draws line in core object
        :param qp: QPainter of main UI object (core)
        :param end_pos: position of mouse if arrow on mouse
               if arrow has end position, end_pos param will be ignored
        """
        if self.end_pos:
            qp.drawLine(QLine(*self.start_pos, *self.end_pos))
            if self.need_arrow:
                ar1, ar2 = self.create_arrow(end_pos=self.end_pos)
                qp.drawLines(ar1, ar2)
            return False
        elif end_pos:
            start, end = self.get_start_and_end(end_pos)
            qp.drawLine(QLine(*start, *end))
            if self.need_arrow:
                ar1, ar2 = self.create_arrow(end_pos=end_pos)
                qp.drawLines(ar1, ar2)
            return True
