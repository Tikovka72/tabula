from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager

from PyQt5 import QtWidgets
from PyQt5.QtCore import QLine

import aggdraw
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin

from objects.arrow import Arrow
from objects.text_widget import TextWidget
from objects.warning_window import WarningWindow

from constants import WIDGET_BORDER_COLOR


class ImageManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.widget_manager = manager.widget_manager
        self.arrow_manager = manager.arrow_manager

    def create_image(self):
        file_to_save = self.get_name_file()
        if not file_to_save:
            return
        with open(file_to_save, "w") as f:
            f.close()
        xs, ys = float("inf"), float("inf")
        xl, yl = -float("inf"), -float("inf")
        for widget in self.widget_manager.get_all_widgets():
            widget: TextWidget = widget
            x_left, y_top, x_right, y_bottom = (
                widget.x() - self.manager.grid_manager.zero_point_dot.get_pos()[0],
                widget.y() - self.manager.grid_manager.zero_point_dot.get_pos()[1],
                widget.x() + widget.width() - self.manager.grid_manager.zero_point_dot.get_pos()[0],
                widget.y() + widget.height() - self.manager.grid_manager.zero_point_dot.get_pos()[1]
            )
            xs = x_left if x_left < xs else xs
            xl = x_right if x_right > xl else xl
            ys = y_top if y_top < ys else ys
            yl = y_bottom if y_bottom > yl else yl
        xl += abs(xs) + 40
        yl += abs(ys) + 40
        im = Image.new("RGB", (xl, yl))
        draw = aggdraw.Draw(im)
        draw.rectangle((0, 0, xl, yl), aggdraw.Pen("#ffffff"), aggdraw.Brush("#ffffff"))
        zero_pos_coefficient_x = self.manager.grid_manager.zero_point_dot.get_pos()[0] - abs(xs) - 20
        zero_pos_coefficient_y = self.manager.grid_manager.zero_point_dot.get_pos()[1] - abs(ys) - 20
        for arrow in self.arrow_manager.get_all_arrows():
            pen = aggdraw.Pen(arrow.color, 2)
            draw.line((arrow.start_pos[0] - zero_pos_coefficient_x,
                       arrow.start_pos[1] - zero_pos_coefficient_y,
                       arrow.end_pos[0] - zero_pos_coefficient_x,
                       arrow.end_pos[1] - zero_pos_coefficient_y
                       ), pen)
            if arrow.need_arrow:
                arrow_line_1, arrow_line_2 = arrow.create_arrow()
                arrow_line_1: QLine = arrow_line_1
                arrow_line_2: QLine = arrow_line_2
                draw.line((
                    arrow_line_1.p1().x() - zero_pos_coefficient_x,
                    arrow_line_1.p1().y() - zero_pos_coefficient_y,
                    arrow_line_1.p2().x() - zero_pos_coefficient_x,
                    arrow_line_1.p2().y() - zero_pos_coefficient_y,
                ), pen)
                draw.line((
                    arrow_line_2.p1().x() - zero_pos_coefficient_x,
                    arrow_line_2.p1().y() - zero_pos_coefficient_y,
                    arrow_line_2.p2().x() - zero_pos_coefficient_x,
                    arrow_line_2.p2().y() - zero_pos_coefficient_y,
                ), pen)
        for widget in self.widget_manager.get_all_widgets():
            pen = aggdraw.Pen(WIDGET_BORDER_COLOR, int(widget.call_set_border()[0]))
            rad = widget.edit_line.border_radius
            data_for_arcs = (
                ((0, 0, rad * 2, rad * 2), (90, 180)),
                ((0, widget.edit_line.height() - rad * 2, rad * 2, widget.edit_line.height()),
                 (180, 270)),
                ((-rad * 2 + widget.edit_line.width(), widget.edit_line.height() - rad * 2,
                  widget.edit_line.width(), widget.edit_line.height()), (270, 0)),
                ((-rad * 2 + widget.edit_line.width(), 0, widget.edit_line.width(), rad * 2),
                 (0, 90))
            )
            for (x1, y1, x2, y2), (start, end) in data_for_arcs:
                draw.arc((
                    widget.x() + widget.OFFSET - zero_pos_coefficient_x + x1,
                    widget.y() + widget.OFFSET - zero_pos_coefficient_y + y1,
                    widget.x() + widget.OFFSET - zero_pos_coefficient_x + x2,
                    widget.y() + widget.OFFSET - zero_pos_coefficient_y + y2,
                ), start, end, pen)
        draw.flush()
        im.save(file_to_save)

    def get_name_file(self) -> str or None:
        """
        handler for calling dialog, which asks for name for new file
        :return: name of new file or None if user closes dialog
        """
        name = QtWidgets.QFileDialog.getSaveFileName(self.manager.core, 'Имя для изображения',
                                                     filter="*.png",
                                                     directory="new pic.png")
        if name[0]:
            return name[0]
        return None
