class Mouse:
    """
    class for mouse. contains position of mouse
    """
    def __init__(self, x: int = 0, y: int = 0):
        self.mouse_x = x
        self.mouse_y = y

    def change_pos(self, x, y):
        """
        changes position of mouse to (x, y) coordinate
        """
        self.mouse_x, self.mouse_y = x, y

    def get_pos(self) -> tuple:
        """
        returns mouse position in tuple format (x, y)
        """
        return self.mouse_x, self.mouse_y
