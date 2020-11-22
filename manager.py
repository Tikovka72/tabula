from PyQt5 import QtWidgets
from PyQt5 import QtCore

from zero_dot import ZeroPointDotWidget
from grid import Grid
from object_class import ObjectClass
from mouse import Mouse


class Manager:
    OFFSET_MAGNET = 5

    def __init__(self, core):
        self.core = core
        # Arrow: {obj1: ObjectClass, obj2: ObjectClass}
        self.arrows = {}
        # ObjectClass: {in: Arrow, out: Arrow}
        self.widgets = {}
        self.magnet_lines = []
        self.drag_or_resize = 0
        self.active_arrow = None
        self.zero_point_dot = ZeroPointDotWidget(parent=self.core, manager=self)
        self.zero_point_dot.setGeometry(self.core.width() // 2, self.core.height() // 2, 1, 1)
        self.grid = Grid(show=True, core_size=(self.core.width(), self.core.height()),
                         zero_pos=self.zero_point_dot)
        self.mouse = Mouse()
        # self.core.showMaximized()

    def add_widget(self, pos=None, widget=None):
        if widget is None:
            widget = ObjectClass(self.core, self, pos=pos if pos else (0, 0),
                                 zero_dot=self.zero_point_dot)
        widget.show()
        self.widgets[widget] = {"in": [], "out": []}

    def add_arrow(self, arrow):
        self.arrows[arrow] = {"obj1": arrow.obj1, "obj2": arrow.obj2}
        obj1, obj2 = self.widgets.get(arrow.obj1, None), self.widgets.get(arrow.obj2, None)
        if obj1:
            self.widgets[obj1]["out"].append(arrow)
        if obj2:
            self.widgets[obj2]["in"].append(arrow)

    def get_all_widgets(self):
        return self.widgets.keys()

    def get_all_arrows(self):
        return self.arrows.keys()

    def toggle_active_arrow(self, arrow=None):
        self.active_arrow = arrow

    def get_active_arrow(self):
        return self.active_arrow

    def get_in_arrows_from_object(self, obj):
        if self.widgets.get(obj, None):
            return self.widgets.get(obj)["in"]
        return []

    def get_out_arrows_from_object(self, obj):
        if self.widgets.get(obj, None):
            return self.widgets.get(obj)["out"]
        return []

    def get_all_arrows_from_object(self, obj):
        if self.widgets.get(obj, None):
            return self.widgets.get(obj)["in"] + self.widgets.get(obj)["out"]
        return []

    def get_arrows_with(self, obj1, obj2):
        obj1_arrows = self.get_all_arrows_from_object(obj1)
        obj2_arrows = self.get_all_arrows_from_object(obj2)
        len_lists_arrows = len(obj1_arrows + obj2_arrows)
        len_sets_arrows = len(set(obj1_arrows + obj2_arrows))
        if len_lists_arrows == len_sets_arrows:
            return False
        return True

    def set_obj1_arrow(self, arrow, obj):
        if self.arrows.get(arrow, None):
            self.arrows.get(arrow)["obj1"] = obj
            arrow.obj1 = obj
            self.widgets.get(obj)["out"].append(arrow)

    def set_obj2_arrow(self, arrow, obj):
        if self.arrows.get(arrow, None):
            self.arrows.get(arrow)["obj2"] = obj
            arrow.obj2 = obj
            self.widgets.get(obj)["in"].append(arrow)

    def delete_arrow(self, arrow):
        objects = self.arrows.get(arrow, {"obj1": None, "obj2": None})
        obj1, obj2 = objects["obj1"], objects["obj2"]
        if obj1:
            obj1_arrows = self.widgets.get(obj1)
            if arrow in obj1_arrows["out"]:
                obj1_arrows["out"].pop(obj1_arrows["out"].index(arrow))
        if obj2:
            obj2_arrows = self.widgets.get(obj2)
            if arrow in obj2_arrows["in"]:
                obj2_arrows["in"].pop(obj2_arrows["in"].index(arrow))
        self.arrows.pop(arrow)

    def delete_widget(self, obj):
        arrows = self.get_all_arrows_from_object(obj)
        for arrow in arrows:
            self.delete_arrow(arrow)
        self.widgets.pop(obj)

    def change_arrow_color(self, arrow):
        color = QtWidgets.QColorDialog(self.core)
        color.setStyleSheet("border : 2px solid blue;")
        color = color.getColor()
        if color.isValid():
            arrow.color = color.name()

    def set_coords_on_widgets(self, widgets, event, x, y):
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
            
    def resize_magnet_checker(self, obj, pos):
        self.magnet_lines = []
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

    def drag_magnet_checker(self, obj):
        self.magnet_lines = []
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

    def get_magnet_lines(self):
        return self.magnet_lines

    def drop_magnet_lines(self):
        self.magnet_lines = []

    def get_mouse_pos(self):
        return self.mouse.get_pos()

    def get_mouse_x(self):
        return self.mouse.get_x()

    def get_mouse_y(self):
        return self.mouse.get_y()

    def change_mouse_pos(self, x, y):
        self.mouse.change_pos(x, y)

    def change_mouse_x(self, x):
        self.mouse.change_x(x)

    def change_mouse_y(self, y):
        self.mouse.change_y(y)

    def set_new_zero_point_pos(self, x, y):
        self.zero_point_dot.set_zero(x, y)

    def get_dor(self):
        return self.drag_or_resize

    def set_dor(self, dor):
        self.drag_or_resize = dor

    def check_and_set_grid_magnet_lines_for_resizing(
            self, obj, x, y, x_mod=False, y_mod=False, widgets=None
    ):
        if widgets is None:
            widgets = {}
        x_left = self.grid.get_nearest_x_line_by_offset(obj.x())
        x_center = self.grid.get_nearest_x_line_by_offset(obj.x() + obj.width() // 2)
        x_right = self.grid.get_nearest_x_line_by_offset(obj.x() + obj.width())
        y_left = self.grid.get_nearest_y_line_by_offset(obj.y())
        y_center = self.grid.get_nearest_y_line_by_offset(
            obj.y() + obj.height() // 2)
        y_right = self.grid.get_nearest_y_line_by_offset(obj.y() + obj.height())
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
