from PyQt5 import QtWidgets
from PyQt5 import QtCore

import sys

from core import Core

from managers.widget_manager import WidgetManager
from managers.arrow_manager import ArrowManager
from managers.file_manager import FileManager
from managers.grid_manager import GridManager

from zero_point import ZeroPointWidget
from object_class import ObjectClass
from mouse import Mouse
from settings_widget import SettingsWindow
from utils import except_hook


class Manager:
    OFFSET_MAGNET = 5

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.core = Core(self)

        self.mouse = Mouse()
        self.zero_point_dot = ZeroPointWidget(parent=self.core, manager=self)
        self.zero_point_dot.setGeometry(self.core.width() // 2, self.core.height() // 2, 1, 1)

        self.widget_manager = WidgetManager(self)
        self.arrow_manager = ArrowManager(self)
        self.file_manager = FileManager(self)
        self.grid_manager = GridManager(self)

        self.magnet_lines = []
        self.drag_or_resize = 0
        self.active_arrow = None

        self.settings_window = SettingsWindow(self.core, self)
        self.core.__init_ui__()
        self.core.show()

    def resize_magnet_checker(self, obj: ObjectClass, pos: QtCore.QPoint) \
            -> (int, int, int, int, dict):
        """
        checks whether object has magnetic lines to other objects while resizing
        :param obj: object for check
        :param pos: future position of widget
        :return: (x, y, width, height) of object, (x, y) was modified and
                 dict with struct widget = (way by x line, way by y line)
        """
        self.magnet_lines = []
        obj_x1 = obj.x()
        obj_y1 = obj.y()
        obj_x2 = pos.x()
        obj_y2 = pos.y()
        x_mod = y_mod = False
        widgets = {}
        for widget in self.widget_manager.get_all_widgets():
            way_x = way_y = None
            if widget == obj:
                continue
            x1, y1 = widget.geometry().x(), widget.geometry().y()
            x2, y2 = x1 + widget.geometry().width(), y1 + widget.geometry().height()
            if x1 - self.OFFSET_MAGNET <= obj_x2 <= x1 + self.OFFSET_MAGNET:
                obj_x2 = x1
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - self.OFFSET_MAGNET <= obj_x2 <= x2 + self.OFFSET_MAGNET:
                obj_x2 = x2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, x2, (obj_y1 + obj_y2) // 2
                ))
            if y1 - self.OFFSET_MAGNET <= obj_y2 <= y1 + self.OFFSET_MAGNET:
                obj_y2 = y1
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y2 - self.OFFSET_MAGNET <= obj_y2 <= y2 + self.OFFSET_MAGNET:
                obj_y2 = y2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))

            if way_y or way_x:
                widgets[widget] = way_x, way_y
        return obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets

    def drag_magnet_checker(self, obj: ObjectClass) -> (int, int, int, int, bool, bool, dict):
        """
        checks whether object has magnetic lines to other objects while moving
        :param obj: object for check
        :return: (x, y, width, height) of object, (x, y) was modified and
                 dict with struct widget = (way by x line, way by y line)
        """
        self.magnet_lines = []
        obj_x1 = obj.x()
        obj_y1 = obj.y()
        obj_x2 = obj_x1 + obj.geometry().width()
        obj_y2 = obj_y1 + obj.geometry().height()
        x_mod = y_mod = False
        # widget: x, y
        widgets = {}
        for widget in self.widget_manager.get_all_widgets():
            way_x = way_y = None
            if widget == obj:
                continue
            x1, y1 = widget.geometry().x(), widget.geometry().y()
            x2, y2 = x1 + widget.geometry().width(), y1 + widget.geometry().height()
            if x1 - self.OFFSET_MAGNET <= obj_x1 <= x1 + self.OFFSET_MAGNET:
                obj_x1 = x1
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x1 - self.OFFSET_MAGNET <= obj_x2 <= x1 + self.OFFSET_MAGNET:
                obj_x1 = x1 - obj.geometry().width()
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - self.OFFSET_MAGNET <= obj_x1 <= x2 + self.OFFSET_MAGNET:
                obj_x1 = x2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, obj_x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - self.OFFSET_MAGNET <= obj_x2 <= x2 + self.OFFSET_MAGNET:
                obj_x1 = x2 - obj.geometry().width()
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, x2, (obj_y1 + obj_y2) // 2
                ))
            if (x1 + x2) // 2 - self.OFFSET_MAGNET <= (obj_x1 + obj_x2) // 2 \
                    <= (x1 + x2) // 2 + self.OFFSET_MAGNET:
                obj_x1 = (x1 + x2) // 2 - obj.geometry().width() // 2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, (y1 + y2) // 2, (x1 + x2) // 2, (obj_y1 + obj_y2) // 2
                ))
            if y1 - self.OFFSET_MAGNET <= obj_y1 <= y1 + self.OFFSET_MAGNET:
                obj_y1 = y1
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y1 - self.OFFSET_MAGNET <= obj_y2 <= y1 + self.OFFSET_MAGNET:
                obj_y1 = y1 - obj.geometry().height()
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y2 - self.OFFSET_MAGNET <= obj_y1 <= y2 + self.OFFSET_MAGNET:
                obj_y1 = y2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))
            if y2 - self.OFFSET_MAGNET <= obj_y2 <= y2 + self.OFFSET_MAGNET:
                obj_y1 = y2 - obj.geometry().height()
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))
            if (y1 + y2) // 2 - self.OFFSET_MAGNET <= (obj_y1 + obj_y2) // 2 \
                    <= (y1 + y2) // 2 + self.OFFSET_MAGNET:
                obj_y1 = (y1 + y2) // 2 - obj.geometry().height() // 2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, (y1 + y2) // 2, (obj_x1 + obj_x2) // 2, (y1 + y2) // 2
                ))
            if way_y or way_x:
                widgets[widget] = way_x, way_y
        return obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets

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

    def set_new_zero_point_pos(self, x: int, y: int):
        """
        sets new zero point's position to (x, y)
        """
        self.zero_point_dot.set_zero(x, y)

    def get_dor(self) -> int:
        """
        :return: object drag or resize at the moment by user
        drag = 1
        resize = 2
        """
        return self.drag_or_resize

    def set_dor(self, dor: int):
        """
        set drag or resize:
        drag = 1
        resize = 2
        you can use DRAG and RESIZE constants from constants.py
        """
        self.drag_or_resize = dor

    def update_core(self):
        self.core.update()


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = Manager()
    sys.exit(app.app.exec())
