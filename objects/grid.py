from PyQt5 import QtCore, QtGui

from objects.zero_point import ZeroPointWidget

from constants import GRID_COLOR, SPECIAL_LINE_COLOR, GRID_STEP


class Grid:
    """
    object for creating grid by QPainter
    """
    def __init__(self, color: str = GRID_COLOR,
                 line: QtCore.Qt.PenStyle = QtCore.Qt.DashLine,
                 show: bool = False,
                 core_size: tuple = None,
                 step: int = GRID_STEP,
                 offset: tuple or list = (20, 20),
                 zero_pos: ZeroPointWidget = None,
                 special_lines_color=SPECIAL_LINE_COLOR):
        """
        :param color: color of grid in hex format: #......
        :param line: code of line's type: QtCore.Qt.CodeLine
        :param show: show grid or hide
        :param core_size: size of main window: (width, height)
        :param step: height and width of one square
        :param offset: offset from left and top for grid
        :param zero_pos: zero point for auto creating grid by this
        :param special_lines_color: color of special lines:
               lines, that cross center and magnet lines for widgets
        """
        self.color = color
        self.special_lines_color = special_lines_color
        self.line = line
        self.zero_pos = zero_pos
        self.pen = QtGui.QPen(QtGui.QColor(self.color), 1)
        self.pen.setStyle(self.line)
        self.show = show
        self.core_size = core_size
        self.step = step
        self.offset_left, self.offset_top = offset
        self.special_lines_for_drag_obj = []
        self.grid = self.generate_grid()

    def generate_grid(self) -> dict:
        """
        creates grid lines and returns them
        :return: dict with "x" and "y" keys,
                 which contain lists with QLine elements
                 or empty dict if core size is None
        """
        if not self.core_size:
            return {}
        lines_x = []
        lines_y = []
        for x in range(self.offset_left, self.core_size[0] + 1, self.step):
            lines_y.append(QtCore.QLine(x, 0, x, self.core_size[1]))
        for y in range(self.offset_top, self.core_size[1] + 1, self.step):
            lines_x.append(QtCore.QLine(0, y, self.core_size[0], y))
        return {"x": lines_x, "y": lines_y}

    def draw(self, qp: QtGui.QPainter):
        """
        draws grid and special lines
        :param qp: QPainter from main object
        """
        if not self.show or not self.grid:
            return
        qp.setPen(self.pen)
        special_lines = self.get_special_lines()
        if self.grid.get("x", []):
            qp.drawLines(*self.grid["x"])
        if self.grid.get("y", []):
            qp.drawLines(*self.grid["y"])
        pen = QtGui.QPen(QtGui.QColor(self.special_lines_color), self.pen.width())
        pen.setStyle(self.line)
        qp.setPen(pen)
        if special_lines.get("x", []):
            qp.drawLines(*special_lines["x"])
        if special_lines.get("y", []):
            qp.drawLines(*special_lines["y"])
        if self.special_lines_for_drag_obj:
            qp.drawLines(*self.special_lines_for_drag_obj)

    def change_core_size(self, width: int, height: int):
        """
        gets new core size
        """
        self.core_size = width, height
        self.grid = self.generate_grid()

    def regenerate_grid(self):
        """
        regenerates grid
        """
        self.grid = self.generate_grid()

    def toggle_show(self) -> bool:
        """
        toggles grid's show (True -> False and False -> True)
        :return: show or not after toggle
        """
        self.show = not self.show
        if self.show:
            self.set_offset_by_zero_point()
            self.regenerate_grid()
        return self.show

    def change_offset(self, offset_left: int = 20, offset_top: int = 20):
        """
        changes offset from left and top
        """
        self.offset_left, self.offset_top = offset_left, offset_top

    def get_offset(self) -> tuple:
        """
        :return: offset from left and top
        """
        return self.offset_left, self.offset_top

    def get_step(self) -> int:
        """
        :return: width and height of grid's cell
        """
        return self.step

    def change_step(self, step: int):
        """
        changes step width and height of grid's cell
        """
        if step > 0:
            self.step = step

    def get_special_lines(self) -> dict:
        """
        creates special lines and returns them
        :return: dict with "x" and "y" keys,
                 which contain lists with QLine elements
        """
        zero = self.zero_pos.get_pos()

        x_lines = list(filter(
            lambda line: True if line.y1() == line.y2() == zero[
                1] else False, self.grid.get("x", [])))
        y_lines = list(filter(
            lambda line: True if line.x1() == line.x2() == zero[
                0] else False, self.grid.get("y", [])))
        return {"x": x_lines, "y": y_lines}

    def set_offset_by_zero_point(self):
        """
        sets offset by zero point and step
        """
        self.offset_left = self.zero_pos.get_pos()[0] % self.step
        self.offset_top = self.zero_pos.get_pos()[1] % self.step

    def get_nearest_x_line_by_offset(self, y: int, offset: int = 5) -> QtCore.QLine:
        """
        gets nearest horizontal line by y coordinate
        :param y: y coordinate
        :param offset: max distance between y coordinate and grid's line
        :return: nearest line or None
        """
        x_line = list(filter(lambda line: True if line.y1() - offset < y < line.y1() + offset
                             else False, self.grid.get("x", [])))
        return x_line[0] if x_line else None

    def get_nearest_y_line_by_offset(self, x: int, offset=5) -> QtCore.QLine:
        """
        gets nearest vertical line by x coordinate
        :param x: x coordinate
        :param offset: max distance between y coordinate and grid's line
        :return: nearest line or None
        """
        y_line = list(filter(lambda line: True if line.x1() - offset < x < line.x1() + offset
                             else False, self.grid.get("y", [])))
        return y_line[0] if y_line else None

    def add_line_to_special_lines(self, line: QtCore.QLine):
        """
        adds line in list of special lines. if line isn't QLine class does nothing
        :param line: your line in QLine format
        """
        if isinstance(line, QtCore.QLine):
            self.special_lines_for_drag_obj.append(line)

    def clear_special_lines(self):
        """
        clears list of special lines
        """
        self.special_lines_for_drag_obj.clear()
