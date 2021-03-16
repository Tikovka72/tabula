from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import Manager

from PyQt5.QtWidgets import QLineEdit, QWidget, QMenu, QLabel
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QDrag, QCursor, QMouseEvent

from arrow_class import Arrow
from zero_point import ZeroPointWidget
from constants import FROM_AND_TO_CENTER, FROM_AND_TO_NEAREST_LINE
from settings_widget import SettingsWindow


class ObjectClass(QWidget):
    clicked = pyqtSignal()

    OFFSET = 5
    FONT_SIZE_FACTOR = 0.80
    STANDARD_SIZE = (150, 40)

    def __init__(self, parent: QWidget,
                 manager: Manager,
                 zero_dot: ZeroPointWidget,
                 pos: tuple or list = None):
        """
        :param parent: core UI widget
        :param manager: main class containing all information
        :param zero_dot: widget that tracks canvas's center
        :param pos: position of object
        """
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
        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit,
                                                  name="Размер",
                                                  standard_values=(
                                                      self.size().width(), self.size().height()),
                                                  int_only=True,
                                                  default_values_to_return=(self.size().width(),
                                                                            self.size().height()),
                                                  call_back=(self.call_back_size_width,
                                                             self.call_back_size_height),
                                                  call_update_all=self.call_set_size)
        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit,
                                                  name="Положение",
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
        """
        returns self to the fact position by zero point
        """
        self.move_animation((self.x() - self.zero_dot.get_pos()[0] + self.zero_dot.zero[0],
                             self.y() - self.zero_dot.get_pos()[1] + self.zero_dot.zero[1]))

    def move_animation(self, end_pos: tuple or list):
        """
        sets move animation to end_pos
        :param end_pos: point to go to
        """
        self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QRect(*end_pos, self.width(), self.height()))

        self.anim.start()

    def call_back_size_width(self, width: int):
        """
        callback for settings window. This is necessary to change width of object
        settings window -> ObjectClass
        """
        self.resize_event(width, self.height(), False)

    def call_back_size_height(self, height):
        """
        callback for settings window. This is necessary to change height of object
        settings window -> ObjectClass
        """
        self.resize_event(self.width(), height, False)

    def call_set_size(self) -> tuple:
        """
        gives self size
        ObjectClass -> settings window
        """
        return self.width(), self.height()

    def call_back_pos_x(self, x: int):
        """
        callback for settings window. This is necessary to change x position of object
        settings window -> ObjectClass
        """
        self.move_event(self.zero_dot.get_pos()[0] + x - self.width() // 2, self.y(), False)

    def call_back_pos_y(self, y: int):
        """
        callback for settings window. This is necessary to change y position of object
        settings window -> ObjectClass
        """
        self.move_event(self.x(), self.zero_dot.get_pos()[1] + y - self.height() // 2, False)

    def call_set_pos(self) -> tuple:
        """
        gives self position
        ObjectClass -> settings window
        """
        return -self.zero_dot.get_pos()[0] + self.x() + self.width() // 2, \
               -self.zero_dot.get_pos()[1] + self.y() + self.height() // 2

    def call_back_text_size(self, size: int):
        """
        callback for settings window. This is necessary to change text size
        settings window -> ObjectClass
        """
        self.edit_line.change_text_size(size)
        self.edit_line.update_text_size()

    def call_back_text_auto(self, st: bool):
        """
        callback for settings window. This is necessary
        to change whether the font size is set automatically
        settings window -> ObjectClass
        """
        self.edit_line.change_auto(st)
        self.edit_line.update_text_size()

    def call_set_text_size(self):
        """
        callback for settings window. This is necessary to change text size
        settings window -> ObjectClass
        """
        return self.edit_line.get_auto(), self.edit_line.get_text_size()

    def call_back_border_radius(self, radius: int):
        """
        callback for settings window. This is necessary to change border radius
        settings window -> ObjectClass
        """
        self.edit_line.set_border(radius=radius)

    def call_back_border_size(self, size: int):
        """
        callback for settings window. This is necessary to change text size
        settings window -> ObjectClass
        """
        self.edit_line.set_border(size=size)

    def call_set_border(self) -> tuple:
        """
        gives self border size and radius
        ObjectClass -> settings window
        """
        return self.edit_line.get_border()

    def del_self(self):
        """
        deletes self
        """
        self.manager.delete_widget(self)
        self.setEnabled(False)
        self.hide()
        self.manager.delete_obj(self)

    def copy_self(self):
        """
        makes self duplicate
        """
        copy = ObjectClass(self.parent(), self.manager, self.zero_dot)
        copy.resize_event(self.width(), self.height())
        copy.edit_line.setText(self.edit_line.text())
        copy.move_event(self.geometry().x() + self.geometry().width() // 2 - 10,
                        self.geometry().y() + self.geometry().height() + 10, show_pos=False)
        copy.hide_size_or_pos_label()
        self.manager.add_widget(widget=copy)
        copy.show()

    def on_back(self):
        """
        moves self on back
        """
        self.lower()

    def change_parent_mouse_pos(self, event: QMouseEvent, need_offset: bool = False):
        """
        changes mouse point for parent. needs for drag event
        """
        self.manager.change_mouse_pos(self.x() + event.x() + (self.OFFSET if need_offset else 0),
                                      self.y() + event.y() + (self.OFFSET if need_offset else 0))

    def resize_event(self, width: int, height: int, show_size: bool = True):
        """
        resizes self
        :param width: width
        :param height: height
        :param show_size: shows size in small window
               in widget's center in {width}x{height} format or not
        """
        if width < 1 or height < 1:
            return
        self.resize(width, height)
        self.edit_line.resize(self.size().width() - self.OFFSET * 2,
                              self.size().height() - self.OFFSET * 2)
        self.resize_angle.setGeometry(self.size().width() - self.OFFSET,
                                      self.size().height() - self.OFFSET,
                                      self.size().width(), self.size().height())
        if show_size:
            self.show_size_or_pos_label()
            self.set_size_or_pos_label(f"{width}x{height}")
        self.update_arrows()
        self.manager.settings_window.update_obj_settings(self)

    def move_event(self, x: int, y: int, show_pos: bool = True):
        """
        moves self
        :param x: new x position
        :param y: new y position
        :param show_pos: shows position on the centre of widget
        """
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
        """
        sets text on center of widget
        """
        self.size_or_pos_label.setText(text)
        self.size_or_pos_label.adjustSize()
        self.size_or_pos_label.move(
            self.width() // 2 - self.size_or_pos_label.width() // 2,
            self.height() // 2 - self.size_or_pos_label.height() // 2
        )

    def hide_size_or_pos_label(self):
        """
        hides text on center of widget
        """
        self.size_or_pos_label.hide()

    def show_size_or_pos_label(self):
        """
        shows text on center of widget
        """
        self.size_or_pos_label.show()

    def check_and_set_arrow(self):
        """
        with clicking on widget this widget checks active arrows and if there is active arrow,
        widget sets self as second object
        """
        arrow: Arrow or None = self.manager.get_active_arrow()
        if arrow:
            if arrow.obj1 == self:
                return
            if self.manager.get_arrows_with(self, arrow.obj1):
                return
            self.manager.set_obj2_arrow(arrow, self)
            self.manager.toggle_active_arrow()
            arrow.set_start_and_end()

    def add_arrow_f(self, need_arrow: bool = False, arrow_type: int = FROM_AND_TO_NEAREST_LINE):
        """
        adds arrow from this widget
        :param need_arrow: needs arrow on end (---- or --->)
        :param arrow_type: type of arrow
        """
        arrow = Arrow(manager=self.manager, need_arrow=need_arrow, arrow_type=arrow_type)
        self.manager.toggle_active_arrow(arrow)
        self.manager.add_arrow(arrow)
        self.manager.set_obj1_arrow(arrow, self)

    def update_arrows(self):
        """
        updates position of all widget's arrows
        """
        for arrow in self.manager.get_all_arrows_from_object(self):
            arrow.set_start_and_end()

    def check_have_active_arrow(self) -> Arrow:
        """
        checks if app has active arrow. needs to transfer this to LineEdit
        manager -> widget -> line edit
        """
        return self.manager.get_active_arrow()

    def toggle_have_active_arrow(self):
        """
        toggles active arrow. needs to transfer this to LineEdit
        manager -> widget -> line edit
        """
        self.manager.toggle_active_arrow()

    def have_arrow_with(self, obj: ObjectClass) -> bool:
        """
        checks if this object has arrow with other object
        :param obj: other object to check
        """
        return self.manager.get_arrows_with(self, obj)

    def show_angles(self):
        """
        shows angles for moving and resizing
        """
        if self.resize_angle:
            self.resize_angle.show()
        if self.drag_angle:
            self.drag_angle.show()

    def hide_angles(self):
        """
        hides angles for moving and resizing
        """
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

    def data(self) -> str:
        """
        :return: data from LineEdit
        """
        return self.edit_line.text()

    def set_data(self, data: str):
        """
        sets your text in LineEdit
        :param data: your text
        """
        self.edit_line.setText(data)


class LineEdit(QLineEdit):
    FONT_SIZE_FACTOR = 0.80

    def __init__(self, parent: ObjectClass):
        """
        :param parent: widget
        """
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
        """
        sends signal to parent for move widget on back
        """
        self.parent().on_back()

    def change_text_size(self, size: int = None):
        """
        changes size for text, but doesn't change it. for setting new size - self.update_text_size()
        :param size: size of text. if None, size will be change with widget's size
        """
        self.text_size = size

    def update_text_size(self):
        """
        updates font's size
        """
        if self.auto:
            size = int(self.size().height() * self.FONT_SIZE_FACTOR)
        else:
            size = self.text_size
        self.font_.setPixelSize(size)
        self.setFont(self.font_)

    def change_auto(self, st: bool = True):
        """
        if text size sets automatically or not
        """
        self.auto = st

    def get_auto(self) -> bool:
        """
        :return: text size sets automatically
        """
        return self.auto

    def get_text_size(self) -> int:
        """
        :return: text size at the moment
        """
        return self.font_.pixelSize()

    def set_border(self, size: int = None, radius: int = None):
        """
        sets border parameters: width and radius of border
        :param size: border's width. default if parameter is None
        :param radius: border's radius. default if parameter is None
        """
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

    def get_border(self) -> tuple:
        """
        :return: size and radius of borer in size: str, radius: str
        """
        style = self.styleSheet()
        style = "".join(style.split())
        radius_index = style.rfind("border-radius:") + len("border-radius:")
        radius = style[radius_index:style[radius_index:].find("%") + radius_index]
        size_index = style.rfind("border:") + len("border:")
        size = style[size_index:style[size_index:].find("px") + size_index]
        return size if size.isdigit() else "0", radius if radius.isdigit() else "0"

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent().manager.settings_window.hide_all_sett()
            self.parent().manager.clear_focus()
            self.parent().manager.clear_focus_arrows()
            self.parent().show_angles()
            self.parent().check_and_set_arrow()
            self.parent().hide_size_or_pos_label()

            self.parent().manager.settings_window.show_sett(self.parent())

    def self_menu_show(self):
        """
        method for showing context menu
        """
        self.menu.exec_(QCursor.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.RightButton:
            mime = QMimeData()
            drag = QDrag(self.parent())
            drag.setMimeData(mime)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)
        else:
            self.change_parent_mouse_pos(event)

    def change_parent_mouse_pos(self, event: QMouseEvent):
        self.parent().change_parent_mouse_pos(event, need_offset=True)

    def resize(self, *size) -> None:
        super().resize(*size)
        self.update_text_size()
