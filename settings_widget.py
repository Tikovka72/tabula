from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QWheelEvent

from utils import pass_f, isdig


class Label(QtWidgets.QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        effect = QtWidgets.QGraphicsColorizeEffect(self)
        self.setGraphicsEffect(effect)
        self.color = ((0, 0, 0), (255, 255, 255))
        self.color_selected = 0
        self.anim = QtCore.QPropertyAnimation(effect, b"color")
        self.anim.setDuration(300)

    def change_color(self):
        self.anim.setStartValue(QtGui.QColor(*self.color[self.color_selected]))
        self.anim.setEndValue(QtGui.QColor(*self.color[abs(self.color_selected - 1)]))
        self.color_selected = abs(self.color_selected - 1)
        self.anim.start()

    def setText(self, a0: str) -> None:
        self.change_color()
        super().setText(a0)
        self.change_color()


class BackButton(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.text_field = Label(self)

    def setText(self, text: str) -> None:
        self.text_field.setText(text)
        self.text_field.adjustSize()
        self.text_field.move(self.width() // 2 - self.text_field.width() // 2 - 1,
                             self.height() // 2 - self.text_field.height() // 2 - 1)
        self.update()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        self.setText(self.text_field.text())


class SettingsWindow(QtWidgets.QWidget):
    MENU_SIZE_X = 300
    STANDARD_SIZE = 300, 400
    OFFSET = 10
    STANDARD_SIZE_FOR_WIDGETS = STANDARD_SIZE[0] - 2 * OFFSET, OFFSET * 2

    class Line(QtWidgets.QWidget):
        SIZE = (450, 20)
        OFFSET = 10
        LINE_HEIGHT = 2

        def __init__(self, parent,
                     n: int,
                     name: str,
                     size: tuple,
                     standard_values=None, int_only=None,
                     default_values_to_return=None, call_back=None, call_update_all=None):
            super().__init__(parent)
            self.parent = parent
            self.n = n
            self.size = size
            _ = name, standard_values, int_only, default_values_to_return, call_back, call_update_all
            self.__init_ui__()

        def __init_ui__(self):
            self.resize(*self.size)
            self.move(self.parent.width() // 2 - self.width() // 2, self.OFFSET * (self.n + 1)
                      + self.height() * self.n)
            self.line = QtWidgets.QWidget(self)
            self.line.move(self.OFFSET, self.height() // 2 - self.LINE_HEIGHT // 2)
            self.line.resize(self.width() - 2 * self.OFFSET, self.LINE_HEIGHT)
            self.line.setStyleSheet("background-color: rgb(200, 200, 200)")

    class Title(QtWidgets.QWidget):
        SIZE = (450, 20)
        OFFSET = 10

        def __init__(self, parent,
                     n: int,
                     name: str,
                     size: tuple,
                     standard_values=None, int_only=None,
                     default_values_to_return=None, call_back=None, call_update_all=None):
            super().__init__(parent)
            self.parent = parent
            self.n = n
            self.name = name
            self.size = size
            _ = standard_values, int_only, default_values_to_return, call_back, call_update_all
            self.__init_ui__()

        def __init_ui__(self):
            self.resize(*self.size)
            self.move(self.parent.width() // 2 - self.width() // 2, self.OFFSET * (self.n + 1)
                      + self.SIZE[1] * self.n)
            self.text = QtWidgets.QLabel(self)
            self.text.setText(str(self.name))
            f = self.text.font()
            f.setPixelSize(self.height() - 2)
            self.text.setFont(f)
            self.text.adjustSize()
            self.text.move(
                self.width() // 2 - self.text.width() // 2,
                self.height() // 2 - self.text.height() // 2
            )

    class SettTwoLineEdit(QtWidgets.QWidget):
        VALUES_N = 2
        SIZE = (450, 20)
        OFFSET = 10
        FIELDS_SIZE = 50, 20
        STANDARD_SIZE = 150, 40

        def __init__(self, parent,
                     n: int,
                     name: str,
                     standard_values: tuple,
                     size: tuple,
                     int_only: bool = False,
                     default_values_to_return: tuple = tuple(),
                     call_back: tuple = tuple(),
                     call_update_all=None):
            super().__init__(parent)
            self.parent = parent
            self.n = n
            self.name = name
            self.standard_values = standard_values if len(standard_values) == self.VALUES_N else None
            self.size = size
            self.int_only = int_only
            self.default_values_to_return = default_values_to_return if \
                len(default_values_to_return) == self.VALUES_N else (pass_f, pass_f)
            self.call_back = call_back if len(call_back) == self.VALUES_N else (pass_f, pass_f)
            self.call_update_all = call_update_all
            self.__init_ui__()

        def __init_ui__(self):
            self.resize(*self.size)
            self.move(self.parent.width() // 2 - self.width() // 2, self.OFFSET * (self.n + 1)
                      + self.SIZE[1] * self.n)
            self.text = QtWidgets.QLabel(self)
            self.text.setText(str(self.name))
            self.text.adjustSize()
            self.text.move(self.OFFSET, self.height() // 2 - self.text.height() // 2)

            value1 = value2 = None
            if self.standard_values:
                value1, value2 = self.standard_values
            self.value1 = QtWidgets.QLineEdit(self)
            self.value1.resize(*self.FIELDS_SIZE)
            self.value1.setText(str(value1))
            self.value1.move(self.width() - self.FIELDS_SIZE[0] * 2 - self.OFFSET * 2,
                             self.height() // 2 - self.value1.height() // 2)
            self.value1.textChanged.connect(self.value1_changed)
            self.value2 = QtWidgets.QLineEdit(self)
            self.value2.resize(*self.FIELDS_SIZE)
            self.value2.setText(str(value2))
            self.value2.move(self.width() - self.FIELDS_SIZE[0] - self.OFFSET,
                             self.height() // 2 - self.value2.height() // 2)
            self.value2.textChanged.connect(self.value2_changed)
            self.show()

        def value1_changed(self):
            new_value1 = "".join([sym if (sym.isdigit() or (sym == "-" and i == 0)
                                          if self.int_only else True)
                                  else "" for i, sym in enumerate(self.value1.text())])
            self.value1.setText(new_value1)
            if self.call_back[0]:
                self.call_back[0](self.value1_get())

        def value2_changed(self):
            new_value2 = "".join([sym if (sym.isdigit() or (sym == "-" and i == 0)
                                          if self.int_only else True)
                                  else "" for i, sym in enumerate(self.value2.text())])
            self.value2.setText(new_value2)
            if self.call_back[1]:
                self.call_back[1](self.value2_get())

        def value1_get(self):
            value = self.value1.text()
            if self.int_only:
                if isdig(value):
                    return int(value)
                return self.default_values_to_return[0]
            if value:
                return value
            return self.default_values_to_return[0]

        def value2_get(self):
            value = self.value2.text()
            if self.int_only:
                if isdig(value):
                    return int(value)
                return self.default_values_to_return[1]
            if value:
                return value
            return self.default_values_to_return[1]

        def value1_set(self, value):
            self.value1.setText(str(value))

        def value2_set(self, value):
            self.value2.setText(str(value))

        def update(self) -> None:
            super().update()
            if self.call_update_all:
                value1, value2 = self.call_update_all()
                self.value1_set(value1)
                self.value2_set(value2)

        def wheelEvent(self, event: QWheelEvent) -> None:
            if not self.int_only:
                return
            if event.angleDelta().y() < 0:
                p = -1
            else:
                p = 1
            if self.value1.underMouse():
                self.value1.setText(
                    str(int(self.value1.text() if self.value1.text() else
                            self.standard_values[0]) + p))
            elif self.value2.underMouse():
                self.value2.setText(
                    str(int(self.value2.text() if self.value2.text() else
                            self.standard_values[1]) + p))

    class SettCheckboxLineEdit(QtWidgets.QWidget):
        VALUES_N = 2
        SIZE = (450, 20)
        OFFSET = 10
        FIELDS_SIZE = 50, 20
        STANDARD_SIZE = 150, 40

        def __init__(self, parent,
                     n: int,
                     name: str,
                     standard_values: tuple,
                     size: tuple,
                     int_only: bool = False,
                     default_values_to_return: tuple = tuple(),
                     call_back: tuple = tuple(),
                     call_update_all=None,
                     lock_line_edit=True):
            super().__init__(parent)
            self.parent = parent
            self.n = n
            self.name = name
            self.standard_values = standard_values if len(standard_values) == self.VALUES_N else None
            self.size = size
            self.int_only = int_only
            self.default_values_to_return = default_values_to_return if \
                len(default_values_to_return) == self.VALUES_N else (None, None)
            self.call_back = call_back if len(call_back) == self.VALUES_N else (pass_f, pass_f)
            self.call_update_all = call_update_all
            self.lock_line_edit = lock_line_edit
            self.__init_ui__()

        def __init_ui__(self):
            self.resize(*self.size)
            self.move(self.parent.width() // 2 - self.width() // 2, self.OFFSET * (self.n + 1)
                      + self.SIZE[1] * self.n)
            self.text = QtWidgets.QLabel(self)
            self.text.setText(str(self.name))
            self.text.adjustSize()
            self.text.move(self.OFFSET, self.height() // 2 - self.text.height() // 2)

            value1 = (None, None)
            value2 = None
            if self.standard_values:
                value1, value2 = self.standard_values
            self.value1 = QtWidgets.QCheckBox(self)
            self.value1.resize(*self.FIELDS_SIZE)
            self.value1.setText(str(value1[0]))
            if value1[1]:
                if not self.value1.isChecked():
                    self.value1.toggle()
            else:
                if self.value1.isChecked():
                    self.value1.toggle()
            self.value1.move(self.width() - self.FIELDS_SIZE[0] * 2 - self.OFFSET * 2,
                             self.height() // 2 - self.value1.height() // 2)
            self.value1.stateChanged.connect(self.value1_changed)

            self.value2 = QtWidgets.QLineEdit(self)
            self.value2.resize(*self.FIELDS_SIZE)
            self.value2.setText(str(value2))
            self.value2.move(self.width() - self.FIELDS_SIZE[0] - self.OFFSET,
                             self.height() // 2 - self.value2.height() // 2)
            self.value2.textChanged.connect(self.value2_changed)
            if self.value1 and self.lock_line_edit:
                self.value2.setEnabled(False)
            self.show()

        def value1_changed(self):
            if self.lock_line_edit:
                if self.value1.isChecked():
                    self.value2.setEnabled(False)
                else:
                    self.value2.setEnabled(True)
            if self.call_back[0]:
                self.call_back[0](self.value1_get())

        def value2_changed(self):
            new_value2 = "".join([i if (i.isdigit() if self.int_only else True)
                                  else "" for i in self.value2.text()])
            self.value2_set(new_value2)
            if self.call_back[1] and (not self.value1_get() and self.lock_line_edit or True):
                self.call_back[1](self.value2_get())

        def value1_get(self):
            return self.value1.isChecked()

        def value2_get(self):
            value = self.value2.text()
            if self.int_only:
                if value.isdigit():
                    return int(value)
                return self.standard_values[1]
            if value:
                return value
            return self.standard_values[1]

        def value1_set(self, value):
            if value:
                if not self.value1.isChecked():
                    self.value1.toggle()
            else:
                if self.value1.isChecked():
                    self.value1.toggle()

        def value2_set(self, value):
            self.value2.setText(str(value))

        def wheelEvent(self, event: QWheelEvent) -> None:
            if not self.int_only or not self.value2.isEnabled():
                return
            if event.angleDelta().y() < 0:
                p = -1
            else:
                p = 1
            if self.value2.underMouse():
                self.value2.setText(
                    str(int(self.value2.text() if self.value2.text() else
                            self.standard_values[1]) + p))

        def update(self) -> None:
            super().update()
            if self.call_update_all:
                value1, value2 = self.call_update_all()
                self.value1_set(value1)
                self.value2_set(value2)

    class SettOneLineEdit(QtWidgets.QWidget):
        VALUES_N = 1
        SIZE = (450, 20)
        OFFSET = 10
        FIELDS_SIZE = 50, 20
        STANDARD_SIZE = 150, 40

        def __init__(self, parent,
                     n: int,
                     name: str,
                     standard_values: tuple,
                     size: tuple,
                     int_only: bool = False,
                     default_values_to_return: tuple = tuple(),
                     call_back: tuple = tuple(),
                     call_update_all=None):
            super().__init__(parent)
            self.parent = parent
            self.n = n
            self.name = name
            self.standard_values = standard_values if len(standard_values) == self.VALUES_N else None
            self.size = size
            self.int_only = int_only
            self.default_values_to_return = default_values_to_return if \
                len(default_values_to_return) == self.VALUES_N else (None, None)
            self.call_back = call_back if len(call_back) == self.VALUES_N else (pass_f, None)
            self.call_update_all = call_update_all
            self.__init_ui__()

        def __init_ui__(self):
            self.resize(*self.size)
            self.move(self.parent.width() // 2 - self.width() // 2, self.OFFSET * (self.n + 1)
                      + self.SIZE[1] * self.n)
            self.text = QtWidgets.QLabel(self)
            self.text.setText(str(self.name))
            self.text.adjustSize()
            self.text.move(self.OFFSET, self.height() // 2 - self.text.height() // 2)

            value1 = None
            if self.standard_values:
                value1 = self.standard_values[0]
            self.value1 = QtWidgets.QLineEdit(self)
            self.value1.resize(*self.FIELDS_SIZE)
            self.value1.setText(str(value1))
            self.value1.move(self.width() - self.FIELDS_SIZE[0] * 2 - self.OFFSET * 2,
                             self.height() // 2 - self.value1.height() // 2)
            self.value1.textChanged.connect(self.value1_changed)
            self.show()

        def value1_changed(self):
            new_value1 = "".join([i if (i.isdigit() if self.int_only else True)
                                  else "" for i in self.value1.text()])
            self.value1.setText(new_value1)
            if self.call_back[0]:
                self.call_back[0](self.value1_get())

        def value1_get(self):
            value = self.value1.text()
            if self.int_only:
                if value.isdigit():
                    return int(value)
                return self.standard_values[0]
            if value:
                return value
            return self.standard_values[0]

        def value1_set(self, value):
            self.value1.setText(str(value))

        def update(self) -> None:
            super().update()
            if self.call_update_all:
                value = self.call_update_all()
                self.value1_set(value)

        def wheelEvent(self, event: QWheelEvent) -> None:
            if not self.int_only:
                return
            if event.angleDelta().y() < 0:
                p = -1
            else:
                p = 1
            if self.value1.underMouse():
                self.value1.setText(
                    str(int(self.value1.text() if self.value1.text() else
                            self.standard_values[0]) + p))

    def __init__(self, parent):
        super().__init__(parent)
        self.objects = {parent: [2, []]}
        self.show_ = True
        self.__init_ui__()

    def __init_ui__(self):
        self.widget = QtWidgets.QWidget(self)
        self.widget.setStyleSheet("background-color: white")
        self.anim = QtCore.QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.hide_menu_button = BackButton(self.parent())
        self.hide_menu_button.setStyleSheet("QPushButton {border: 1px solid #ddd; "
                                            "border-radius: 15%;}"
                                            "QPushButton::hover {background-color: #eee}")
        self.hide_menu_button.setText("→")
        self.hide_menu_button.show()
        self.hide_menu_button.clicked.connect(self.toggle_show)
        self.set_geometry()

    def set_geometry(self):
        if self.show_:
            self.setGeometry(self.parent().width() - self.MENU_SIZE_X, 0,
                             self.MENU_SIZE_X, self.parent().height())
            self.widget.setGeometry(0, 0, self.width(), self.height())
            self.hide_menu_button.setGeometry(self.parent().width() - 10 - 30, 10, 30, 30)
        else:
            self.setGeometry(self.parent().width(), 0,
                             self.MENU_SIZE_X, self.parent().height())
            self.widget.setGeometry(0, 0, self.width(), self.height())
            self.hide_menu_button.setGeometry(self.parent().width() - 10 - 30, 10, 30, 30)

    def toggle_show(self):
        if self.x() == self.parent().width():
            self.move_animation((self.parent().width() - self.MENU_SIZE_X, 0))
            self.hide_menu_button.setText("→")
        else:
            self.move_animation((self.parent().width(), 0))
            self.hide_menu_button.setText("←")
        self.show_ = not self.show_

    def move_animation(self, end_pos):
        self.anim.setStartValue(QtCore.QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QtCore.QRect(*end_pos, self.width(), self.height()))

        self.anim.start()

    def add_settings(self, obj, sett,
                     name="",
                     standard_values=tuple(),
                     size=STANDARD_SIZE_FOR_WIDGETS,
                     int_only=False,
                     default_values_to_return=tuple(),
                     call_back=tuple(),
                     call_update_all=None, **kwargs):
        if obj in self.objects:
            self.objects[obj][1].append(sett(self,
                                             self.objects[obj][0],
                                             name=name,
                                             standard_values=standard_values,
                                             int_only=int_only,
                                             size=size,
                                             default_values_to_return=default_values_to_return,
                                             call_back=call_back,
                                             call_update_all=call_update_all, **kwargs))
            self.objects[obj][0] += 1
        else:
            self.objects[obj] = [3, [sett(self,
                                          2,
                                          name=name,
                                          standard_values=standard_values,
                                          int_only=int_only,
                                          size=size,
                                          default_values_to_return=default_values_to_return,
                                          call_back=call_back,
                                          call_update_all=call_update_all, **kwargs)]]

    def show_sett(self, obj) -> None:
        for sett in self.objects[obj][1]:
            sett.update()
            sett.show()

    def update_obj_settings(self, obj):
        for sett in self.objects[obj][1]:
            sett.update()

    def hide_all_sett(self):
        for _, sett in self.objects.values():
            if sett and not sett[0].isHidden():
                [s.hide() for s in sett]
        self.hide_menu_button.show()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        pass

    def raise_(self) -> None:
        super().raise_()
        self.hide_menu_button.raise_()