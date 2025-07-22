import sys
import ctypes
import os
import subprocess
import psutil
from PySide6.QtWidgets import QApplication
from windows.main_window import MainWindow
from qfluentwidgets import setTheme, Theme

# Kiểm tra xem ứng dụng đang chạy từ file .exe hay từ source code.
def is_running_as_exe():
    return getattr(sys, 'frozen', False)

# Lấy đường dẫn đến thư mục chứa file .exe hoặc file .py.
def get_application_path():
    if is_running_as_exe():
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def is_process_running(process_name):
    # Kiểm tra xem có tiến trình nào với tên cho trước đang chạy hay không.
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def setup_auto_start(app_path):
    # Tạo một shortcut trong thư mục Startup để chạy notifier.exe khi khởi động.
    # Hàm này chỉ chạy khi đã đóng gói thành file .exe
    if not is_running_as_exe():
        return

    try:
        import win32com.client
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, "TaskFlow Notifier.lnk")
        notifier_exe_path = os.path.join(app_path, "notifier.exe")

        # Chỉ tạo shortcut nếu nó chưa tồn tại
        if not os.path.exists(shortcut_path):
            print("Đang tạo shortcut khởi động cùng Windows...")
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = notifier_exe_path
            shortcut.WorkingDirectory = app_path
            shortcut.save()
            print("Đã tạo shortcut thành công.")
    except ImportError:
        print("Lỗi: Cần cài đặt 'pywin32' để tạo shortcut.")
    except Exception as e:
        print(f"Không thể tạo shortcut khởi động: {e}")

def start_notifier_if_not_running(app_path):
    """Kiểm tra và khởi chạy notifier.exe nếu nó chưa chạy."""
    if not is_process_running("notifier.exe"):
        print("Dịch vụ thông báo chưa chạy. Đang khởi động...")
        notifier_exe_path = os.path.join(app_path, "notifier.exe")
        if os.path.exists(notifier_exe_path):
            # Sử dụng cờ DETACHED_PROCESS để chạy notifier.exe hoàn toàn độc lập
            subprocess.Popen([notifier_exe_path], creationflags=subprocess.DETACHED_PROCESS, close_fds=True)
            print("Đã khởi động dịch vụ thông báo.")
        else:
            print("Không tìm thấy file notifier.exe.")

def main():
    app = QApplication(sys.argv)
    
    # Chỉ thực hiện các tác vụ liên quan đến notifier trên Windows
    if sys.platform == 'win32':
        app_id = 'LuongTran.TaskFlow.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Lấy đường dẫn của ứng dụng
        app_path = get_application_path()
        
        # Thiết lập tự khởi động và chạy notifier
        setup_auto_start(app_path)
        start_notifier_if_not_running(app_path)

    setTheme(Theme.LIGHT)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
