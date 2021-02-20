from PyQt5 import QtWidgets


class WarningWindow(QtWidgets.QDialog):
    """
    dialog window for warnings with "ok" and "cancel" buttons
    """
    def __init__(self, text: str = "", parent=None):
        """
        :param text: warning message
        :param parent: parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Дмалог")
        buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.button_box = QtWidgets.QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        text = QtWidgets.QLabel(text)
        self.layout.addWidget(text)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
