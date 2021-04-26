from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Manager

from PyQt5 import QtWidgets

import aggdraw
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin

from objects.arrow import Arrow
from objects.text_widget import TextWidget
from objects.warning_window import WarningWindow

from constants import WIDGET_BORDER_COLOR

Image.LANCZOS = True
Image.BICUBIC = True


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
        for arrow in self.arrow_manager.get_all_arrows():
            pen = aggdraw.Pen(arrow.color, 2)
            draw.line((arrow.start_pos[0] -
                       self.manager.grid_manager.zero_point_dot.get_pos()[0] + abs(xs) + 20,
                       arrow.start_pos[1] -
                       self.manager.grid_manager.zero_point_dot.get_pos()[1] + abs(ys) + 20,
                       arrow.end_pos[0] -
                       self.manager.grid_manager.zero_point_dot.get_pos()[0] + abs(xs) + 20,
                       arrow.end_pos[1] -
                       self.manager.grid_manager.zero_point_dot.get_pos()[1] + abs(ys) + 20
                       ), pen)
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
