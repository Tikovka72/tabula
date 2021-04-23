from PyQt5 import QtWidgets

import sys

from core import Core

from managers.widget_manager import WidgetManager
from managers.arrow_manager import ArrowManager
from managers.file_manager import FileManager
from managers.grid_manager import GridManager

from mouse import Mouse
from settings_widget import SettingsWindow
from utils import except_hook


class Manager:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.core = Core(self)

        self.mouse = Mouse()

        self.widget_manager = WidgetManager(self)
        self.arrow_manager = ArrowManager(self)
        self.file_manager = FileManager(self)
        self.grid_manager = GridManager(self)

        self.active_arrow = None

        self.settings_window = SettingsWindow(self.core, self)
        self.core.__init_ui__()
        self.core.show()

    def get_mouse_pos(self) -> tuple:
        """
        :return: mouse position
        """
        return self.mouse.get_pos()

    def change_mouse_pos(self, x: int, y: int):
        """
        changes mouse (mouse.Mouse) position to (x, y)
        """
        self.mouse.change_pos(x, y)

    def update_core(self):
        self.core.update()


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = Manager()
    sys.exit(app.app.exec())
