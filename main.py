# main.py
import sys
import ctypes
import os
import subprocess
import psutil
from PySide6.QtWidgets import QApplication

# Import các thành phần của ứng dụng
from windows.main_window import MainWindow 
from qfluentwidgets import setTheme, Theme

# Các hàm is_running_as_exe, get_application_path, etc.
def is_running_as_exe():
    return getattr(sys, 'frozen', False)

def get_application_path():
    if is_running_as_exe():
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def setup_auto_start(app_path):
    if not is_running_as_exe():
        return
    try:
        import win32com.client
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, "TaskFlow Notifier.lnk")
        notifier_exe_path = os.path.join(app_path, "notifier.exe")
        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = notifier_exe_path
            shortcut.WorkingDirectory = app_path
            shortcut.save()
    except Exception as e:
        print(f"Không thể tạo shortcut khởi động: {e}")

def start_notifier_if_not_running(app_path):
    notifier_exe_path = os.path.join(app_path, "notifier.exe")
    if os.path.exists(notifier_exe_path) and not is_process_running("notifier.exe"):
        try:
            subprocess.Popen([notifier_exe_path], creationflags=subprocess.DETACHED_PROCESS, close_fds=True)
        except Exception as e:
            print(f"Cannot start notifier: {e}")

def main():
    if sys.platform == 'win32':
        os.environ["PYTHONIOENCODING"] = "utf-8"

    app = QApplication(sys.argv)
    
    if sys.platform == 'win32':
        app_id = 'LuongTran.TaskFlow.2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        app_path = get_application_path()
        setup_auto_start(app_path)
        start_notifier_if_not_running(app_path)

    # Luôn đặt theme là Sáng (Light)
    setTheme(Theme.LIGHT)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()