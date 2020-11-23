from PyQt5.QtWidgets import QLineEdit, QWidget, QMenu, QLabel
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QDrag, QCursor, QMouseEvent

from arrow_class import Arrow
from settings import Settings
from zero_dot import ZeroPointDotWidget
from constants import FROM_AND_TO_CENTER, FROM_AND_TO_NEAREST_LINE
from settings_widget import SettingsWindow


class LineEdit(QLineEdit):
    FONT_SIZE_FACTOR = 0.80

    def __init__(self, parent):
        super().__init__(parent)
        self.text_size_menu = 12  # px
        self.border_radius = 5  # %
        self.border_size = 1
        self.text_size = None
        self.auto = True
        self.background_color = "white"
        self.background_color_menu = "white"
        self.background_color_menu_selected = "rgb(128, 166, 255)"
        self.setMouseTracking(True)
        self.__init_ui__()

    def __init_ui__(self):
        self.setStyleSheet(
            "QLineEdit {"
            f"border-radius: {self.border_radius}%;"
            f"border: {self.border_size}px solid black;"
            "}"
        )
        self.font_ = self.font()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.self_menu_show)
        self.menu = QMenu(self)
        self.menu.addAction("Копировать текст", self.copy, shortcut="Ctrl+C")
        self.menu.addAction("Вставить", self.paste, shortcut="Ctrl+V")
        self.menu.addSeparator()
        self.menu.addAction("Дублировать объект", self.parent().copy_self)
        self.menu.addAction("На задний план", self.on_back)
        self.menu.addSeparator()
        self.menu.addAction("Добавить связь",
                            lambda: self.parent().add_arrow_f(arrow_type=FROM_AND_TO_NEAREST_LINE))
        line_menu = self.menu.addMenu("Добавить связь...")
        line_menu.addAction("от центра до центра",
                            lambda: self.parent().add_arrow_f(arrow_type=FROM_AND_TO_CENTER))
        self.menu.addAction("Добавить стрелку", lambda: self.parent().add_arrow_f(True))
        self.menu.addSeparator()
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
        self.text_size = int(self.size().height() * self.FONT_SIZE_FACTOR)
        self.update_text_size()

    def on_back(self):
        self.parent().on_back()

    def change_text_size(self, size=None):
        self.text_size = size

    def update_text_size(self):
        if self.auto:
            size = int(self.size().height() * self.FONT_SIZE_FACTOR)
        else:
            size = self.text_size
        self.font_.setPixelSize(size)
        self.setFont(self.font_)

    def change_auto(self, st=True):
        self.auto = st

    def get_auto(self):
        return self.auto

    def get_text_size(self):
        return self.font_.pixelSize()

    def set_border(self, size=None, radius=None):
        default = self.get_border()
        radius = radius if radius is not None else int(default[1])
        size = size if size is not None and size >= 0 else int(default[0])
        size = size if size >= 0 else default[0]
        radius = radius if min(self.width(), self.height()) // 2 >= radius \
            else min(self.width(), self.height()) // 2
        self.setStyleSheet(
            "QLineEdit {"
            f"border-radius: {radius}%;"
            f"{'border: ' + str(size) + 'px solid black;' if int(size) > 0 else ''}"
            "}")
        self.border_radius = radius
        self.border_size = size

    def get_border(self):
        style = self.styleSheet()
        style = "".join(style.split())
        radius_index = style.rfind("border-radius:") + len("border-radius:")
        radius = style[radius_index:style[radius_index:].find("%") + radius_index]
        size_index = style.rfind("border:") + len("border:")
        size = style[size_index:style[size_index:].find("px") + size_index]
        return size if size.isdigit() else "0", radius if radius.isdigit() else "0"

    def check_radius(self, radius):
        return min(self.width(), self.height()) // 2 - 5 >= radius

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent().show_angles()
            self.parent().check_and_set_arrow()
            self.parent().hide_size_or_pos_label()
            self.parent().manager.settings_window.hide_all_sett()
            self.parent().manager.settings_window.show_sett(self.parent())

    def self_menu_show(self):
        self.menu.exec_(QCursor.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.change_parent_mouse_pos(event)

    def change_parent_mouse_pos(self, event: QMouseEvent):
        self.parent().change_parent_mouse_pos(event, need_offset=True)

    def resize(self, *size) -> None:
        super().resize(*size)
        self.update_text_size()


class ObjectClass(QWidget):
    clicked = pyqtSignal()

    OFFSET = 5
    FONT_SIZE_FACTOR = 0.80
    STANDARD_SIZE = (150, 40)

    def __init__(self, parent, manager, zero_dot: ZeroPointDotWidget, pos=None):
        super().__init__(parent)
        self.manager = manager
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.zero_dot = zero_dot
        self.arrows = []
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        if pos:
            self.move(*pos)
        self.__init_ui__()
        self.manager.settings_window.raise_()

    def __init_ui__(self):
        self.resize(*self.STANDARD_SIZE)

        self.edit_line = LineEdit(self)
        self.edit_line.setText("Sample text")
        self.edit_line.setGeometry(self.OFFSET, self.OFFSET,
                                   self.size().width() - self.OFFSET * 2,
                                   self.size().height() - self.OFFSET * 2)
        self.edit_line_font = self.edit_line.font()
        self.edit_line.setAlignment(Qt.AlignCenter)
        self.size_or_pos_label = QLabel(self)
        self.size_or_pos_label.setText("")
        self.size_or_pos_label_font = self.size_or_pos_label.font()
        self.size_or_pos_label_font.setPixelSize(12)
        self.size_or_pos_label.setFont(self.size_or_pos_label_font)
        self.size_or_pos_label.setStyleSheet("background-color: rgb(200, 200, 200); padding: 3px")
        self.size_or_pos_label.adjustSize()
        self.size_or_pos_label.hide()

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
        self.manager.settings_window.add_settings(self, SettingsWindow.Title,
                                                  name="Размер и расположение объекта")
        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit, name="Размер",
                                                  standard_values=(
                                                  self.size().width(), self.size().height()),
                                                  int_only=True,
                                                  default_values_to_return=(self.size().width(),
                                                                            self.size().height()),
                                                  call_back=(self.call_back_size_width,
                                                             self.call_back_size_height),
                                                  call_update_all=self.call_set_size)
        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit, name="Положение",
                                                  standard_values=(self.x(), self.y()),
                                                  int_only=True,
                                                  default_values_to_return=(self.x(), self.y()),
                                                  call_back=(
                                                  self.call_back_pos_x, self.call_back_pos_y),
                                                  call_update_all=self.call_set_pos)
        self.manager.settings_window.add_settings(self, SettingsWindow.Line)
        self.manager.settings_window.add_settings(self, SettingsWindow.Title, name="Текст")
        self.manager.settings_window.add_settings(self, SettingsWindow.SettCheckboxLineEdit,
                                                  name="Размер шрифта",
                                                  standard_values=(("Авто", True),
                                                                   self.edit_line.get_text_size()),
                                                  int_only=True,
                                                  default_values_to_return=(
                                                  True, self.edit_line.get_text_size()),
                                                  call_back=(self.call_back_text_auto,
                                                             self.call_back_text_size),
                                                  call_update_all=self.call_set_text_size)
        self.manager.settings_window.add_settings(self, SettingsWindow.Line)
        self.manager.settings_window.add_settings(self, SettingsWindow.Title, name="Рамка")
        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit,
                                                  name="Размер и радиус рамки",
                                                  standard_values=self.edit_line.get_border(),
                                                  int_only=True,
                                                  default_values_to_return=(0, 1),
                                                  call_back=(self.call_back_border_size,
                                                             self.call_back_border_radius),
                                                  call_update_all=self.call_set_border)
        self.manager.settings_window.add_settings(self, SettingsWindow.Line)
        self.manager.settings_window.show_sett(self)

    def return_to_fact_pos(self):
        self.move_animation((self.x() - self.zero_dot.get_pos()[0] + self.zero_dot.zero[0],
                             self.y() - self.zero_dot.get_pos()[1] + self.zero_dot.zero[1]))

    def move_animation(self, end_pos):
        self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QRect(*end_pos, self.width(), self.height()))

        self.anim.start()

    def call_back_size_width(self, width):
        self.resize_event(width, self.height(), False)

    def call_back_size_height(self, height):
        self.resize_event(self.width(), height, False)

    def call_set_size(self):
        return self.width(), self.height()

    def call_back_pos_x(self, x):
        self.move_event(self.zero_dot.get_pos()[0] + x - self.width() // 2, self.y(), False)

    def call_back_pos_y(self, y):
        self.move_event(self.x(), self.zero_dot.get_pos()[1] + y - self.height() // 2, False)

    def call_set_pos(self):
        return -self.zero_dot.get_pos()[0] + self.x() + self.width() // 2, \
               -self.zero_dot.get_pos()[1] + self.y() + self.height() // 2

    def call_back_text_size(self, size):
        self.edit_line.change_text_size(size)
        self.edit_line.update_text_size()

    def call_back_text_auto(self, st):
        self.edit_line.change_auto(st)
        self.edit_line.update_text_size()

    def call_set_text_size(self):
        return self.edit_line.get_auto(), self.edit_line.get_text_size()

    def call_back_border_radius(self, radius):
        self.edit_line.set_border(radius=radius)

    def call_back_border_size(self, size):
        self.edit_line.set_border(size=size)

    def call_set_border(self):
        return self.edit_line.get_border()

    def del_self(self):
        self.manager.delete_widget(self)
        self.setEnabled(False)
        self.hide()

    def copy_self(self):
        copy = ObjectClass(self.parent(), self.manager, self.zero_dot)
        copy.resize_event(self.width(), self.height())
        copy.edit_line.setText(self.edit_line.text())
        copy.move_event(self.geometry().x() + self.geometry().width() // 2 - 10,
                        self.geometry().y() + self.geometry().height() + 10, show_pos=False)
        copy.hide_size_or_pos_label()
        self.manager.add_widget(widget=copy)
        copy.show()

    def on_back(self):
        self.lower()

    def change_parent_mouse_pos(self, event, need_offset=False):
        self.manager.change_mouse_pos(self.x() + event.x() + (self.OFFSET if need_offset else 0),
                                      self.y() + event.y() + (self.OFFSET if need_offset else 0))

    def resize_event(self, x, y, show_size=True):
        if x < 1 or y < 1:
            return
        self.resize(x, y)
        self.edit_line.resize(self.size().width() - self.OFFSET * 2,
                              self.size().height() - self.OFFSET * 2)
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())
        if show_size:
            self.show_size_or_pos_label()
            self.set_size_or_pos_label(f"{x}x{y}")
        self.update_arrows()
        self.manager.settings_window.update_obj_settings(self)

    def move_event(self, x, y, show_pos=True):
        self.move(x, y)
        if show_pos:
            self.show_size_or_pos_label()
            self.set_size_or_pos_label(f"{x - self.zero_dot.get_pos()[0] + self.width() // 2} "
                                       f"{y - self.zero_dot.get_pos()[1] + self.height() // 2}")
        self.manager.settings_window.update_obj_settings(self)

    def moveEvent(self, a0) -> None:
        self.move(a0.pos().x(), a0.pos().y())
        self.update_arrows()

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

    def check_and_set_arrow(self):
        arrow: Arrow or None = self.manager.get_active_arrow()
        if arrow:
            if arrow.obj1 == self:
                return
            if self.manager.get_arrows_with(self, arrow.obj1):
                return
            self.manager.set_obj2_arrow(arrow, self)
            self.manager.toggle_active_arrow()
            arrow.set_start_and_end_pos_by_obj()

    def add_arrow_f(self, need_arrow=False, arrow_type=FROM_AND_TO_NEAREST_LINE):
        arrow = Arrow(need_arrow=need_arrow, arrow_type=arrow_type)
        self.manager.toggle_active_arrow(arrow)
        self.manager.add_arrow(arrow)
        self.manager.set_obj1_arrow(arrow, self)

    def update_arrows(self):
        for arrow in self.manager.get_all_arrows_from_object(self):
            arrow.set_start_and_end_pos_by_obj()

    def check_have_active_arrow(self):
        return self.manager.get_active_arrow()

    def toggle_have_active_arrow(self):
        self.manager.toggle_active_arrow()

    def have_arrow_with(self, obj):
        return self.manager.get_arrows_with(self, obj)

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

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mime = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)
        else:
            self.change_parent_mouse_pos(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            self.show_angles()
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
