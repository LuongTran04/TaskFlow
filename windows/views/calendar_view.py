import sys
import os
from PySide6.QtWidgets import (
    QWidget, QCalendarWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QScrollArea, QFrame, QToolButton, QStyle
)
from PySide6.QtCore import QDate, Qt, QTime, QTimer
from PySide6.QtGui import QTextCharFormat, QFont, QColor, QIcon
from windows.add_task_window import AddTaskWindow
from models.task import Task
from database.db_manager import DBManager
from windows.task_detail_window import TaskDetailWindow

# Hàm helper để lấy đường dẫn tài nguyên (cho icon)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CalendarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CalendarView")
        
        # Khởi tạo đối tượng quản lý cơ sở dữ liệu
        self.db = DBManager()

        # Tạo layout chính theo chiều ngang
        main_layout = QHBoxLayout(self)

        # Tạo widget lịch
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Kết nối sự kiện click chuột trên lịch với hàm tải công việc
        self.calendar.clicked.connect(self.load_tasks_for_day)
        
        # Gọi hàm để tùy chỉnh giao diện cho lịch
        self.customize_calendar()

        # Tạo layout dọc cho phần bên phải
        self.right_layout = QVBoxLayout()
        
        # Tạo khu vực hiển thị task theo giờ
        self.hourly_view = self.create_hourly_view()
        # Thêm khu vực này vào layout bên phải
        self.right_layout.addWidget(self.hourly_view)

        # Thêm lịch và layout bên phải vào layout chính, chia tỉ lệ
        main_layout.addWidget(self.calendar, 2) # Lịch chiếm 2/5
        main_layout.addLayout(self.right_layout, 3) # Khu vực task chiếm 3/5

        self.setLayout(main_layout)
        
        # Lấy ngày đang được chọn ban đầu
        self.selected_date = self.calendar.selectedDate().toPython()
        # Tải các công việc của ngày đó
        self.load_tasks_for_day(self.calendar.selectedDate())

    def customize_calendar(self):
        """Hàm tập hợp các tùy chỉnh cho QCalendarWidget."""
        
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        style = self.style()
        left_arrow_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)
        right_arrow_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        
        prev_button = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        
        if prev_button:
            prev_button.setIcon(left_arrow_icon)
        if next_button:
            next_button.setIcon(right_arrow_icon)

        stylesheet = """
            QCalendarWidget QTableView { 
                gridline-color: transparent; 
                outline: 0px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #B2EBF2;
            }
            QCalendarWidget QToolButton, QCalendarWidget QLabel#qt_calendar_monthbutton, QCalendarWidget QLabel#qt_calendar_yearbutton {
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:item:selected {
                background-color: #E0F7FA;
                color: #212121;
            }
        """
        self.calendar.setStyleSheet(stylesheet)

        today = QDate.currentDate()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#F5F5F5"))
        fmt.setFontWeight(QFont.Bold)
        self.calendar.setDateTextFormat(today, fmt)
        
    def create_hourly_view(self):
        """Hàm này tạo ra toàn bộ khu vực hiển thị các công việc theo giờ."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True) 
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: white; border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.hour_blocks = []
        for hour in range(24):
            block_frame = QFrame()
            block_frame.setMinimumHeight(60)
            block_layout = QVBoxLayout(block_frame)
            block_layout.setAlignment(Qt.AlignTop)
            block_layout.setContentsMargins(50, 5, 5, 5)
            block_layout.setSpacing(5)
            time_label = QLabel(f"{hour:02d}:00", block_frame)
            time_label.setStyleSheet("color: #606060; background-color: transparent;")
            time_label.move(5, 5)
            block_frame.mouseDoubleClickEvent = lambda event, h=hour: self.open_add_task_window_at_hour(h)
            layout.addWidget(block_frame)
            self.hour_blocks.append(block_frame)

        scroll.setWidget(container)
        return scroll

    def load_tasks_for_day(self, qdate: QDate):
        """Hàm này tải và hiển thị các công việc cho ngày được chọn."""
        self.selected_date = qdate.toPython()
        scroll_position = 0
        if hasattr(self, 'hourly_view') and self.hourly_view:
            scroll_bar = self.hourly_view.verticalScrollBar()
            if scroll_bar:
                scroll_position = scroll_bar.value()
            self.hourly_view.setParent(None)
            self.hourly_view.deleteLater()

        self.hourly_view = self.create_hourly_view()
        self.right_layout.addWidget(self.hourly_view)
        tasks = self.db.get_tasks_by_date(self.selected_date)
        for task in tasks:
            self.display_task(task)

        QTimer.singleShot(0, lambda: self.hourly_view.verticalScrollBar().setValue(scroll_position))

    def open_add_task_window_at_hour(self, hour: int | None):
        """Mở cửa sổ AddTask, truyền vào giờ đã được double-click."""
        dialog = AddTaskWindow(default_hour=hour, parent=self)
        if dialog.exec():
            task = dialog.get_task_data()
            if task:
                self.handle_new_task(task)

    def handle_new_task(self, task: Task):
        self.db.add_task(task, self.selected_date)
        self.load_tasks_for_day(self.calendar.selectedDate())
    
    def handle_task_updated(self, task: Task):
        self.db.update_task(task)
        self.load_tasks_for_day(self.calendar.selectedDate())

    def handle_task_deleted(self, task_id: int):
        self.db.delete_task(task_id)
        self.load_tasks_for_day(self.calendar.selectedDate())

    def display_task(self, task: Task):
        """Hàm này tạo và hiển thị một nhãn cho một task."""
        start_hour = task.start_time.hour
        block = self.hour_blocks[start_hour]
        layout = block.layout()
        label = QLabel(f"{task.title}" if not task.completed else f"<s>{task.title}</s>")
        label.setWordWrap(True)

        if task.completed:
            label.setStyleSheet("""
                background-color: #E8F5E9; border: 1px solid #C8E6C9;
                color: #555; padding: 6px 8px; border-radius: 4px;
                text-decoration: line-through;
            """)
        else:
            label.setStyleSheet(""" 
                background-color: #E3F2FD; border: 1px solid #BBDEFB;
                padding: 6px 8px; border-radius: 4px;
            """)
        
        label.setCursor(Qt.PointingHandCursor)

        def open_detail():
            detail_window = TaskDetailWindow(task, self)
            detail_window.task_updated.connect(self.handle_task_updated)
            detail_window.task_deleted.connect(self.handle_task_deleted)
            detail_window.exec()

        label.mousePressEvent = lambda e: open_detail()
        layout.addWidget(label)