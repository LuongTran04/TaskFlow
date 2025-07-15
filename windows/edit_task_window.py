from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from models.task import Task
from qfluentwidgets import (LineEdit, TimeEdit, TextEdit, PushButton, 
                            PrimaryPushButton, CheckBox, BodyLabel)

# Kế thừa từ QDialog gốc của PySide6
class EditTaskWindow(QDialog):
    task_updated = Signal(Task)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.task = task
        
        layout = QVBoxLayout(self)

        layout.addWidget(BodyLabel("Task Name:"))
        # Sửa lỗi ValueError: Khởi tạo trước, gán giá trị sau
        self.title_input = LineEdit()
        self.title_input.setText(task.title)
        layout.addWidget(self.title_input)

        layout.addWidget(BodyLabel("Start Time:"))
        self.start_time_input = TimeEdit()
        self.start_time_input.setTime(QTime(task.start_time.hour, task.start_time.minute))
        layout.addWidget(self.start_time_input)

        layout.addWidget(BodyLabel("End Time:"))
        self.end_time_input = TimeEdit()
        self.end_time_input.setTime(QTime(task.end_time.hour, task.end_time.minute))
        layout.addWidget(self.end_time_input)

        layout.addWidget(BodyLabel("Description:"))

        self.desc_input = TextEdit()
        self.desc_input.setText(task.description)
        layout.addWidget(self.desc_input)

        button_layout = QHBoxLayout()
        self.save_btn = PrimaryPushButton("Save Changes")
        self.cancel_btn = PushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.save_btn.clicked.connect(self.update_task)
        self.cancel_btn.clicked.connect(self.reject)

    def update_task(self):
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()

        if title and start_time < end_time:
            self.task.title = title
            self.task.start_time = start_time
            self.task.end_time = end_time
            self.task.description = self.desc_input.toPlainText().strip()
            self.task_updated.emit(self.task)
            self.accept()