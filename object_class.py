from PyQt5.QtWidgets import QLineEdit, QWidget, QMenu, QAction, QLabel
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QContextMenuEvent, QCursor, QMouseEvent

from arrow_class import Arrow


class LineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.text_size_menu = 12     # px
        self.border_radius = 5  # %
        self.background_color = "white"
        self.background_color_menu = "white"
        self.background_color_menu_selected = "rgb(128, 166, 255)"
        self.setMouseTracking(True)
        self.__init_ui__()

    def __init_ui__(self):
        self.setStyleSheet(
            "QLineEdit {"
            f"border-radius: {self.border_radius}%;"
            f"border: 1px solid black;"
            "}"
        )
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.self_menu_show)
        self.menu = QMenu(self)
        self.menu.addAction("Копировать", self.copy, shortcut="Ctrl+C")
        self.menu.addAction("Дублировать объект", self.parent().copy_self)
        self.menu.addAction("На задний план", self.on_back)
        self.menu.addAction("Вставить", self.paste, shortcut="Ctrl+V")
        self.menu.addAction("Добавить связь", self.parent().add_arrow_f)
        self.menu.addAction("Добавить стрелку", lambda: self.parent().add_arrow_f(True))
        self.menu.addAction("Удалить", self.parent().del_self)
        self.menu.setStyleSheet(
            "QMenu {"
            f"font-size: {self.text_size_menu}px;"
            f"background-color: {self.background_color_menu};"
            f"border-radius: {self.border_radius}%;"
            f"border: 1px solid black;"
            "}"
            "QMenu::selected {"
            f"background-color: {self.background_color_menu_selected};"
            "};"
        )

    def on_back(self):
        self.parent().on_back()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent().show_angles()
            self.parent().check_and_set_arrow()

    def self_menu_show(self):
        self.menu.exec_(QCursor.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.change_parent_mouse_pos(event)

    def change_parent_mouse_pos(self, event: QMouseEvent):
        self.parent().change_parent_mouse_pos(event, need_offset=True)


class ObjectClass(QWidget):
    clicked = pyqtSignal()

    OFFSET = 5
    FONT_SIZE_FACTOR = 0.80
    STANDARD_SIZE = (80, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.arrows = []
        self.__init_ui__()

    def __init_ui__(self):
        self.resize(*self.STANDARD_SIZE)

        self.edit_line = LineEdit(self)
        self.edit_line.setGeometry(self.OFFSET, self.OFFSET,
                                   self.size().width() - self.OFFSET * 2,
                                   self.size().height() - self.OFFSET * 2)
        self.edit_line_font = self.edit_line.font()
        self.edit_line_font.setPixelSize(int(self.edit_line.size().height() * self.FONT_SIZE_FACTOR))
        self.edit_line.setFont(self.edit_line_font)
        self.edit_line.setAlignment(Qt.AlignCenter)

        self.size_or_pos_label = QLabel(self)
        self.size_or_pos_label.setText("")
        self.size_or_pos_label_font = self.size_or_pos_label.font()
        self.size_or_pos_label_font.setPixelSize(12)
        self.size_or_pos_label.setFont(self.size_or_pos_label_font)
        self.size_or_pos_label.setStyleSheet("background-color: rgb(200, 200, 200); padding: 3px")
        self.size_or_pos_label.adjustSize()

        self.size_or_pos_label.move(
            self.width() // 2 - self.size_or_pos_label.width() // 2,
            self.height() // 2 - self.size_or_pos_label.height() // 2
        )

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

    def check_and_set_arrow(self):
        arrow: Arrow or None = self.check_have_active_arrow()
        if arrow:
            if arrow.obj1 == self:
                return
            if self.have_arrow_with(arrow.obj1):
                return
            arrow.obj2 = self
            self.parent().arrows[arrow]["obj2"] = self
            arrow.set_start_and_end_pos_by_obj()
            self.arrows.append(arrow)
            self.parent().toggle_have_active_arrow()

    def del_self(self):
        for arrow in self.arrows:
            objects = self.parent().arrows.get(arrow, None)
            if objects:
                obj1, obj2 = objects.get("obj1", None), objects.get("obj2", None),
            else:
                return
            if obj1 and obj1 != self:
                obj1.arrows.pop(obj1.arrows.index(arrow))
            elif obj2 and obj2 != self:
                obj2.arrows.pop(obj2.arrows.index(arrow))
            self.parent().arrows.pop(arrow)
        self.arrows = []
        self.parent().widgets.pop(self.parent().widgets.index(self))
        self.setEnabled(False)
        self.hide()

    def on_back(self):
        [(widget.raise_()) if widget != self else ... for widget in self.parent().widgets]

    def resize_event(self, x, y):
        x = max(x, self.STANDARD_SIZE[0])
        y = max(y, self.STANDARD_SIZE[1])
        self.resize(x, y)
        self.edit_line.resize(self.size().width() - self.OFFSET * 2,
                              self.size().height() - self.OFFSET * 2)

        self.edit_line_font.setPixelSize(int(self.edit_line.size().height() * self.FONT_SIZE_FACTOR))
        self.edit_line.setFont(self.edit_line_font)
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())
        self.show_size_or_pos_label()
        self.set_size_or_pos_label(f"{x}x{y}")
        self.update_arrows()

    def move_event(self, x, y):
        self.move(x, y)
        self.show_size_or_pos_label()
        self.set_size_or_pos_label(f"{x}x{y}")

    def set_size_or_pos_label(self, text):
        self.size_or_pos_label.setText(text)
        self.size_or_pos_label.adjustSize()
        self.size_or_pos_label.move(
            self.width() // 2 - self.size_or_pos_label.width() // 2,
            self.height() // 2 - self.size_or_pos_label.height() // 2
        )

    def hide_size_or_pos_label(self):
        self.size_or_pos_label.hide()

    def show_size_or_pos_label(self):
        self.size_or_pos_label.show()

    def add_arrow_f(self, need_arrow=False):
        arrow = Arrow(need_arrow=need_arrow)
        arrow.obj1 = self
        self.parent().toggle_have_active_arrow(arrow)
        self.parent().add_arrow(arrow)
        self.arrows.append(arrow)

    def update_arrows(self):
        for arrow in self.arrows:
            arrow.set_start_and_end_pos_by_obj()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mime = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)
        else:
            self.change_parent_mouse_pos(event)

    def change_parent_mouse_pos(self, event, need_offset=False):
        self.parent().change_mouse_pos(self.x() + event.x() + (self.OFFSET if need_offset else 0),
                                       self.y() + event.y() + (self.OFFSET if need_offset else 0))

    def show_angles(self):
        if self.resize_angle:
            self.resize_angle.show()
        if self.drag_angle:
            self.drag_angle.show()

    def hide_angles(self):
        if self.resize_angle:
            self.resize_angle.hide()
        if self.drag_angle:
            self.drag_angle.hide()

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            self.show_angles()
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def check_have_active_arrow(self):
        return self.parent().check_have_active_arrow()

    def toggle_have_active_arrow(self):
        self.parent().toggle_have_active_arrow()

    def have_arrow_with(self, obj):
        for arrow in self.parent().arrows:
            if arrow.obj1 and arrow.obj2:
                if (arrow.obj1 == obj and arrow.obj2 == self) or \
                        (arrow.obj1 == self and arrow.obj2 == obj):
                    return True
        return False

    def copy_self(self):
        copy = ObjectClass(self.parent())
        copy.resize_event(self.width(), self.height())
        copy.edit_line.setText(self.edit_line.text())
        copy.arrows = []
        copy.move(self.geometry().x() + self.geometry().width() // 2 - 10,
                  self.geometry().y() + self.geometry().height() + 10)
        self.parent().widgets.append(copy)
        copy.show()
