from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager
    from objects.text_widget import TextWidget

from PyQt5 import QtWidgets

from objects.arrow import Arrow


class ArrowManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.widget_manager = self.manager.widget_manager
        # Arrow: {obj1: ObjectClass, obj2: ObjectClass}
        self.arrows = {}
        self.active_arrow = None

    def add_arrow(self, arrow: Arrow):
        """
        adds arrow to dict self.arrows
        :param arrow: arrow that you want to add to dict
        :return:
        """
        self.arrows[arrow] = {"obj1": arrow.obj1, "obj2": arrow.obj2}
        obj1, obj2 = (self.widget_manager.widgets.get(arrow.obj1, None),
                      self.widget_manager.widgets.get(arrow.obj2, None))
        if obj1:
            self.widget_manager.widgets[obj1]["out"].append(arrow)
        if obj2:
            self.widget_manager.widgets[obj2]["in"].append(arrow)

    def get_all_arrows(self):
        """
        returns all of arrows that it contains self.arrows
        :return: all arrows
        """
        return self.arrows.keys()

    def toggle_active_arrow(self, arrow=None):
        """
        toggles active arrow (arrow for which settings window is enabled)
        :param arrow: arrow, for which you want to enable settings
               or clear this window if arrow is None
        """
        self.active_arrow = arrow

    def get_active_arrow(self) -> Arrow:
        """
        gets active arrow (arrow for which settings window is enabled)
        :return:
        """
        return self.active_arrow

    def get_all_arrows_from_object(self, obj: TextWidget) -> list:
        """
        gets all arrows linked  with "obj" widget
        :param obj: widget for which you need to get arrows
        :return: list of these arrows, or empty list if widget isn't in self.widgets
        """
        if self.widget_manager.widgets.get(obj, None):
            return self.widget_manager.widgets.get(obj)["in"] + \
                   self.widget_manager.widgets.get(obj)["out"]
        return []

    def get_arrows_with(self, obj1, obj2):
        """
        checks if objects are linked
        :return: True if objects are linked else False
        """
        obj1_arrows = self.get_all_arrows_from_object(obj1)
        obj2_arrows = self.get_all_arrows_from_object(obj2)
        len_lists_arrows = len(obj1_arrows + obj2_arrows)
        len_sets_arrows = len(set(obj1_arrows + obj2_arrows))
        if len_lists_arrows == len_sets_arrows:
            return False
        return True

    def set_obj1_arrow(self, arrow: Arrow, obj: TextWidget):
        """
        sets arrow's first object
        """
        if self.arrows.get(arrow, None):
            self.arrows.get(arrow)["obj1"] = obj
            arrow.obj1 = obj
            self.widget_manager.widgets.get(obj)["out"].append(arrow)

    def set_obj2_arrow(self, arrow: Arrow, obj: TextWidget):
        """
        sets arrow's second object
        """
        if self.arrows.get(arrow, None):
            self.arrows.get(arrow)["obj2"] = obj
            arrow.obj2 = obj
            self.widget_manager.widgets.get(obj)["in"].append(arrow)

    def delete_arrow(self, arrow: Arrow):
        """
        deletes arrow from self.arrows and all links with this arrow
        """
        objects = self.arrows.get(arrow, {"obj1": None, "obj2": None})
        obj1, obj2 = objects["obj1"], objects["obj2"]
        if obj1:
            obj1_arrows = self.widget_manager.widgets.get(obj1)
            if arrow in obj1_arrows["out"]:
                obj1_arrows["out"].pop(obj1_arrows["out"].index(arrow))
        if obj2:
            obj2_arrows = self.widget_manager.widgets.get(obj2)
            if arrow in obj2_arrows["in"]:
                obj2_arrows["in"].pop(obj2_arrows["in"].index(arrow))
        self.arrows.pop(arrow) if self.arrows.get(arrow, False) else None

    def change_arrow_color(self, arrow: Arrow):
        """
        IN PROCESS

        calls dialog, that changes arrow's color

        IN PROCESS
        """
        color = QtWidgets.QColorDialog(self.manager.core)
        color.setStyleSheet("border : 2px solid blue;")
        color = color.getColor()
        if color.isValid():
            arrow.color = color.name()

    def clear_focus_arrows(self):
        """
        clears focus from all arrows
        """
        [arr.clear_focus() for arr in self.arrows]
