from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from models.task import Task
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, 
                            MessageDialog, SubtitleLabel)

class TaskDetailWindow(QDialog):
    task_updated = Signal(Task)
    task_deleted = Signal(int)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.task = task
        
        self.setMinimumSize(420, 280)
        
        layout = QVBoxLayout(self)

        self.title_label = SubtitleLabel()
        layout.addWidget(self.title_label)
        
        self.duration_label = BodyLabel()
        layout.addWidget(self.duration_label)

        self.desc_label = BodyLabel()
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        self.status_label = BodyLabel()
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.edit_btn = PushButton("Edit")
        self.delete_btn = PushButton("Delete")
        self.toggle_btn = PrimaryPushButton()
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.toggle_btn)
        layout.addLayout(button_layout)

        self.close_btn = PushButton("Close")
        layout.addWidget(self.close_btn)

        self.edit_btn.clicked.connect(self.edit_task)
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.toggle_btn.clicked.connect(self.toggle_completion)
        self.close_btn.clicked.connect(self.accept)

        self.update_all_displays()

    def edit_task(self):
        from windows.edit_task_window import EditTaskWindow
        edit_window = EditTaskWindow(self.task, self)
        if edit_window.exec():
            self.task = edit_window.task
            self.task_updated.emit(self.task)
            self.accept()

    def confirm_delete(self):
        title = "Confirm Delete"
        content = "Are you sure you want to delete this task?"
        w = MessageDialog(title, content, self)
        
        w.setFixedSize(380, 190)

        if w.exec():
            self.task_deleted.emit(self.task.id)
            self.accept()

    def toggle_completion(self):
        self.task.completed = not self.task.completed
        self.task_updated.emit(self.task)
        self.update_all_displays()
    
    def update_all_displays(self):
        self.title_label.setText(self.task.title)
        if self.task.completed:
            self.title_label.setStyleSheet("text-decoration: line-through; color: #888;")
        else:
            self.title_label.setStyleSheet("text-decoration: none;")
        
        self.duration_label.setText(f"Duration: {self.task.start_time.strftime('%H:%M')} → {self.task.end_time.strftime('%H:%M')}")
        self.desc_label.setText(f"Description: {self.task.description or '(No description)'}")
        self.status_label.setText(f"Status: {'Completed' if self.task.completed else 'Not completed'}")
        self.toggle_btn.setText("Mark as Done" if not self.task.completed else "Mark as Not Done")