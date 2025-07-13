# edit_task_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QTimeEdit, QTextEdit, QPushButton, QHBoxLayout, QMessageBox, QCheckBox
)
from PySide6.QtCore import QTime, Signal
from models.task import Task

class EditTaskWindow(QDialog):
    task_updated = Signal(Task)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.setFixedSize(320, 300)
        self.task = task

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Task Name:"))
        self.title_input = QLineEdit(task.title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Start Time:"))
        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("HH:mm")
        self.start_time_input.setTime(QTime(task.start_time.hour, task.start_time.minute))
        layout.addWidget(self.start_time_input)

        layout.addWidget(QLabel("End Time:"))
        self.end_time_input = QTimeEdit()
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setTime(QTime(task.end_time.hour, task.end_time.minute))
        layout.addWidget(self.end_time_input)

        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit(task.description)
        layout.addWidget(self.desc_input)

        # Completion status checkbox
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.setChecked(task.completed) 

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.update_task)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_task(self):
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()
        description = self.desc_input.toPlainText().strip()
        

        if title and start_time < end_time:
            self.task.title = title
            self.task.start_time = start_time
            self.task.end_time = end_time
            self.task.description = description
            self.task_updated.emit(self.task)
            self.accept()
        else:
            self.setWindowTitle("Please check your input!")