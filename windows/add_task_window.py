# add_task_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QTimeEdit, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import QTime, Signal, Qt  # Thêm Qt vào imports
from models.task import Task

class AddTaskWindow(QDialog):
    task_created = Signal(Task)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.setFixedSize(300, 280)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Task Name:"))
        self.title_input = QLineEdit()
        self.title_input.setFocusPolicy(Qt.StrongFocus)  # Thêm dòng này
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Start Time:"))
        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("HH:mm")
        self.start_time_input.setTime(QTime.currentTime())
        layout.addWidget(self.start_time_input)

        layout.addWidget(QLabel("End Time:"))
        self.end_time_input = QTimeEdit()
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setTime(QTime.currentTime().addSecs(3600))
        layout.addWidget(self.end_time_input)

        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setFocusPolicy(Qt.StrongFocus)  # Thêm dòng này
        layout.addWidget(self.desc_input)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.create_task)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_task(self):
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()
        description = self.desc_input.toPlainText().strip()

        if title and start_time < end_time:
            task = Task(title=title, start_time=start_time, end_time=end_time, description=description)
            self.task_created.emit(task)
            self.accept()