from PyQt5 import QtCore, QtGui

from zero_dot import ZeroPointDotWidget


class Grid:
    def __init__(self, color="#C8C8C8", line=QtCore.Qt.DashLine, show=False, core_size=None,
                 step=20, offset=(20, 20), zero_pos: ZeroPointDotWidget = None,
                 special_lines_color="#969696"):
        self.color = color
        self.special_lines_color = special_lines_color
        self.line = line
        self.zero_pos = zero_pos
        self.pen = QtGui.QPen(QtGui.QColor(self.color), 1)
        self.pen.setStyle(self.line)
        self.show = show
        self.core_size = core_size
        self.step = step
        self.offset_x, self.offset_y = offset
        self.special_lines_for_drag_obj = []
        self.grid = self.generate_grid()

    def generate_grid(self):
        if not self.core_size:
            return []
        lines_x = []
        lines_y = []
        for x in range(self.offset_x, self.core_size[0] + 1, self.step):
            lines_y.append(QtCore.QLine(x, 0, x, self.core_size[1]))
        for y in range(self.offset_y, self.core_size[1] + 1, self.step):
            lines_x.append(QtCore.QLine(0, y, self.core_size[0], y))
        return {"x": lines_x, "y": lines_y}

    def draw(self, qp: QtGui.QPainter):
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

    def change_grid_size(self, x, y):
        self.core_size = x, y
        self.grid = self.generate_grid()

    def regenerate_grid(self):
        self.grid = self.generate_grid()

    def toggle_show(self):
        self.show = not self.show
        if self.show:
            self.set_offset_by_zero_point()
            self.regenerate_grid()

    def change_offset(self, offset_x=20, offset_y=20):
        self.offset_x, self.offset_y = offset_x, offset_y

    def get_offset(self):
        return self.offset_x, self.offset_y

    def get_step(self):
        return self.step

    def change_step(self, step):
        if step > 0:
            self.step = step

    def get_special_lines(self):
        zero = self.zero_pos.get_pos()

        x_lines = list(filter(
            lambda line: True if line.y1() == line.y2() == zero[
                1] else False, self.grid.get("x", [])))
        y_lines = list(filter(
            lambda line: True if line.x1() == line.x2() == zero[
                0] else False, self.grid.get("y", [])))
        return {"x": x_lines, "y": y_lines}

    def set_offset_by_zero_point(self):
        self.offset_x = self.zero_pos.get_pos()[0] % self.step
        self.offset_y = self.zero_pos.get_pos()[1] % self.step

    def get_nearest_lines_by_offset(self, x, y, offset=5):
        x_line = list(filter(lambda line: True if line.y1() - offset < y < line.y1() + offset
                             else False, self.grid.get("x", [])))
        y_line = list(filter(lambda line: True if line.x1() - offset < x < line.x1() + offset
                             else False, self.grid.get("y", [])))
        x_line = x_line[0] if x_line else None
        y_line = y_line[0] if y_line else None
        return x_line, y_line

    def get_nearest_y_line_by_offset(self, y, offset=5):
        x_line = list(filter(lambda line: True if line.y1() - offset < y < line.y1() + offset
                             else False, self.grid.get("x", [])))
        return x_line[0] if x_line else None

    def get_nearest_x_line_by_offset(self, x, offset=5):
        y_line = list(filter(lambda line: True if line.x1() - offset < x < line.x1() + offset
                             else False, self.grid.get("y", [])))
        return y_line[0] if y_line else None

    def add_line_to_special_lines(self, line):
        self.special_lines_for_drag_obj.append(line)

    def clear_special_lines(self):
        self.special_lines_for_drag_obj = []
