from PySide2.QtWidgets import QWidget, QMessageBox

class simpleErrorPopUp(QWidget):
    def __init__(self, error_message: str):
        super().__init__()
        QMessageBox.warning(self, "ERROR", error_message)



