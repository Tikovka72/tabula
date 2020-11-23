import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor, QPen

from manager import Manager
from utils import check_on_arrow
from constants import NONE, DRAG, RESIZE, MAGNET_LINES_COLOR


class Core(QtWidgets.QWidget):
    STANDARD_SIZE = 640, 480

    def __init__(self):
        super().__init__()
        self.manager = Manager(self)
        self.arrow_menu = False
        self.mouse_nearest_lines = []
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.__init_ui__()

    def __init_ui__(self):
        self.setWindowTitle("tabula")
        self.setMinimumSize(640, 480)
        self.resize(*self.STANDARD_SIZE)
        self.showMaximized()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setObjectName("core")
        self.setStyleSheet("QWidget#core {background-color: white}")
        self.setFocus()

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self.update()
        x, y = self.manager.zero_point_dot.get_pos()
        x -= self.manager.zero_point_dot.get_zero()[0]
        y -= self.manager.zero_point_dot.get_zero()[1]
        new_x, new_y = a0.size().width() // 2, a0.size().height() // 2
        [widget.move_event(widget.x() + new_x - self.manager.zero_point_dot.get_zero()[0],
                           widget.y() + new_y - self.manager.zero_point_dot.get_zero()[1],
                           show_pos=False)
         for widget in self.manager.get_all_widgets()]
        self.manager.set_new_zero_point_pos(new_x, new_y)
        self.manager.zero_point_dot.move_event(new_x + x,
                                               new_y + y)
        self.manager.grid.set_offset_by_zero_point()
        self.manager.grid.regenerate_grid()
        self.manager.grid.change_grid_size(a0.size().width(), a0.size().height())
        self.manager.settings_window.set_geometry()

    def self_menu_show(self):
        pos = self.manager.get_mouse_pos()
        context_menu = QtWidgets.QMenu()
        context_menu.addAction('Добавить объект',
                               lambda: self.manager.add_widget(pos))
        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        context_menu.exec_(QtGui.QCursor.pos())

    def arrow_menu_show(self, arrow):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction("Изменить цвет", lambda: self.manager.change_arrow_color(arrow))
        context_menu.addAction('Удалить стрелку', lambda: self.manager.delete_arrow(arrow),
                               shortcut=QtCore.Qt.Key_D)
        context_menu.setStyleSheet(
            f"font-size: 15px;"
            f"border-radius: 5%;"
            f"border: 1px solid black;"
        )
        context_menu.exec_(QtGui.QCursor.pos())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() == QtCore.Qt.LeftButton and self.hasFocus():
            x, y = self.manager.get_mouse_pos()
            [widget.move_event(
                widget.x() + (event.pos().x() - x), widget.y() +
                (event.pos().y() - y),
                show_pos=False
            )
             for widget in self.manager.get_all_widgets()]
            grid_offset = self.manager.grid.get_offset()
            self.manager.grid.change_offset(
                (grid_offset[0] + (event.pos().x() - x)) % self.manager.grid.get_step(),
                (grid_offset[1] + (event.pos().y() - y)) % self.manager.grid.get_step())
            self.manager.grid.regenerate_grid()
            self.manager.zero_point_dot.move_event(self.manager.zero_point_dot.x() +
                                                   (event.pos().x() - x),
                                                   self.manager.zero_point_dot.y() +
                                                   (event.pos().y() - y))
        self.manager.change_mouse_pos(event.x(), event.y())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if not self.hasFocus():
            return
        if event.key() in (QtCore.Qt.Key_R, 1050):
            [widget.return_to_fact_pos() for widget in self.manager.get_all_widgets()]
            self.manager.zero_point_dot.return_to_zero()
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()
        if event.key() in (QtCore.Qt.Key_G, 1055):
            self.manager.grid.toggle_show()
        if event.key() == QtCore.Qt.Key_Plus:
            self.manager.grid.change_step(self.manager.grid.get_step() * 2)
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()
        elif event.key() == QtCore.Qt.Key_Minus:
            self.manager.grid.change_step(self.manager.grid.get_step() // 2)
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.RightButton:
            if self.manager.get_active_arrow():
                self.manager.delete_arrow(self.manager.get_active_arrow())
                self.manager.toggle_active_arrow()
                return
            for arrow in self.manager.get_all_arrows():
                if arrow.start_pos and arrow.end_pos:
                    x1, y1 = arrow.start_pos
                    x2, y2 = arrow.end_pos
                    x3, y3 = event.pos().x(), event.pos().y()
                    if -3 < check_on_arrow(x1, y1, x2, y2, x3, y3) < 3:
                        self.arrow_menu_show(arrow)
                        return

            if self.hasFocus():
                self.self_menu_show()
        elif event.button() == QtCore.Qt.LeftButton:
            for arrow in self.manager.get_all_arrows():
                if arrow.start_pos and arrow.end_pos:
                    x1, y1 = arrow.start_pos
                    x2, y2 = arrow.end_pos
                    x3, y3 = event.pos().x(), event.pos().y()
                    if -3 < check_on_arrow(x1, y1, x2, y2, x3, y3) < 3:
                        arrow.set_focus()
                        return
            self.manager.clear_focus_arrows()
        for widget in self.manager.get_all_widgets():
            widget.hide_angles()
        self.manager.clear_focus()
        self.setFocus()
        self.manager.settings_window.hide_all_sett()

    def dragEnterEvent(self, event):
        x, y = event.pos().x() - event.source().pos().x(), event.pos().y() - event.source().pos().y()
        if 0 <= x <= event.source().OFFSET + 5 and 0 <= y <= event.source().OFFSET + 5:
            self.manager.set_dor(DRAG)
            event.source().show_size_or_pos_label()
            event.source().show_angles()
            self.manager.settings_window.hide_all_sett()
            self.manager.settings_window.show_sett(event.source())
        elif event.source().size().width() - event.source().OFFSET - 5 \
                <= x <= \
                event.source().size().width() + 5 and \
                event.source().size().height() - event.source().OFFSET - 5 \
                <= y <= \
                event.source().size().height() + 5:
            self.manager.set_dor(RESIZE)
            event.source().show_size_or_pos_label()
            event.source().show_angles()
            self.manager.settings_window.hide_all_sett()
            self.manager.settings_window.show_sett(event.source())

        event.accept()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        obj = event.source()
        modifier_pressed = QtWidgets.QApplication.keyboardModifiers()
        shift_pressed = (int(modifier_pressed) & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier
        if self.manager.get_dor() == DRAG:
            event.source().move(event.pos().x() - obj.OFFSET // 2, event.pos().y() - obj.OFFSET // 2)
            x, y, _, _, x_mod, y_mod, widgets = self.manager.drag_magnet_checker(obj)

            if shift_pressed:
                if not x_mod:
                    x = x - (x - self.manager.zero_point_dot.get_pos()[0]) \
                        % (self.manager.OFFSET_MAGNET * 2)
                if not y_mod:
                    y = y - (y - self.manager.zero_point_dot.get_pos()[1]) \
                        % (self.manager.OFFSET_MAGNET * 2)
            x, y = max(x, 0), max(y, 0)
            if self.manager.grid.show:
                x, y, widgets = self.manager.check_and_set_grid_magnet_lines_for_resizing(
                    obj, x, y, x_mod, y_mod, widgets
                )
            self.manager.set_coords_on_widgets(widgets, event, x, y)
            event.source().move_event(x, y)
            event.source().update_arrows()
        elif self.manager.get_dor() == RESIZE:
            obj_x1, obj_y1, obj_x2, obj_y2, x_mod, y_mod, widgets = \
                self.manager.resize_magnet_checker(obj, event.pos())
            x, y = obj_x2 - obj_x1, obj_y2 - obj_y1
            if shift_pressed:
                if not x_mod:
                    x = max(x - x % (self.OFFSET_MAGNET * 2), 0)
                if not y_mod:
                    y = max(y - y % (self.OFFSET_MAGNET * 2), 0)
            self.manager.set_coords_on_widgets(widgets, event, x, y)
            event.source().resize_event(x, y)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.manager.drop_magnet_lines()
        self.manager.grid.clear_special_lines()
        event.accept()
        self.manager.set_dor(NONE)
        [widget.hide_size_or_pos_label() for widget in self.manager.get_all_widgets()]

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.manager.grid.draw(qp)
        for arrow in self.manager.get_all_arrows():
            qp.setPen(QPen(QColor(arrow.get_color()), 2))
            end = self.manager.get_mouse_pos()
            arrow.draw(qp, end_pos=end)
        pen = QPen(QColor(MAGNET_LINES_COLOR), 1)
        pen.setStyle(QtCore.Qt.DashLine)
        qp.setPen(pen)
        mls = self.manager.get_magnet_lines()
        if mls:
            qp.drawLines(*mls)
        qp.end()
        self.update()


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        tabula_app = Core()
        tabula_app.show()

        sys.exit(app.exec())
    except Exception as e:
        print(e)
