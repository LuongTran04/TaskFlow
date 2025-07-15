import sys
from PySide6.QtWidgets import QApplication
from windows.main_window import MainWindow
from qfluentwidgets import setTheme, Theme

def main():
    app = QApplication(sys.argv)

    setTheme(Theme.LIGHT)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()