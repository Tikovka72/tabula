from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen

from objects.settings_widget import SettingsWindow
from objects.text_widget import TextWidget

from utils import check_on_arrow

from constants import NONE, DRAG, RESIZE, MAGNET_LINE_COLOR, OFFSET_MAGNET, CONTEXT_MENU_BORDER_COLOR


class GraphicCore(QtWidgets.QWidget):
    """
    main class with UI
    """
    STANDARD_SIZE = 640, 480
    OFFSET_MAGNET = 5

    def __init__(self, manager: Manager):
        super().__init__()
        self.qp = QPainter()
        self.manager = manager
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

    def __init_ui__(self):
        self.setWindowTitle("tabula")
        self.setMinimumSize(640, 480)
        self.resize(*self.STANDARD_SIZE)
        self.showMaximized()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setObjectName("core")
        self.setStyleSheet("QWidget#core {background-color: white}")
        self.setFocus()

        self.manager.settings_window.add_settings(self, SettingsWindow.Title,
                                                  name="Положение экрана")

        self.manager.settings_window.add_settings(self, SettingsWindow.SettTwoLineEdit,
                                                  name="Положение центра",
                                                  standard_values=self.manager.grid_manager.
                                                  zero_point_dot.get_pos(),
                                                  int_only=True,
                                                  default_values_to_return=(
                                                      self.size().width() // 2,
                                                      self.size().height() // 2),
                                                  call_back=(self.call_back_zero_pos_width,
                                                             self.call_back_zero_pos_height),
                                                  call_update_all=self.call_set_zero_pos)

        self.manager.settings_window.add_settings(self, SettingsWindow.Title,
                                                  name="Сетка")

        self.manager.settings_window.add_settings(self, SettingsWindow.SettCheckboxLineEdit,
                                                  name="Размер сетки",
                                                  standard_values=(("вкл", True),
                                                                   self.manager.
                                                                   grid_manager.grid.get_step()),
                                                  int_only=True,
                                                  default_values_to_return=(
                                                      True, self.manager.
                                                      grid_manager.grid.get_step()),
                                                  call_back=(self.call_back_grid_show,
                                                             self.call_back_grid_size),
                                                  call_update_all=self.call_set_grid,
                                                  lock_line_edit=False)

        self.manager.settings_window.show_sett(self)

    def call_back_zero_pos_width(self, x: int):
        """
        callback for settings window. This is necessary to move zero point horizontally
        settings window -> core
        """

        self.manager.grid_manager.zero_point_dot.move_event(
            x + self.width() // 2,
            self.manager.grid_manager.zero_point_dot.get_pos()[1]
        )

        self.manager.grid_manager.grid.set_offset_by_zero_point()
        self.manager.grid_manager.grid.regenerate_grid()
        self.update()

    def call_back_zero_pos_height(self, y: int):
        """
        callback for settings window. This is necessary to move zero point vertically
        settings window -> core
        """
        self.manager.grid_manager.zero_point_dot.move_event(
            self.manager.grid_manager.zero_point_dot.get_pos()[0], y + self.height() // 2)
        self.manager.grid_manager.grid.set_offset_by_zero_point()
        self.manager.grid_manager.grid.regenerate_grid()
        self.update()

    def call_set_zero_pos(self) -> tuple:
        """
        gives right zero point position to settings window
        core -> settings window
        :return: position in tuple format (x, y)
        """
        x_left, y_up = self.manager.grid_manager.zero_point_dot.get_pos()
        x = x_left - self.width() // 2
        y = y_up - self.height() // 2
        return x, y

    def call_back_grid_show(self, show: bool):
        """
        callback for settings window. This is necessary to change grid showing
        settings window -> core
        """
        if show and not self.manager.grid_manager.grid.show:
            self.manager.grid_manager.grid.toggle_show()
        elif not show and self.manager.grid_manager.grid.show:
            self.manager.grid_manager.grid.toggle_show()
        self.update()

    def call_back_grid_size(self, step: int):
        """
        callback for settings window. This is necessary to change grid size
        settings window -> core
        """
        self.manager.grid_manager.grid.change_step(step)
        self.manager.grid_manager.grid.set_offset_by_zero_point()
        self.manager.grid_manager.grid.regenerate_grid()
        self.update()

    def call_set_grid(self) -> tuple:
        """
        gives grid's showing and step
        core -> settings window
        :return: tuple: (show, step)
        """
        return self.manager.grid_manager.grid.show, self.manager.grid_manager.grid.get_step()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.update()
        x, y = self.manager.grid_manager.zero_point_dot.get_pos()
        x -= self.manager.grid_manager.zero_point_dot.get_zero()[0]
        y -= self.manager.grid_manager.zero_point_dot.get_zero()[1]
        new_x, new_y = event.size().width() // 2, event.size().height() // 2

        [widget.move_event(
            widget.x() + new_x - self.manager.grid_manager.zero_point_dot.get_zero()[0],
            widget.y() + new_y - self.manager.grid_manager.zero_point_dot.get_zero()[1],
            show_pos=False)
         for widget in self.manager.widget_manager.get_all_widgets()]

        self.manager.grid_manager.set_new_zero_point_pos(new_x, new_y)
        self.manager.grid_manager.zero_point_dot.move_event(new_x + x, new_y + y)
        self.manager.grid_manager.grid.set_offset_by_zero_point()
        self.manager.grid_manager.grid.generate_grid()
        self.manager.grid_manager.grid.change_core_size(event.size().width(), event.size().height())
        self.manager.settings_window.set_geometry()
        self.manager.settings_window.update_obj_settings(self)
        self.update()

    def self_menu_show(self):
        """
        main context menu
        """
        pos = self.manager.mouse_manager.get_mouse_pos()
        context_menu = QtWidgets.QMenu()

        context_menu.addAction('Добавить объект',
                               lambda: self.manager.widget_manager.add_widget(pos),
                               shortcut="Ctrl+N")

        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid {CONTEXT_MENU_BORDER_COLOR};"
        )

        context_menu.setWindowFlags(context_menu.windowFlags() | Qt.NoDropShadowWindowHint)
        context_menu.exec_(QtGui.QCursor.pos())

    def arrow_menu_show(self, arrow):
        """
        arrow's context menu
        :param arrow: arrow_class.Arrow class
        """
        context_menu = QtWidgets.QMenu()

        context_menu.addAction("Изменить цвет",
                               lambda: self.manager.arrow_manager.change_arrow_color(arrow))

        context_menu.addAction('Удалить стрелку',
                               lambda: self.manager.arrow_manager.delete_arrow(arrow),
                               shortcut=QtCore.Qt.Key_D)

        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )

        context_menu.exec_(QtGui.QCursor.pos())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() == QtCore.Qt.LeftButton and self.hasFocus():
            x, y = self.manager.mouse_manager.get_mouse_pos()

            [widget.move_event(
                widget.x() + (event.pos().x() - x), widget.y() +
                (event.pos().y() - y),
                show_pos=False)
                for widget in self.manager.widget_manager.get_all_widgets()]

            self.manager.grid_manager.zero_point_dot.move_event(
                self.manager.grid_manager.zero_point_dot.x() +
                (event.pos().x() - x),
                self.manager.grid_manager.zero_point_dot.y() + (event.pos().y() - y)
            )

            if self.manager.grid_manager.grid.show:
                self.manager.grid_manager.grid.set_offset_by_zero_point()
                self.manager.grid_manager.grid.regenerate_grid()

            self.manager.settings_window.update_obj_settings(self)
            self.update()
        self.manager.mouse_manager.change_mouse_pos(event.x(), event.y())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        modifier = QtWidgets.QApplication.keyboardModifiers()
        if modifier == Qt.ControlModifier:
            if event.key() in (Qt.Key_N, 1058):

                w = self.manager.widget_manager.add_widget(
                    self.manager.mouse_manager.get_mouse_pos())

                self.update()
                self.manager.widget_manager.clear_focus()
                w.setFocus()
                w.show_angles()
                self.update()
            widget_has_focus = self.manager.widget_manager.widget_has_focus_or_none()
            if widget_has_focus:
                widget_has_focus.keyReleaseEvent(event)
                self.update()
        if not self.hasFocus():
            return
        if event.key() in (QtCore.Qt.Key_R, 1050):
            [widget.return_to_fact_pos() for widget in self.manager.widget_manager.get_all_widgets()]
            self.manager.grid_manager.zero_point_dot.return_to_zero()
            self.manager.grid_manager.grid.set_offset_by_zero_point()
            self.manager.grid_manager.grid.regenerate_grid()

        if event.key() in (QtCore.Qt.Key_G, 1055):
            self.manager.grid_manager.grid.toggle_show()
        if event.key() == QtCore.Qt.Key_Plus:
            self.manager.grid_manager.grid.change_step(self.manager.grid_manager.grid.get_step() * 2)
            self.manager.grid_manager.grid.set_offset_by_zero_point()
            self.manager.grid_manager.grid.regenerate_grid()
            self.manager.settings_window.update_obj_settings(self)

        elif event.key() == QtCore.Qt.Key_Minus:

            self.manager.grid_manager.grid.change_step(
                self.manager.grid_manager.grid.get_step() // 2)

            self.manager.grid_manager.grid.set_offset_by_zero_point()
            self.manager.grid_manager.grid.regenerate_grid()
            self.manager.settings_window.update_obj_settings(self)
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        [a.clear_focus() for a in self.manager.arrow_manager.get_all_arrows()]
        if event.button() == QtCore.Qt.RightButton:
            if self.manager.arrow_manager.get_active_arrow():

                self.manager.arrow_manager.delete_arrow(
                    self.manager.arrow_manager.get_active_arrow())

                self.manager.arrow_manager.toggle_active_arrow()
                return
            for arrow in self.manager.arrow_manager.get_all_arrows():
                if arrow.start_pos and arrow.end_pos:
                    x1, y1 = arrow.start_pos
                    x2, y2 = arrow.end_pos
                    x3, y3 = event.pos().x(), event.pos().y()
                    if -3 < check_on_arrow(x1, y1, x2, y2, x3, y3) < 3:
                        self.arrow_menu_show(arrow)
                        self.update()
                        return
            if self.hasFocus():
                self.self_menu_show()
        elif event.button() == QtCore.Qt.LeftButton:
            for arrow in self.manager.arrow_manager.get_all_arrows():
                if arrow.start_pos and arrow.end_pos:
                    x1, y1 = arrow.start_pos
                    x2, y2 = arrow.end_pos
                    x3, y3 = event.pos().x(), event.pos().y()
                    if -3 < check_on_arrow(x1, y1, x2, y2, x3, y3) < 3:
                        arrow.set_focus()
                        self.update()
                        return
            self.manager.settings_window.hide_all_sett()
            self.manager.settings_window.show_sett(self)

            self.manager.arrow_manager.clear_focus_arrows()
        self.manager.widget_manager.clear_focus()
        self.setFocus()
        self.update()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        x, y = event.pos().x() - event.source().pos().x(), event.pos().y() - event.source().pos().y()

        if not self.manager.widget_manager.dragged_obj and \
                event.source().size().width() - event.source().OFFSET - 5 \
                <= x <= \
                event.source().size().width() + 5 and \
                event.source().size().height() - event.source().OFFSET - 5 \
                <= y <= \
                event.source().size().height() + 5:

            self.manager.widget_manager.set_dor(RESIZE)
            event.source().show_size_or_pos_label()
            event.source().show_angles()
            self.manager.settings_window.hide_all_sett()
            self.manager.settings_window.show_sett(event.source())
        else:
            if self.manager.widget_manager.dragged_obj is None:
                self.manager.widget_manager.dragged_obj = event.source()
                self.manager.widget_manager.set_dor(DRAG)
                event.source().show_size_or_pos_label()
                event.source().show_angles()

                self.manager.widget_manager.drag_dot = (event.pos().x() - event.source().x(),
                                                        event.pos().y() - event.source().y())

                self.manager.settings_window.hide_all_sett()
                self.manager.settings_window.show_sett(event.source())
        event.accept()
        self.update()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        obj: TextWidget = event.source()
        modifier_pressed = QtWidgets.QApplication.keyboardModifiers()
        shift_pressed = (int(modifier_pressed) & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier
        if self.manager.widget_manager.get_dor() == DRAG:

            obj.move(
                event.pos().x() - self.manager.widget_manager.drag_dot[0],
                event.pos().y() - self.manager.widget_manager.drag_dot[1]
            )

            x, y, _, _, x_mod, y_mod, widgets = self.manager.widget_manager.drag_magnet_checker(obj)
            if shift_pressed:
                if not x_mod:

                    x = x - (x - self.manager.grid_manager.zero_point_dot.get_pos()[0]) \
                        % (OFFSET_MAGNET * 2)

                if not y_mod:

                    y = y - (y - self.manager.grid_manager.zero_point_dot.get_pos()[1]) \
                        % (OFFSET_MAGNET * 2)

            x, y = max(x, 0), max(y, 0)
            if self.manager.grid_manager.grid.show:

                x, y, widgets = \
                    self.manager.grid_manager.check_and_set_grid_magnet_lines_for_resizing(
                         obj, x, y, x_mod, y_mod, widgets
                    )

            self.manager.widget_manager.set_coords_on_widgets(widgets, event, x, y)
            obj.move_event(x, y)
            obj.update_arrows()
        elif self.manager.widget_manager.get_dor() == RESIZE:

            obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets = \
                self.manager.widget_manager.resize_magnet_checker(obj, event.pos())

            x, y = obj_x2 - obj_x1, obj_y2 - obj_y1
            if shift_pressed:
                if not x_mod:
                    x = max(x - x % (OFFSET_MAGNET * 2), 0)
                if not y_mod:
                    y = max(y - y % (OFFSET_MAGNET * 2), 0)
            self.manager.widget_manager.set_coords_on_widgets(widgets, event, x, y)
            obj.resize_event(x, y)

        self.update()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.manager.widget_manager.dragged_obj = None
        self.manager.grid_manager.drop_magnet_lines()
        self.manager.grid_manager.grid.clear_special_lines()
        event.accept()
        self.manager.widget_manager.set_dor(NONE)
        [widget.hide_size_or_pos_label() for widget in self.manager.widget_manager.get_all_widgets()]
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        self.qp.begin(self)
        self.qp.setRenderHint(QPainter.Antialiasing)
        self.manager.grid_manager.grid.draw(self.qp)
        for arrow in self.manager.arrow_manager.get_all_arrows():
            self.qp.setPen(QPen(QColor(arrow.get_color()), 2))
            end = self.manager.mouse_manager.get_mouse_pos()
            if arrow.draw(self.qp, end_pos=end):
                self.update()
        pen = QPen(QColor(MAGNET_LINE_COLOR), 1)
        pen.setStyle(QtCore.Qt.DashLine)
        self.qp.setPen(pen)
        mls = self.manager.grid_manager.get_magnet_lines()
        if mls:
            self.qp.drawLines(*mls)
        self.qp.end()
