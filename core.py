import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor, QPen

from object_class import ObjectClass
from class_class import ClassClass


class Core(QtWidgets.QWidget):
    OFFSET_MAGNET = 5

    def __init__(self):

        super().__init__()
        self.widgets = []
        # arrowObject: [Obj1, Obj2]
        self.arrows = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.drag_or_resize = 0
        self.active_arrow = None
        self.arrow_menu = False
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.magnet_lines = []
        self.__init_ui__()

    def __init_ui__(self):
        self.showMaximized()
        self.setWindowTitle("shemer")
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setStyleSheet("background-color: white; "
                           "QPushButton {border: 1px solid white; border-radius: 5%}")

    def self_menu_show(self):
        pos = (self.mouse_x, self.mouse_y)
        context_menu = QtWidgets.QMenu()

        context_menu.addAction('Добавить объект',
                               lambda: self.create_object(pos))
        context_menu.addAction('Добавить класс',
                               lambda: self.create_class(pos))
        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        context_menu.exec_(QtGui.QCursor.pos())

    def arrow_menu_show(self, arrow):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction("Изменить цвет", lambda: self.change_arrow_color(arrow))
        context_menu.addAction('Удалить стрелку', lambda: self.delete_arrow(arrow),
                               shortcut=QtCore.Qt.Key_D)
        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        context_menu.exec_(QtGui.QCursor.pos())

    def change_arrow_color(self, arrow):
        color = QtWidgets.QColorDialog(self)
        color.setStyleSheet("border : 2px solid blue;")
        color.getColor(
            parent=self,

        )
        try:
            color_hex = color.name().lstrip("#")
            color_rgb = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
            arrow.color = color_rgb
        except Exception:
            pass

    def delete_arrow(self, arrow):
        widgets = self.arrows[arrow]
        if widgets["obj1"]:
            widgets["obj1"].arrows.pop(widgets["obj1"].arrows.index(arrow))
        if widgets["obj2"]:
            widgets["obj2"].arrows.pop(widgets["obj2"].arrows.index(arrow))
        self.arrows.pop(arrow)

    def create_object(self, pos):
        label = ObjectClass(self)
        label.move(pos[0], pos[1])
        label.show()
        self.widgets.append(label)

    def create_class(self, pos):
        cl = ClassClass(self)
        cl.move(*pos)
        cl.show()
        self.widgets.append(cl)

    def toggle_have_active_arrow(self, active_arrow=None):
        self.active_arrow = active_arrow

    def check_have_active_arrow(self):
        return self.active_arrow

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_x, self.mouse_y = event.x(), event.y()

    def dragEnterEvent(self, event):
        x, y = event.pos().x() - event.source().pos().x(), event.pos().y() - event.source().pos().y()
        if 0 <= x <= event.source().OFFSET + 5 and 0 <= y <= event.source().OFFSET + 5:
            self.drag_or_resize = 1
            event.source().show_size_or_pos_label()
        elif event.source().size().width() - event.source().OFFSET - 5 \
                <= x <= \
                event.source().size().width() + 5 and \
                event.source().size().height() - event.source().OFFSET - 5 \
                <= y <= \
                event.source().size().height() + 5:
            self.drag_or_resize = 2
            event.source().show_size_or_pos_label()

        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.magnet_lines = []
        event.pos()
        event.pos().x() - event.source().size().width() // 2,
        event.pos().y() - event.source().size().height() // 2
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        self.drag_or_resize = 0
        [widget.hide_size_or_pos_label() for widget in self.widgets]

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        obj = event.source()
        modifier_pressed = QtWidgets.QApplication.keyboardModifiers()
        shift_pressed = (modifier_pressed & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier
        if self.drag_or_resize == 1:
            event.source().move(event.pos().x() - obj.OFFSET // 2, event.pos().y() - obj.OFFSET // 2)
            x, y, _, _, x_mod, y_mod, widgets = self.drag_magnet_checker(obj)

            if shift_pressed:
                if not x_mod:
                    x = max(x - x % (self.OFFSET_MAGNET * 2), 0)
                if not y_mod:
                    y = max(y - y % (self.OFFSET_MAGNET * 2), 0)
            self.set_coords_on_widgets(widgets, event, x, y)
            event.source().move_event(x, y)
            event.source().update_arrows()
        elif self.drag_or_resize == 2:
            obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets = \
                self.resize_magnet_checker(obj, event.pos())
            x, y = obj_x2 - obj_x1, obj_y2 - obj_y1
            if shift_pressed:
                if not x_mod:
                    x = max(x - x % (self.OFFSET_MAGNET * 2), 0)
                if not y_mod:
                    y = max(y - y % (self.OFFSET_MAGNET * 2), 0)
            self.set_coords_on_widgets(widgets, event, x, y)
            event.source().resize_event(x, y)

    def set_coords_on_widgets(self, widgets, event, x, y):
        [widget.hide_size_or_pos_label() for widget in self.widgets]
        for widget, (way_x, way_y) in widgets.items():
            widget.show_size_or_pos_label()
            widget.set_size_or_pos_label(
                "{} {}".format(str(str(abs((x + event.source().width() // 2) - way_x)
                                       if way_x else '') + '↔') if way_x else '',
                               str(str(abs((y + event.source().height() // 2) - way_y)
                                       if way_y else '') + '↕') if way_y else '')
            )

    @staticmethod
    def check_on_arrow(x1, y1, x2, y2, x3, y3):
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx = x3 - x1
        dy = y3 - y1
        s = dx1 * dy - dx * dy1
        ab = (dx1 * dx1 + dy1 * dy1) ** 0.5
        h = s / ab
        return h

    def resize_magnet_checker(self, obj, pos):
        self.magnet_lines = []
        obj_x1 = obj.x()
        obj_y1 = obj.y()
        obj_x2 = pos.x()
        obj_y2 = pos.y()
        x_mod = y_mod = False
        widgets = {}
        for widget in self.widgets:
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
        for widget in self.widgets:
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

            if way_y or way_x:
                widgets[widget] = way_x, way_y
        return obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.RightButton:
            if self.active_arrow:
                self.active_arrow.obj1.arrows.pop \
                    (self.active_arrow.obj1.arrows.index(self.active_arrow))
                self.arrows.pop(self.active_arrow)
                self.active_arrow = None
                return
            for arrow in self.arrows:
                if arrow.start_pos and arrow.end_pos:
                    x1, y1 = arrow.start_pos
                    x2, y2 = arrow.end_pos
                    x3, y3 = event.pos().x(), event.pos().y()
                    if self.check_on_arrow(x1, y1, x2, y2, x3, y3) < 3:
                        self.arrow_menu_show(arrow)
                        return
            self.self_menu_show()

        for widget in self.widgets:
            widget.hide_angles()
        self.setFocus()

    def add_arrow(self, arrow):
        self.arrows[arrow] = {"obj1": arrow.obj1, "obj2": arrow.obj2}

    def change_mouse_pos(self, x, y):
        self.mouse_x, self.mouse_y = x, y

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)

        for arrow in self.arrows.keys():
            qp.setPen(QPen(QColor(*arrow.color), 2))
            end = (self.mouse_x, self.mouse_y)
            qp.drawLine(arrow.generate_draw_objects(end))
            if arrow.need_arrow:
                arrows = arrow.create_arrow(end)
                qp.drawLine(arrows[0])
                qp.drawLine(arrows[1])
        pen = QPen(QColor(100, 100, 100), 1, )
        pen.setStyle(QtCore.Qt.DashLine)
        qp.setPen(pen)

        for line in self.magnet_lines:
            qp.drawLine(line)
        qp.end()
        self.update()

    def delete_widget(self, sender):
        if sender in self.widgets:
            self.widgets.pop(self.widgets.index(sender))
        del sender


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        weather_app = Core()
        weather_app.show()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
