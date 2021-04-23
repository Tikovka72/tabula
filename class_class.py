from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

from object_class import ObjectClass


class ClassClass(ObjectClass):
    STANDARD_SIZE = 80, 95

    def __init__(self, parent):
        super().__init__(parent)

    def __init_ui__(self):
        self.setMaximumSize(*ObjectClass.STANDARD_SIZE)
        super().__init_ui__()
        self.setMaximumSize(600, 500)
        self.setSizePolicy(QSizePolicy())
        self.info = QtWidgets.QTextEdit(self)
        self.info.move(0, self.STANDARD_SIZE[1])
        self.info.setStyleSheet(f"border-radius: 5px; border: 1px solid black; font-size: 16px")
        self.info.hide()
        self.resize_event(*self.STANDARD_SIZE)

    def resize_event(self, x, height):
        x = max(x, self.STANDARD_SIZE[0])
        height = max(height, self.STANDARD_SIZE[1])
        self.resize(x, height)
        self.edit_line.resize(self.size().width() - self.OFFSET * 2,
                              self.edit_line.height())

        self.edit_line_font.setPixelSize(int(self.edit_line.size().height() * self.FONT_SIZE_FACTOR))
        self.edit_line.setFont(self.edit_line_font)
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())
        self.info.setGeometry(self.OFFSET, self.OFFSET * 2 + self.edit_line.height(),
                              self.size().width() - self.OFFSET * 2,
                              self.height() - self.OFFSET * 3 - self.edit_line.height())

        self.update_arrows()
