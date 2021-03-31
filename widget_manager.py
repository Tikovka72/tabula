from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5 import QtGui

if TYPE_CHECKING:
    from manager import Manager

from object_class import ObjectClass


class WidgetManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        # ObjectClass: {in: Arrow, out: Arrow}
        self.widgets = {}

    def add_widget(self, pos: tuple or list = None, widget: ObjectClass = None) -> ObjectClass:
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
            widget = ObjectClass(self.manager.core, self, pos=pos if pos else (0, 0),
                                 zero_dot=self.manager.zero_point_dot)
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

    def delete_widget(self, obj: ObjectClass):
        """
        deletes widget from self.widgets and all arrows that were linked with it
        """
        arrows = self.manager.arrow_manager.get_all_arrows_from_object(obj)
        for arrow in arrows:
            try:
                self.manager.arrow_manager.delete_arrow(arrow)
            except Exception as e:
                print(e)
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
