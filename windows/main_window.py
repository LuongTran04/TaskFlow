# windows/main_window.py
import sys
import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtGui import QIcon
from qfluentwidgets import NavigationInterface, NavigationItemPosition, FluentIcon
from plyer import notification
from PySide6.QtCore import QTimer

# Import các view
from windows.views.calendar_view import CalendarView
from windows.views.dashboard_view import DashboardView

# Hàm helper để lấy đường dẫn tài nguyên
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    # Giả sử file icon nằm trong thư mục gốc
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Flow")
        self.setGeometry(100, 100, 1200, 750)

        try:
            self.setWindowIcon(QIcon(resource_path("TaskFlowLogo.ico")))
        except Exception as e:
            print(f"Không tìm thấy file icon chính: {e}")

        # Tạo widget trung tâm và layout chính
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tạo thanh điều hướng (Navigation)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True, showReturnButton=False)
        self.main_layout.addWidget(self.navigation_interface)

        # Tạo QStackedWidget để chứa các trang
        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget, 1)

        # Khởi tạo các trang con (view)
        self.calendar_view = CalendarView(self)
        self.dashboard_view = DashboardView(self)
        
        # Thêm các trang vào QStackedWidget
        self.stacked_widget.addWidget(self.calendar_view)
        self.stacked_widget.addWidget(self.dashboard_view)

        # Thêm các nút bấm vào thanh điều hướng
        self.add_navigation_items()
        
        self.setCentralWidget(self.main_widget)
        
        # Khởi tạo hệ thống thông báo
        self.setup_notifications()

    def add_navigation_items(self):
        """Thêm các nút điều hướng cho các trang."""
        self.navigation_interface.addItem(
            routeKey='calendar_view',
            icon=FluentIcon.CALENDAR,
            text='Calendar',
            onClick=lambda: self.stacked_widget.setCurrentWidget(self.calendar_view)
        )
        self.navigation_interface.addItem(
            routeKey='dashboard_view',
            icon=FluentIcon.DOCUMENT,
            text='Dashboard',
            onClick=self.on_dashboard_clicked
        )
        
        # Đặt trang Calendar làm trang mặc định
        self.navigation_interface.setCurrentItem('calendar_view')

    def on_dashboard_clicked(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.update_dashboard_data()

    def setup_notifications(self):
        """Hàm này thiết lập bộ đếm thời gian để kiểm tra task mỗi phút."""
        if not hasattr(self, 'calendar_view') or not hasattr(self.calendar_view, 'db'):
            return

        self.db_manager = self.calendar_view.db
        self.notified_tasks_today = set() 
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_upcoming_tasks)
        # Bắt đầu chạy timer, kích hoạt mỗi 60,000 milliseconds (1 phút)
        self.notification_timer.start(60000)
        self.check_upcoming_tasks() # Chạy kiểm tra ngay lần đầu

    def check_upcoming_tasks(self):
        """Kiểm tra và gửi thông báo."""
        from PySide6.QtCore import QDate, QTime

        today = QDate.currentDate().toPython()
        now = QTime.currentTime()

        if QDate.currentDate() != getattr(self, '_last_checked_date', None):
            self.notified_tasks_today.clear()
            self._last_checked_date = QDate.currentDate()
            
        tasks_today = self.db_manager.get_tasks_by_date(today)

        for task in tasks_today:
            if task.completed or task.id in self.notified_tasks_today:
                continue

            end_time = QTime(task.end_time.hour, task.end_time.minute)
            seconds_until_end = now.secsTo(end_time)
            
            notification_seconds = task.notification_time * 60

            if 0 < seconds_until_end <= notification_seconds:
                try:
                    notification.notify(
                        title=f"Task Reminder: {task.title}",
                        message=f"This task is scheduled to end at {end_time.toString('HH:mm')}.",
                        app_name="Task Flow",
                        app_icon=resource_path("TaskFlowLogo.ico"),
                        timeout=10
                    )
                    self.notified_tasks_today.add(task.id)
                except Exception as e:
                    print(f"Lỗi khi gửi thông báo: {e}")