from PyQt5 import QtWidgets, QtGui, QtCore


class ZeroPointDotWidget(QtWidgets.QWidget):
    """
    point in centre of screen. This needs for moving canvas and knowing where real center.
    (point moves with canvas)
    """
    def __init__(self, parent, manager=None):
        """
        :param parent: widget on which point is located
        :param manager: main class containing all information
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.zero = self.parent.STANDARD_SIZE[0] // 2, self.parent.STANDARD_SIZE[1] // 2
        self.manager = manager
        self.pos()
        self.anim = ZeroDotAndGridAnimation(self, b"geometry", self.manager)
        self.anim.setDuration(300)
        self.__init_ui__()

    def __init_ui__(self):
        self.setStyleSheet("background-color: black")

    def move_event(self, x, y):
        """
        add-on for move for moving animation
        """
        self.move(x, y)

    def get_pos(self):
        """
        gives real center position
        :return:
        """
        return self.x(), self.y()

    def return_to_zero(self, anim=True):
        if anim:
            self.move_animation(self.zero)
        else:
            self.move(*self.zero)

    def set_zero(self, x, y):
        self.zero = x, y

    def get_zero(self):
        return self.zero

    def move_animation(self, end_pos):
        self.anim.setStartValue(QtCore.QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QtCore.QRect(*end_pos, self.width(), self.height()))

        self.anim.start()


class ZeroDotAndGridAnimation(QtCore.QPropertyAnimation):
    def __init__(self, parent, anim_type, manager):
        super().__init__(parent, anim_type)
        self.manager = manager

    def updateCurrentValue(self, value) -> None:
        self.targetObject().setGeometry(value)
        if self.manager.grid.show:
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()
            self.manager.settings_window.update_obj_settings(self.manager.core)
