from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

if TYPE_CHECKING:
    from main import Manager

from objects.warning_window import WarningWindow
from objects.arrow_class import Arrow


class FileManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.widget_manager = manager.widget_manager
        self.arrow_manager = manager.arrow_manager
        self.opened_file = None

    def save_file(self):
        """
        handler for saving project in file
        """
        if not self.opened_file:
            self.opened_file = self.get_name_file()
            if not self.opened_file:
                return
        text_file = []
        widget_ids = {}
        for i, widget in enumerate(self.widget_manager.widgets):
            text_file.append(
                "U+FB4x13c".join(map(
                    str,
                    (i, widget.x(), widget.y(), widget.width(), widget.height(), widget.data()))
                )
            )
            widget_ids[widget] = i
        text_arrows = []
        for i, arrow in enumerate(self.arrow_manager.arrows):
            text_arrows.append(
                "U+FB4x16c".join(map(
                    str, (i, widget_ids[arrow.obj1], widget_ids[arrow.obj2], int(arrow.need_arrow)))
                )
            )
        with open(self.opened_file, "w", encoding="UTF-8") as f:
            f.write("U+FB4x18c".join(("U+FB4x15c".join(text_file), "U+FB4x17c".join(text_arrows))))

    def open_file(self):
        """
        handler for opening  *.tbl files
        """
        if self.opened_file:
            dialog = WarningWindow(text="Вы хотите закрыть текущий файл?")
            if dialog.exec_():
                self.opened_file = None
        file = QtWidgets.QFileDialog().getOpenFileName(
            self.manager.core, "open file", filter="*.tbl")
        if not file[0]:
            return
        widgets = tuple(self.widget_manager.widgets.keys())
        tuple(map(lambda wi: wi.del_self(), widgets))
        with open(file[0], encoding="UTF-8") as f:
            self.opened_file = file[0]
            data = f.read()
        self.manager.grid_manager.zero_point_dot.return_to_zero(anim=False)
        self.manager.grid_manager.grid.set_offset_by_zero_point()
        self.manager.grid_manager.grid.regenerate_grid()
        widgets_and_arrows = data.split("U+FB4x18c")
        if len(widgets_and_arrows) == 2:
            widgets, arrows = data.split("U+FB4x18c")
        else:
            return
        widgets = widgets.split("U+FB4x15c")
        arrows = arrows.split("U+FB4x17c")
        widgets_total = {}
        if widgets[0]:
            for widget in widgets:
                wid, x, y, w, h, d = widget.split("U+FB4x13c")
                widget_class = self.widget_manager.add_widget((int(x), int(y)))
                widget_class.resize(int(w), int(h))
                widget_class.set_data(d)
                widgets_total[int(wid)] = widget_class
        if arrows[0]:
            for arrow in arrows:
                aid, obj1, obj2, na = arrow.split("U+FB4x16c")
                arr = Arrow(self.arrow_manager, need_arrow=bool(int(na)))
                self.arrow_manager.add_arrow(arr)
                self.arrow_manager.set_obj1_arrow(arr, widgets_total[int(obj1)])
                self.arrow_manager.set_obj2_arrow(arr, widgets_total[int(obj2)])
                arr.set_start_and_end()
                self.manager.widget_manager.clear_focus()
                self.manager.arrow_manager.clear_focus_arrows()

    def get_name_file(self) -> str or None:
        """
        handler for calling dialog, which asks for name for new file
        :return: name of new file or None if user closes dialog
        """
        name = QtWidgets.QFileDialog.getSaveFileName(self.manager.core, 'Save File', filter="*.tbl",
                                                     directory="new scheme.tbl")
        if name[0]:
            return name[0]
        return None
