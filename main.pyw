from PyQt5 import QtWidgets
from PyQt5.QtGui import QFontDatabase

import sys

from main_window import GraphicCore

from managers.arrow_manager import ArrowManager
from managers.file_manager import FileManager
from managers.grid_manager import GridManager
from managers.image_manager import ImageManager
from managers.mouse_manager import MouseManager
from managers.widget_manager import WidgetManager

from objects.settings_widget import SettingsWindow

from utils import except_hook, get_fonts


class Manager:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.core = GraphicCore(self)
        self.font_db = get_fonts(QFontDatabase())
        self.mouse_manager = MouseManager(self)
        self.widget_manager = WidgetManager(self)
        self.arrow_manager = ArrowManager(self)
        self.file_manager = FileManager(self)
        self.grid_manager = GridManager(self)
        self.image_manager = ImageManager(self)

        self.settings_window = SettingsWindow(self.core, self)
        self.core.__init_ui__()
        self.core.show()

    def update_core(self):
        self.core.update()


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = Manager()
    sys.exit(app.app.exec())
