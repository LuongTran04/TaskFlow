import sys
import ctypes
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from windows.main_window import MainWindow
from qfluentwidgets import setTheme, Theme, isDarkTheme

def main():
    app = QApplication(sys.argv)

    # Thiết lập icon cho ứng dụng trên Windows
    if sys.platform == 'win32':
        app_id = 'LuongTran.TaskFlow.1.0' # Tên định danh tùy ý
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    setTheme(Theme.LIGHT if isDarkTheme() else Theme.LIGHT)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()