

from PySide6.QtWidgets import QApplication
from GUI.main_window import MainWindow

def main():
    app = QApplication([])
    mainWnd = MainWindow()
    mainWnd.show()
    app.exec()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
