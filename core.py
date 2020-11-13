import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor, QPen

from object_class import ObjectClass
from class_class import ClassClass


class Core(QtWidgets.QWidget):
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
        self.__init_ui__()

    def __init_ui__(self):
        self.showMaximized()
        self.setWindowTitle("shemer")
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setStyleSheet("background-color: white")

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

        context_menu.addAction('Удалить стрелку', lambda: self.delete_arrow(arrow),
                               shortcut=QtCore.Qt.Key_D)
        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        context_menu.exec_(QtGui.QCursor.pos())

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
        elif event.source().size().width() - event.source().OFFSET - 5\
                <= x <= \
                event.source().size().width() + 5 and \
                event.source().size().height() - event.source().OFFSET -5 \
                <= y <= \
                event.source().size().height() + 5:
            self.drag_or_resize = 2

        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        event.pos()
        event.pos().x() - event.source().size().width() // 2,
        event.pos().y() - event.source().size().height() // 2
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        self.drag_or_resize = 0

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if self.drag_or_resize == 1:
            event.source().move(event.pos().x() - event.source().OFFSET // 2,
                                event.pos().y() - event.source().OFFSET // 2)
            event.source().update_arrows()
        elif self.drag_or_resize == 2:
            x, y = event.pos().x() - event.source().pos().x(), \
                   event.pos().y() - event.source().pos().y()
            event.source().resize_event(x, y)

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

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.RightButton:
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
            try:
                widget.resize_angle.hide()
                widget.drag_angle.hide()
            except Exception as e:
                pass
        self.setFocus()

    def add_arrow(self, arrow):
        self.arrows[arrow] = {"obj1": arrow.obj1, "obj2": arrow.obj2}

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(QColor(0, 0, 0), 3))
        for arrow in self.arrows.keys():
            end = (self.mouse_x, self.mouse_y)
            qp.drawLine(arrow.generate_draw_objects(end))
            if arrow.need_arrow:
                arrows = arrow.create_arrow(end)
                qp.drawLine(arrows[0])
                qp.drawLine(arrows[1])
        qp.end()
        self.update()

    def delete_widget(self, sender):
        if sender in self.widgets:
            self.widgets.pop(self.widgets.index(sender))
        print(self.widgets)
        del sender


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        weather_app = Core()
        weather_app.show()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
