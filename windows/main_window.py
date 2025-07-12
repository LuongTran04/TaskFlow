from PySide6.QtWidgets import (
    QMainWindow, QWidget, QCalendarWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import QDate, Qt
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

        self.hourly_view = self.create_hourly_view()
        self.add_task_btn = QPushButton("➕ Add Task")
        self.add_task_btn.clicked.connect(self.open_add_task_window)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.add_task_btn)
        right_layout.addWidget(self.hourly_view)

        main_layout.addWidget(self.calendar, 2)
        main_layout.addLayout(right_layout, 3)

        self.setCentralWidget(main_widget)
        self.selected_date = self.calendar.selectedDate().toPython()
        self.load_tasks_for_day(self.calendar.selectedDate())

    def create_hourly_view(self):
        scroll = QScrollArea()
        container = QWidget()
        layout = QVBoxLayout(container)

        self.hour_blocks = []

        for hour in range(24):
            block_frame = QFrame()
            block_frame.setFixedHeight(60)
            block_frame.setStyleSheet("QFrame { border-bottom: 1px solid #888; }")
            block_layout = QVBoxLayout(block_frame)
            block_layout.setContentsMargins(50, 5, 5, 5)
            block_layout.setSpacing(5)

            time_label = QLabel(f"{hour:02d}:00", block_frame)
            time_label.setStyleSheet("color: black;")
            time_label.move(5, 5)

            layout.addWidget(block_frame)
            self.hour_blocks.append(block_frame)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def display_task(self, task: Task):
        start_hour = task.start_time.hour
        block = self.hour_blocks[start_hour]
        if not block.layout():
            block.setLayout(QVBoxLayout())

        # Xóa widget cũ nếu tồn tại
        for i in reversed(range(block.layout().count())):
            if block.layout().itemAt(i).widget():
                block.layout().itemAt(i).widget().deleteLater()

        # Tạo label mới với trạng thái hoàn thành
        label = QLabel(f"📌 {task.title}" if not task.completed else f"<s>📌 {task.title}</s>")
        
        # Thiết lập style dựa trên trạng thái hoàn thành
        if task.completed:
            label.setStyleSheet("""
                background-color: #c8e6c9;  /* Màu xanh lá nhạt */
                padding: 6px 8px;
                border-radius: 6px;
                text-decoration: line-through;
                color: #666;
            """)
        else:
            label.setStyleSheet("""
                background-color: #bbdefb;  /* Màu xanh dương nhạt */
                padding: 6px 8px;
                border-radius: 6px;
            """)
        
        label.setCursor(Qt.PointingHandCursor)

        def open_detail():
            detail_window = TaskDetailWindow(task, self)
            detail_window.task_updated.connect(self.handle_task_updated)  # Kết nối signal cập nhật
            detail_window.task_deleted.connect(self.handle_task_deleted)  # Kết nối signal xóa
            detail_window.exec()

        label.mousePressEvent = lambda e: open_detail()
        block.layout().addWidget(label)

    def load_tasks_for_day(self, qdate: QDate):
        self.selected_date = qdate.toPython()

        for block in self.hour_blocks:
            if block.layout():
                while block.layout().count():
                    item = block.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

        tasks = self.db.get_tasks_by_date(self.selected_date)
        for task in tasks:
            self.display_task(task)

    def open_add_task_window(self):
        dialog = AddTaskWindow(self)
        dialog.task_created.connect(self.handle_new_task)
        dialog.exec()
    
    def handle_new_task(self, task: Task):
        self.db.add_task(task, self.selected_date)
        self.display_task(task)
    
    # main_window.py (add these methods to the MainWindow class)
    def handle_task_updated(self, task: Task):
        self.db.update_task(task, self.selected_date)
        # Load lại toàn bộ tasks để cập nhật giao diện
        self.load_tasks_for_day(QDate.fromString(self.selected_date.isoformat(), "yyyy-MM-dd"))

    def handle_task_deleted(self, task_id: int):
        self.db.delete_task(task_id)
        self.load_tasks_for_day(QDate.fromString(self.selected_date.isoformat(), "yyyy-MM-dd"))

    def display_task(self, task: Task):
        start_hour = task.start_time.hour
        block = self.hour_blocks[start_hour]
        if not block.layout():
            block.setLayout(QVBoxLayout())

        label = QLabel(f"📌 {task.title}")
        if task.completed:
            label.setText(f"<s>📌 {task.title}</s>")
            label.setStyleSheet("background-color: lightgreen; padding: 6px 8px; border-radius: 6px; text-decoration: line-through;")
        else:
            label.setStyleSheet("background-color: lightblue; padding: 6px 8px; border-radius: 6px;")
        
        label.setCursor(Qt.PointingHandCursor)

        def open_detail():
            detail_window = TaskDetailWindow(task, self)
            detail_window.task_updated.connect(self.handle_task_updated)
            detail_window.task_deleted.connect(self.handle_task_deleted)
            detail_window.exec()

        label.mousePressEvent = lambda e: open_detail()
        block.layout().addWidget(label)
