class Mouse:
    def __init__(self, x=0, y=0):
        self.mouse_x = x
        self.mouse_y = y

    def change_pos(self, x, y):
        self.mouse_x, self.mouse_y = x, y

    def change_x(self, x):
        self.mouse_x = x

    def change_y(self, y):
        self.mouse_y = y

    def get_pos(self):
        return self.mouse_x, self.mouse_y

    def get_x(self):
        return self.mouse_x

    def get_y(self):
        return self.mouse_y
