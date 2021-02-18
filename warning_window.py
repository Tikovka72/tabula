from PyQt5 import QtWidgets


class WarningWindow(QtWidgets.QDialog):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Дмалог")
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.button_box = QtWidgets.QDialogButtonBox(btns)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        text = QtWidgets.QLabel(text)
        self.layout.addWidget(text)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
