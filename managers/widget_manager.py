from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager

from PyQt5 import QtGui, QtCore

from objects.text_widget import TextWidget

from constants import OFFSET_MAGNET


class WidgetManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        # ObjectClass: {in: Arrow, out: Arrow}
        self.widgets = {}
        self.drag_or_resize = 0
        self.drag_dot = 0, 0
        self.dragged_obj = None

    def add_widget(self, pos: tuple or list = None, widget: TextWidget = None) -> TextWidget:
        """
        method for adding widget in dict with all widgets (self.widgets).
        if widget was passed, this manager will add this widget to dict self.widgets
        if widget wasn't passed, this manager will create new widget for dict and
            set position "pos" for this new widget, if "pos" wasn't passed,
            "pos" will set to  (0, 0)
        :param pos: pos of widget
        :param widget: object_class.ObjectClass
        :return: this widget
        """
        if widget is None:
            widget = TextWidget(self.manager.core, self, pos=pos if pos else (0, 0),
                                zero_dot=self.manager.grid_manager.zero_point_dot)
        widget.show()
        self.widgets[widget] = {"in": [], "out": []}
        self.manager.settings_window.hide_all_sett()
        self.manager.settings_window.show_sett(widget)
        return widget

    def get_all_widgets(self):
        """
        returns all of widgets that it contains self.widgets
        :return: all widgets
        """
        return self.widgets.keys()

    def delete_widget(self, obj: TextWidget):
        """
        deletes widget from self.widgets and all arrows that were linked with it
        """
        arrows = self.manager.arrow_manager.get_all_arrows_from_object(obj)
        for arrow in arrows:
            # TODO check exception
            try:
                self.manager.arrow_manager.delete_arrow(arrow)
            except Exception:
                ...
        self.widgets.pop(obj)

    def set_coords_on_widgets(self, widgets: list or tuple,
                              event: QtGui.QDragMoveEvent, x: int, y: int):
        """
        sets label for widgets with distance to some widget
        :param widgets: widgets that need label
        :param event: event for position of mouse
        :param x: x coordinate of main widget
        :param y: y coordinate of main widget
        """
        [widget.hide_size_or_pos_label() for widget in self.get_all_widgets()]
        for widget, (way_x, way_y) in widgets.items():
            if way_x or way_y:
                widget.show_size_or_pos_label()
                widget.set_size_or_pos_label(
                    "{} {}".format(str(str(abs((x + event.source().width() // 2) - way_x)
                                           if way_x else '') + '↔') if way_x else '',
                                   str(str(abs((y + event.source().height() // 2) - way_y)
                                           if way_y else '') + '↕') if way_y else '')
                )

    def clear_focus(self):
        """
        clears focus and hides angles from all widgets
        """
        [(w.clearFocus(), w.hide_angles()) for w in self.widgets]

    def delete_obj(self, obj):
        _ = obj  # for use parameter (PEP8)
        del obj
        self.manager.core.update()

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

    def resize_magnet_checker(self, obj: TextWidget, pos: QtCore.QPoint) \
            -> (int, int, int, int, dict):
        """
        checks whether object has magnetic lines to other objects while resizing
        :param obj: object for check
        :param pos: future position of widget
        :return: (x, y, width, height) of object, (x, y) was modified and
                 dict with struct widget = (way by x line, way by y line)
        """
        self.manager.magnet_lines = []
        obj_x1 = obj.x()
        obj_y1 = obj.y()
        obj_x2 = pos.x()
        obj_y2 = pos.y()
        x_mod = y_mod = False
        widgets = {}
        for widget in self.get_all_widgets():
            way_x = way_y = None
            if widget == obj:
                continue
            x1, y1 = widget.geometry().x(), widget.geometry().y()
            x2, y2 = x1 + widget.geometry().width(), y1 + widget.geometry().height()
            if x1 - OFFSET_MAGNET <= obj_x2 <= x1 + OFFSET_MAGNET:
                obj_x2 = x1
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - OFFSET_MAGNET <= obj_x2 <= x2 + OFFSET_MAGNET:
                obj_x2 = x2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, x2, (obj_y1 + obj_y2) // 2
                ))
            if y1 - OFFSET_MAGNET <= obj_y2 <= y1 + OFFSET_MAGNET:
                obj_y2 = y1
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y2 - OFFSET_MAGNET <= obj_y2 <= y2 + OFFSET_MAGNET:
                obj_y2 = y2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))

            if way_y or way_x:
                widgets[widget] = way_x, way_y
        return obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets

    def drag_magnet_checker(self, obj: TextWidget) -> (int, int, int, int, bool, bool, dict):
        """
        checks whether object has magnetic lines to other objects while moving
        :param obj: object for check
        :return: (x, y, width, height) of object, (x, y) was modified and
                 dict with struct widget = (way by x line, way by y line)
        """
        self.manager.magnet_lines = []
        obj_x1 = obj.x()
        obj_y1 = obj.y()
        obj_x2 = obj_x1 + obj.geometry().width()
        obj_y2 = obj_y1 + obj.geometry().height()
        x_mod = y_mod = False
        # widget: x, y
        widgets = {}
        for widget in self.get_all_widgets():
            way_x = way_y = None
            if widget == obj:
                continue
            x1, y1 = widget.geometry().x(), widget.geometry().y()
            x2, y2 = x1 + widget.geometry().width(), y1 + widget.geometry().height()
            if x1 - OFFSET_MAGNET <= obj_x1 <= x1 + OFFSET_MAGNET:
                obj_x1 = x1
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x1 - OFFSET_MAGNET <= obj_x2 <= x1 + OFFSET_MAGNET:
                obj_x1 = x1 - obj.geometry().width()
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x1, (y1 + y2) // 2, x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - OFFSET_MAGNET <= obj_x1 <= x2 + OFFSET_MAGNET:
                obj_x1 = x2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, obj_x1, (obj_y1 + obj_y2) // 2
                ))
            if x2 - OFFSET_MAGNET <= obj_x2 <= x2 + OFFSET_MAGNET:
                obj_x1 = x2 - obj.geometry().width()
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    x2, (y1 + y2) // 2, x2, (obj_y1 + obj_y2) // 2
                ))
            if (x1 + x2) // 2 - OFFSET_MAGNET <= (obj_x1 + obj_x2) // 2 \
                    <= (x1 + x2) // 2 + OFFSET_MAGNET:
                obj_x1 = (x1 + x2) // 2 - obj.geometry().width() // 2
                way_y = (y2 + y1) // 2
                x_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, (y1 + y2) // 2, (x1 + x2) // 2, (obj_y1 + obj_y2) // 2
                ))
            if y1 - OFFSET_MAGNET <= obj_y1 <= y1 + OFFSET_MAGNET:
                obj_y1 = y1
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y1 - OFFSET_MAGNET <= obj_y2 <= y1 + OFFSET_MAGNET:
                obj_y1 = y1 - obj.geometry().height()
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y1, (obj_x1 + obj_x2) // 2, y1
                ))
            if y2 - OFFSET_MAGNET <= obj_y1 <= y2 + OFFSET_MAGNET:
                obj_y1 = y2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))
            if y2 - OFFSET_MAGNET <= obj_y2 <= y2 + OFFSET_MAGNET:
                obj_y1 = y2 - obj.geometry().height()
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, y2, (obj_x1 + obj_x2) // 2, y2
                ))
            if (y1 + y2) // 2 - OFFSET_MAGNET <= (obj_y1 + obj_y2) // 2 \
                    <= (y1 + y2) // 2 + OFFSET_MAGNET:
                obj_y1 = (y1 + y2) // 2 - obj.geometry().height() // 2
                way_x = (x2 + x1) // 2
                y_mod = True
                self.manager.magnet_lines.append(QtCore.QLine(
                    (x1 + x2) // 2, (y1 + y2) // 2, (obj_x1 + obj_x2) // 2, (y1 + y2) // 2
                ))
            if way_y or way_x:
                widgets[widget] = way_x, way_y
        return obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets

    def widget_has_focus_or_none(self) -> TextWidget or None:
        """
        bring first widget that haas focus else None
        :return: widget or none
        """
        for w in self.widgets:
            if w.hasFocus():
                return w
        return None
