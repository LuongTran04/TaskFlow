from PySide6.QtWidgets import (
    QMainWindow, QWidget, QCalendarWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QScrollArea, QFrame, QToolButton, QStyle
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QTextCharFormat, QFont, QColor
from qfluentwidgets import PrimaryPushButton
from windows.add_task_window import AddTaskWindow
from models.task import Task
from database.db_manager import DBManager
from windows.task_detail_window import TaskDetailWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Flow")
        self.setGeometry(100, 100, 1000, 600)

        self.db = DBManager()

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.load_tasks_for_day)
        
        self.customize_calendar()

        self.right_layout = QVBoxLayout()
        
        self.add_task_btn = PrimaryPushButton("Add Task")
        self.add_task_btn.clicked.connect(self.open_add_task_window)
        
        self.hourly_view = self.create_hourly_view()

        self.right_layout.addWidget(self.add_task_btn)
        self.right_layout.addWidget(self.hourly_view)

        main_layout.addWidget(self.calendar, 2)
        main_layout.addLayout(self.right_layout, 3)

        self.setCentralWidget(main_widget)
        self.selected_date = self.calendar.selectedDate().toPython()
        self.load_tasks_for_day(self.calendar.selectedDate())

    def customize_calendar(self):
        """Hàm tập hợp các tùy chỉnh cho QCalendarWidget."""
        
        # Ẩn cột hiển thị số tuần 
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
        scroll = QScrollArea()
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.hour_blocks = []

        for hour in range(24):
            block_frame = QFrame()
            block_frame.setMinimumHeight(60)
            block_frame.setStyleSheet("QFrame { border-bottom: 1px solid #e0e0e0; }")
            block_layout = QVBoxLayout(block_frame)
            block_layout.setAlignment(Qt.AlignTop)
            block_layout.setContentsMargins(50, 5, 5, 5)
            block_layout.setSpacing(5)

            time_label = QLabel(f"{hour:02d}:00", block_frame)
            time_label.setStyleSheet("color: #606060;")
            time_label.move(5, 5)

            layout.addWidget(block_frame)
            self.hour_blocks.append(block_frame)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def load_tasks_for_day(self, qdate: QDate):
        self.selected_date = qdate.toPython()

        if self.hourly_view:
            self.hourly_view.setParent(None)
            self.hourly_view.deleteLater()

        self.hourly_view = self.create_hourly_view()
        self.right_layout.addWidget(self.hourly_view)

        tasks = self.db.get_tasks_by_date(self.selected_date)
        for task in tasks:
            self.display_task(task)

    def open_add_task_window(self):
        dialog = AddTaskWindow(self)
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