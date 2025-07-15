from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from models.task import Task
from qfluentwidgets import (LineEdit, TimeEdit, TextEdit, PushButton, 
                            PrimaryPushButton, BodyLabel)

# Kế thừa từ QDialog gốc của PySide6
class AddTaskWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        
        layout = QVBoxLayout(self)

        # Sử dụng các widget Fluent bên trong QDialog
        layout.addWidget(BodyLabel("Task Name:"))
        self.title_input = LineEdit()
        self.title_input.setPlaceholderText("Enter task name...")
        layout.addWidget(self.title_input)

        layout.addWidget(BodyLabel("Start Time:"))
        self.start_time_input = TimeEdit()
        self.start_time_input.setTime(QTime.currentTime())
        layout.addWidget(self.start_time_input)

        layout.addWidget(BodyLabel("End Time:"))
        self.end_time_input = TimeEdit()
        self.end_time_input.setTime(QTime.currentTime().addSecs(3600))
        layout.addWidget(self.end_time_input)
        
        layout.addWidget(BodyLabel("Description:"))
        self.description_input = TextEdit()
        self.description_input.setPlaceholderText("Enter a description...")
        layout.addWidget(self.description_input)

        button_layout = QHBoxLayout()
        self.save_btn = PrimaryPushButton("Save")
        self.cancel_btn = PushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_task_data(self):
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()
        description = self.description_input.toPlainText().strip()

        if title and start_time < end_time:
            return Task(title=title, start_time=start_time, end_time=end_time, description=description)
        return None