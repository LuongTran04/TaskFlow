from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from models.task import Task

class TaskDetailWindow(QDialog):
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Details of {task.title}")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>📝 {task.title}</b>"))
        layout.addWidget(QLabel(f"🕒 {task.start_time.strftime('%H:%M')} → {task.end_time.strftime('%H:%M')}"))
        desc = QLabel(task.description or "(No description)")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)
