from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                              QHBoxLayout, QMessageBox)
from models.task import Task
from PySide6.QtCore import QTime, Signal

class TaskDetailWindow(QDialog):
    task_updated = Signal(Task)
    task_deleted = Signal(int)  # Will emit task ID to delete

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Details of {task.title}")
        self.setFixedSize(300, 200)
        self.task = task

        layout = QVBoxLayout()
        
        # Task title with strike-through if completed
        title_label = QLabel(f"<b>Task name: {task.title}</b>")
        if task.completed:
            title_label.setText(f"<b><s>{task.title}</s></b>")
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(f"Duration: {task.start_time.strftime('%H:%M')} → {task.end_time.strftime('%H:%M')}"))
        desc = QLabel(f"Description: {task.description or '(No description)'}")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Status label
        status_label = QLabel("Completed" if task.completed else "Not completed")
        layout.addWidget(status_label)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_task)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.confirm_delete)
        buttons_layout.addWidget(self.delete_btn)

        self.toggle_btn = QPushButton("Mark Done" if not task.completed else "Mark Undone")
        self.toggle_btn.clicked.connect(self.toggle_completion)
        buttons_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(buttons_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def edit_task(self):
        from windows.edit_task_window import EditTaskWindow
        edit_window = EditTaskWindow(self.task, self)
        edit_window.task_updated.connect(self.handle_task_updated)
        edit_window.exec()

    def handle_task_updated(self, updated_task):
        self.task = updated_task
        self.task_updated.emit(updated_task)
        self.accept()

    def confirm_delete(self):
        reply = QMessageBox.question(
            self,  # parent widget
            "Confirm Delete",  # title
            "Are you sure you want to delete this task?",  # message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # buttons
            QMessageBox.StandardButton.No  # default button
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.task_deleted.emit(self.task.id)
            self.accept()

    def toggle_completion(self):
        self.task.completed = not self.task.completed
        self.update_task_display()  # Thêm hàm cập nhật hiển thị
        self.task_updated.emit(self.task)

    def update_task_display(self):
        # Cập nhật nút
        self.toggle_btn.setText("Mark Done" if not self.task.completed else "Mark Undone")
        
        # Cập nhật trạng thái hoàn thành
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text().startswith("<b>"):
                if self.task.completed:
                    widget.setText(f"<b><s>{self.task.title}</s></b>")
                else:
                    widget.setText(f"<b>{self.task.title}</b>")
                break