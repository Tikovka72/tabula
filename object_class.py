from PyQt5.QtWidgets import QLineEdit, QWidget, QMenu, QAction, QLabel, QCheckBox, QSlider
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QDrag, QContextMenuEvent, QCursor, QMouseEvent, QWheelEvent

from arrow_class import Arrow
from settings import Settings
from zero_dot import ZeroPointDotWidget


class LineEdit(QLineEdit):
    FONT_SIZE_FACTOR = 0.80

    def __init__(self, parent):
        super().__init__(parent)
        self.text_size_menu = 12     # px
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
        self.menu.addAction("Дублировать объект", self.parent().copy_self)
        self.menu.addAction("На задний план", self.on_back)
        self.menu.addAction("Настройки", self.settings_show)
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

    def self_menu_show(self):
        self.menu.exec_(QCursor.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.change_parent_mouse_pos(event)

    def change_parent_mouse_pos(self, event: QMouseEvent):
        self.parent().change_parent_mouse_pos(event, need_offset=True)

    def settings_show(self):
        self.parent().settings_show()

    def resize(self, x, y) -> None:
        super().resize(x, y)
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
        self.fact_pos = 0, 0
        if pos:
            self.move(*pos)
        self.__init_ui__()

    def __init_ui__(self):
        self.resize(*self.STANDARD_SIZE)
        self.fact_pos = self.x(), self.y()

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
        self.settings = Settings(self, self.edit_line.text())
        self.settings.add_settings(Settings.Title, name="Размер и расположение объекта")

        self.settings.add_settings(Settings.SettTwoLineEdit, name="Размер",
                                   standard_values=(self.size().width(), self.size().height()),
                                   int_only=True,
                                   default_values_to_return=(self.size().width(),
                                                             self.size().height()),
                                   call_back=(self.call_back_size_width, self.call_back_size_height),
                                   call_update_all=self.call_set_size)
        self.settings.add_settings(Settings.SettTwoLineEdit, name="Положение",
                                   standard_values=(self.x(), self.y()),
                                   int_only=True,
                                   default_values_to_return=(self.x(), self.y()),
                                   call_back=(self.call_back_pos_x, self.call_back_pos_y),
                                   call_update_all=self.call_set_pos)
        self.settings.add_settings(Settings.Line)
        self.settings.add_settings(Settings.Title, name="Текст")
        self.settings.add_settings(Settings.SettCheckboxLineEdit, name="Размер шрифта",
                                   standard_values=(("Авто", True),
                                                    self.edit_line.get_text_size()),
                                   int_only=True,
                                   default_values_to_return=(True, self.edit_line.get_text_size()),
                                   call_back=(self.call_back_text_auto, self.call_back_text_size),
                                   call_update_all=self.call_set_text_size)
        self.settings.add_settings(Settings.Line)
        self.settings.add_settings(Settings.Title, name="Рамка")
        self.settings.add_settings(Settings.SettTwoLineEdit, name="Размер и радиус рамки",
                                   standard_values=self.edit_line.get_border(),
                                   int_only=True,
                                   default_values_to_return=(0, 1),
                                   call_back=(self.call_back_border_size,
                                              self.call_back_border_radius),
                                   call_update_all=self.call_set_border)
        self.settings.add_settings(Settings.Line)

        self.settings.add_settings(Settings.Title, name="Линии")

    def settings_show(self):
        self.settings.show()

    def return_to_fact_pos(self):
        self.move_animation((self.x() - self.zero_dot.get_pos()[0] + self.zero_dot.zero[0],
                             self.y() - self.zero_dot.get_pos()[1] + self.zero_dot.zero[1]))

    def move_animation(self, end_pos):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QRect(*end_pos, self.width(), self.height()))

        self.anim.start()

    def set_new_fact_pos(self, x, y):
        self.fact_pos = x, y

    def call_back_size_width(self, width):
        self.resize_event(width, self.height(), False)

    def call_back_size_height(self, height):
        self.resize_event(self.width(), height, False)

    def call_set_size(self):
        return self.width(), self.height()

    def call_back_pos_x(self, x):
        self.move_event(self.zero_dot.get_pos()[0] + x, self.y(), False)
        self.set_new_fact_pos(x, self.y())

    def call_back_pos_y(self, y):
        self.move_event(self.x(), self.zero_dot.get_pos()[1] + y, False)
        self.set_new_fact_pos(self.x(), y)

    def call_set_pos(self):
        return -self.zero_dot.get_pos()[0] + self.x(), -self.zero_dot.get_pos()[1] + self.y()

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
        copy = ObjectClass(self.parent(), self.manager)
        copy.resize_event(self.width(), self.height())
        copy.edit_line.setText(self.edit_line.text())
        copy.move(self.geometry().x() + self.geometry().width() // 2 - 10,
                  self.geometry().y() + self.geometry().height() + 10)
        copy.hide_size_or_pos_label()
        self.manager.add_widget(copy)
        copy.show()

    def on_back(self):
        [(widget.raise_()) if widget != self else ... for widget in self.manager.widgets.keys()]

    def change_parent_mouse_pos(self, event, need_offset=False):
        self.manager.change_mouse_pos(self.x() + event.x() + (self.OFFSET if need_offset else 0),
                                      self.y() + event.y() + (self.OFFSET if need_offset else 0))

    def resize_event(self, x, y, show_size=True):
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

    def move_event(self, x, y, show_pos=True, fact_pos=False):
        self.move(x, y)
        if show_pos:
            self.show_size_or_pos_label()
            self.set_size_or_pos_label(f"{x - self.zero_dot.get_pos()[0]}x{y - self.zero_dot.get_pos()[1]}")
        if fact_pos:
            self.set_new_fact_pos(x, y)
        # self.update_arrows()

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

    def add_arrow_f(self, need_arrow=False):
        arrow = Arrow(need_arrow=need_arrow)
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
