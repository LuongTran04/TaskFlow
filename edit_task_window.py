from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
    QDateEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
from models.task import Task

class EditTaskWindow(QWidget):
    task_edited = Signal(Task)
    
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.setWindowTitle("Edit Task")
        self.setGeometry(650, 200, 300, 250)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tên task
        layout.addWidget(QLabel("Task Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(str(self.task.name) if self.task.name is not None else "")
        layout.addWidget(self.name_input)
        
        # Deadline
        layout.addWidget(QLabel("Due Date:"))
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.fromString(self.task.due_date, "yyyy-MM-dd"))
        layout.addWidget(self.due_date_input)
        
        # Mô tả
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        self.description_input.setText(self.task.description)
        layout.addWidget(self.description_input)
        
        # Nút lưu thay đổi
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_task)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
    def save_task(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Task name cannot be empty!")
            return
            
        edited_task = Task(
            name=name,
            due_date=self.due_date_input.date().toString("yyyy-MM-dd"),
            description=self.description_input.text()
        )
        
        self.task_edited.emit(edited_task)
        self.close()