from PyQt5 import QtWidgets, QtGui, QtCore


class ZeroPointWidget(QtWidgets.QWidget):
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
        self.anim = ZeroPointAndGridAnimation(self, manager=self.manager)

    def move_event(self, x: int, y: int):
        """
        add-on for move for moving animation
        """
        self.move(x, y)

    def get_pos(self) -> tuple:
        """
        gives real center position
        :return: position of center point
        """
        return self.x(), self.y()

    def return_to_zero(self, anim: bool = True):
        """
        sets zero point to center, regenerates grid and updates settings window
        :param anim: sets smoothly
        """
        if anim:
            self.move_animation(self.zero)
        else:
            self.move(*self.zero)
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()
            self.manager.settings_window.update_obj_settings(self.manager.core)

    def set_zero(self, x: int, y: int):
        """
        sets new real center
        """
        self.zero = x, y

    def get_zero(self) -> tuple:
        """
        gets real center
        :return: coordinate in tuple (x, y)
        """
        return self.zero

    def move_animation(self, end_pos: tuple or list):
        """
        handler for move animation. This needs for zero class (self), grid and settings window
        :param end_pos: position where you want to move center
        """
        self.anim.setStartValue(QtCore.QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QtCore.QRect(*end_pos, self.width(), self.height()))

        self.anim.start()


class ZeroPointAndGridAnimation(QtCore.QPropertyAnimation):
    """
    custom animation for
    """
    def __init__(self, parent, anim_type=b"geometry", manager=None):
        """
        :param parent: object which for animation is needed
        :param anim_type: type of animation in PyQt5 form
        :param manager: main class containing all information
        """
        super().__init__(parent, anim_type)
        self.setDuration(300)
        self.manager = manager

    def updateCurrentValue(self, value: QtCore.QRect) -> None:
        """
        QPropertyAnimation method,
        runs animation for zero point and grid, updates settings widget
        :param value: end value in QRect format
        """
        self.targetObject().setGeometry(value)
        if self.manager.grid.show:
            self.manager.grid.set_offset_by_zero_point()
            self.manager.grid.regenerate_grid()
            self.manager.settings_window.update_obj_settings(self.manager.core)
