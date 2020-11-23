import math

from PyQt5.QtCore import QLine
from PyQt5.QtGui import QPainter
from numpy import arctan2

from constants import FROM_AND_TO_CENTER, FROM_AND_TO_NEAREST_LINE


class Arrow:
    def __init__(self, start_pos=None, end_pos=None, color="#000000", need_arrow=False,
                 arrow_type=FROM_AND_TO_NEAREST_LINE):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.obj1 = None
        self.obj2 = None
        self.need_arrow = need_arrow
        self.arrow_type = arrow_type

    def get_data_about_object1(self):
        if not self.obj1:
            return 0, 0, 0, 0, 0, 0, 0, 0
        width1 = self.obj1.size().width()
        height1 = self.obj1.size().height()
        x1, y1 = self.obj1.pos().x(), self.obj1.pos().y()
        up_dot1 = x1 + width1 // 2, y1
        bottom_dot1 = x1 + width1 // 2, y1 + height1
        left_dot1 = x1, y1 + height1 // 2
        right_dot1 = x1 + width1, y1 + height1 // 2
        return width1, height1, x1, y1, up_dot1, bottom_dot1, left_dot1, right_dot1, \


    def get_data_about_object2(self):
        if not self.obj2:
            return 0, 0, 0, 0, 0, 0, 0, 0
        width2 = self.obj2.size().width()
        height2 = self.obj2.size().height()
        x2, y2 = self.obj2.pos().x(), self.obj2.pos().y()
        up_dot2 = x2 + width2 // 2, y2
        bottom_dot2 = x2 + width2 // 2, y2 + height2
        left_dot2 = x2, y2 + height2 // 2
        right_dot2 = x2 + width2, y2 + height2 // 2
        return width2, height2, x2, y2, up_dot2, bottom_dot2, left_dot2, right_dot2

    def set_start_and_end_ntn(self):
        width1, height1, x1, y1, up_dot1, bottom_dot1, left_dot1, right_dot1 = \
            self.get_data_about_object1()
        width2, height2, x2, y2, up_dot2, bottom_dot2, left_dot2, right_dot2 = \
            self.get_data_about_object2()

        possible_lines = {
            up_dot1: (bottom_dot2, left_dot2, right_dot2),
            bottom_dot1: (up_dot2, left_dot2, right_dot2),
            left_dot1: (up_dot2, bottom_dot2, right_dot2),
            right_dot1: (up_dot2, bottom_dot2, left_dot2),
        }
        min_ = float("inf")
        dots_min = (0, 0), (0, 0)
        for obj1_el, obj2_els in possible_lines.items():
            for obj2_el in obj2_els:
                distance = ((obj2_el[0] - obj1_el[0]) ** 2 + (obj2_el[1] - obj1_el[1]) ** 2) ** 0.5
                if distance < min_:
                    min_ = distance
                    dots_min = obj1_el, obj2_el
        self.start_pos, self.end_pos = dots_min
        return dots_min

    def set_start_and_end_ctc(self):
        center1 = self.obj1.x() + self.obj1.width() // 2, self.obj1.y() + self.obj1.height() // 2
        center2 = self.obj2.x() + self.obj2.width() // 2, self.obj2.y() + self.obj2.height() // 2
        self.start_pos, self.end_pos = center1, center2
        return center1, center2

    def set_start_and_end_pos_by_obj(self):
        if not (self.obj1 and self.obj2):
            return
        return ARROW_TYPES[self.arrow_type]["set_sae"](self)

    def get_start_and_end_ntn(self, end_pos: tuple):
        width1, height1, x1, y1, up_dot1, bottom_dot1, left_dot1, right_dot1 = \
            self.get_data_about_object1()
        min_ = float("inf")
        dots_min = (0, 0), (0, 0)
        for start_pos in [up_dot1, bottom_dot1, left_dot1, right_dot1]:
            distance = ((end_pos[0] - start_pos[0]) ** 2 +
                        (end_pos[1] - start_pos[1]) ** 2) ** 0.5
            if distance < min_:
                min_ = distance
                dots_min = start_pos, end_pos
        return dots_min

    def get_start_and_end_ctc(self, end_pos: tuple):
        center1 = self.obj1.x() + self.obj1.width() // 2, \
                  self.obj1.y() + self.obj1.height() // 2
        return center1, end_pos

    def get_start_pos_and_end_pos_by_end_pos(self, end_pos: tuple):
        if self.obj1:
            return ARROW_TYPES[self.arrow_type]["get_saebep"](self, end_pos)
        return (0, 0), (0, 0)

    def create_arrow(self, end_pos=None):
        if self.start_pos:
            start = self.start_pos
            end = self.end_pos or end_pos
        else:
            start, end = self.get_start_pos_and_end_pos_by_end_pos(end_pos or self.end_pos)
        ul = arctan2(-(start[0] - end[0]), -(start[1] - end[1]))
        s1 = int(end[0] + 20 * math.sin(ul - 40)), int(end[1] + 20 * math.cos(ul - 40))
        s2 = int(end[0] + 20 * math.sin(ul + 40)), int(end[1] + 20 * math.cos(ul + 40))
        return QLine(*s1, *end), QLine(*s2, *end)

    def draw(self, qp: QPainter, end_pos=None):
        if self.end_pos:
            qp.drawLine(QLine(*self.start_pos, *self.end_pos))
            if self.need_arrow:
                ar1, ar2 = self.create_arrow(end_pos=self.end_pos)
                qp.drawLines(ar1, ar2)
        elif end_pos:
            start, end = self.get_start_pos_and_end_pos_by_end_pos(end_pos)
            qp.drawLine(QLine(*start, *end))
            if self.need_arrow:
                ar1, ar2 = self.create_arrow(end_pos=end_pos)
                qp.drawLines(ar1, ar2)


ARROW_TYPES = {
    FROM_AND_TO_CENTER: {"set_sae": Arrow.set_start_and_end_ctc,
                         "get_saebep": Arrow.get_start_and_end_ctc},
    FROM_AND_TO_NEAREST_LINE: {"set_sae": Arrow.set_start_and_end_ntn,
                               "get_saebep": Arrow.get_start_and_end_ntn},
}
