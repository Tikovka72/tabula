from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag


class LineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().show_angles()


class ObjectClass(QWidget):
    clicked = pyqtSignal()

    OFFSET = 5
    FONT_SIZE_FACTOR = 0.80

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.__init_ui__()

    def __init_ui__(self):
        self.resize(80, 40)

        self.edit_line = LineEdit(self)
        self.edit_line.setGeometry(self.OFFSET, self.OFFSET,
                                   self.size().width() - self.OFFSET * 2,
                                   self.size().height() - self.OFFSET * 2)
        self.edit_line.setStyleSheet(
            f"background-color: white; "
            f"font-size: {int(self.edit_line.size().height() * self.FONT_SIZE_FACTOR)}px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"

        )
        self.edit_line.setAlignment(Qt.AlignCenter)

        self.drag_angle = QWidget(self)
        self.drag_angle.setGeometry(0, 0, self.OFFSET, self.OFFSET)
        self.drag_angle.setStyleSheet(
            "background-color: black"
        )

        self.resize_angle = QWidget(self)
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())
        self.resize_angle.setStyleSheet("background-color: black")

    def resize_event(self, x, y):
        self.resize(x, y)
        self.edit_line.setGeometry(self.OFFSET, self.OFFSET,
                                   self.size().width() - self.OFFSET * 2,
                                   self.size().height() - self.OFFSET * 2)

        self.edit_line.setStyleSheet(
            f"background-color: white; "
            f"font-size: {int(self.edit_line.size().height() * self.FONT_SIZE_FACTOR)}px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        self.drag_angle.setStyleSheet(
            "background-color: black"
        )
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mime = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)

    def show_angles(self):
        self.resize_angle.show()
        self.drag_angle.show()

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            self.show_angles()
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
