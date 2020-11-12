import sys
from PyQt5 import QtWidgets, QtGui, QtCore

from edit_line import ObjectClass


class Core(QtWidgets.QWidget):
    def __init__(self):

        super().__init__()
        self.widgets = []
        self.arrows = []
        self.__init_ui__()
        self.mouse_x = 0
        self.mouse_y = 0
        self.drag_or_resize = 0
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

    def __init_ui__(self):
        self.showMaximized()
        self.setWindowTitle("shemer")
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.self_menu_show)
        self.setStyleSheet("background-color: white")

    def self_menu_show(self):
        pos = (self.mouse_x, self.mouse_y)
        context_menu = QtWidgets.QMenu()

        context_menu.addAction('Подробнее', lambda: self.add_label(pos))
        context_menu.addAction('Удалить', self.a)
        context_menu.exec_(QtGui.QCursor.pos())

    def add_label(self, pos):
        label = ObjectClass(self)
        label.move(pos[0], pos[1])
        label.show()
        self.widgets.append(label)

    def a(self):
        ...

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_x, self.mouse_y = event.x(), event.y()

    def dragEnterEvent(self, event):
        x, y = event.pos().x() - event.source().pos().x(), event.pos().y() - event.source().pos().y()
        if 0 <= x <= event.source().OFFSET and 0 <= y <= event.source().OFFSET:
            self.drag_or_resize = 1
        elif event.source().size().width() - event.source().OFFSET \
                <= x <= \
                event.source().size().width() and \
                event.source().size().height() - event.source().OFFSET \
                <= y <= \
                event.source().size().height():
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
        elif self.drag_or_resize == 2:
            x, y = event.pos().x() - event.source().pos().x(), \
                   event.pos().y() - event.source().pos().y()
            event.source().resize_event(x, y)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        for widget in self.widgets:
            widget.resize_angle.hide()
            widget.drag_angle.hide()
        self.setFocus()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    weather_app = Core()
    weather_app.show()
    sys.exit(app.exec())
