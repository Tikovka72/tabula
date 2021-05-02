from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager

    from objects.text_widget import TextWidget

from objects.grid import Grid
from objects.zero_point import ZeroPointWidget


class GridManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.zero_point_dot = ZeroPointWidget(parent=self.manager.core, manager=self.manager)

        self.zero_point_dot.setGeometry(
            self.manager.core.width() // 2, self.manager.core.height() // 2, 1, 1)

        self.grid = Grid(
            show=True, core_size=(self.manager.core.width(), self.manager.core.height()),
            zero_pos=self.zero_point_dot)

        self.magnet_lines = []

    # TODO doc for this
    def check_and_set_grid_magnet_lines_for_resizing(
            self, obj: TextWidget,
            x: int,
            y: int,
            x_mod: bool = False,
            y_mod: bool = False,
            widgets: dict = None
    ) -> (int, int, dict):
        """
        I don't know what it does
        :param obj:
        :param x:
        :param y:
        :param x_mod:
        :param y_mod:
        :param widgets:
        :return:
        """
        if widgets is None:
            widgets = {}
        x_left = self.grid.get_nearest_y_line_by_offset(obj.x())
        x_center = self.grid.get_nearest_y_line_by_offset(obj.x() + obj.width() // 2)
        x_right = self.grid.get_nearest_y_line_by_offset(obj.x() + obj.width())
        y_left = self.grid.get_nearest_x_line_by_offset(obj.y())

        y_center = self.grid.get_nearest_x_line_by_offset(
            obj.y() + obj.height() // 2)

        y_right = self.grid.get_nearest_x_line_by_offset(obj.y() + obj.height())
        self.grid.clear_special_lines()
        if x_left or x_center or x_right:

            x_t = (x_left.x1() if x_left else False) or \
                  (x_center.x1() - obj.width() // 2 if x_center else False) or \
                  (x_right.x1() - obj.width() if x_right else False)

            x = x_t or x
            if y_mod:
                for widget in widgets:
                    v = widgets[widget]
                    if v[0] and v[0] != x:
                        widgets[widget] = (None, v[1])

            if x_left and x == x_left.x1():
                self.grid.add_line_to_special_lines(x_left)
            if x_center and x + obj.width() // 2 == x_center.x1():
                self.grid.add_line_to_special_lines(x_center)
            if x_right and x + obj.width() == x_right.x1():
                self.grid.add_line_to_special_lines(x_right)
        if y_left or y_center or y_right:

            y_t = (y_left.y1() if y_left else False) or (
                y_center.y1() - obj.height() // 2 if y_center else False) or \
                  (y_right.y1() - obj.height() if y_right else False)

            y = y_t or y
            if x_mod:
                for widget in widgets:
                    v = widgets[widget]
                    if v[1] and v[1] != y:
                        widgets[widget] = (v[0], 0)

            if y_left and y == y_left.y1():
                self.grid.add_line_to_special_lines(y_left)
            if y_center and y + obj.height() // 2 == y_center.y1():
                self.grid.add_line_to_special_lines(y_center)
            if y_right and y + obj.height() == y_right.y1():
                self.grid.add_line_to_special_lines(y_right)

        return x, y, widgets

    def get_magnet_lines(self) -> list:
        """
        :return: all magnet lines
        """
        return self.magnet_lines

    def drop_magnet_lines(self):
        """
        drops all magnet lines
        """
        self.magnet_lines.clear()

    def set_new_zero_point_pos(self, x: int, y: int):
        """
        sets new zero point's position to (x, y)
        """
        self.zero_point_dot.set_zero(x, y)
