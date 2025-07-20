from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from models.task import Task
from qfluentwidgets import (LineEdit, TimeEdit, TextEdit, PushButton, 
                            PrimaryPushButton, CheckBox, BodyLabel, MessageDialog) # Thêm MessageDialog vào import

class EditTaskWindow(QDialog):
    # Tạo một tín hiệu (signal) để thông báo cho cửa sổ chính khi một task đã được cập nhật
    task_updated = Signal(Task)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        # Thiết lập tiêu đề, lưu trữ đối tượng task và đặt chiều rộng tối thiểu
        self.setWindowTitle("Edit Task")
        self.task = task
        self.setMinimumWidth(400)

        # Tạo layout chính theo chiều dọc
        layout = QVBoxLayout(self)

        # Thêm nhãn và ô nhập liệu cho tên công việc
        layout.addWidget(BodyLabel("Task Name:"))
        self.title_input = LineEdit()
        # Hiển thị tên công việc hiện tại lên ô nhập liệu
        self.title_input.setText(task.title)
        layout.addWidget(self.title_input)

        # Thêm nhãn và ô chọn thời gian bắt đầu
        layout.addWidget(BodyLabel("Start Time:"))
        self.start_time_input = TimeEdit()
        # Đặt định dạng hiển thị 24 giờ 
        self.start_time_input.setDisplayFormat("HH:mm")
        # Đặt thời gian hiện tại của task lên ô chọn giờ
        self.start_time_input.setTime(QTime(task.start_time.hour, task.start_time.minute))
        layout.addWidget(self.start_time_input)

        # Thêm nhãn và ô chọn thời gian kết thúc
        layout.addWidget(BodyLabel("End Time:"))
        self.end_time_input = TimeEdit()
        # Đặt định dạng hiển thị 24 giờ
        self.end_time_input.setDisplayFormat("HH:mm")
        # Đặt thời gian hiện tại của task lên ô chọn giờ
        self.end_time_input.setTime(QTime(task.end_time.hour, task.end_time.minute))
        layout.addWidget(self.end_time_input)

        # Thêm nhãn và ô nhập liệu cho mô tả
        layout.addWidget(BodyLabel("Description:"))
        self.desc_input = TextEdit()
        # Hiển thị mô tả hiện tại của task lên ô nhập liệu
        self.desc_input.setText(task.description)
        layout.addWidget(self.desc_input)

        # Tạo layout ngang cho các nút bấm
        button_layout = QHBoxLayout()
        self.save_btn = PrimaryPushButton("Save Changes")
        self.cancel_btn = PushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Kết nối sự kiện click của các nút với các hàm tương ứng
        self.save_btn.clicked.connect(self.validate_and_update) # Đổi tên hàm để có cả kiểm tra
        self.cancel_btn.clicked.connect(self.reject)

    def validate_and_update(self):
        # Hàm này kiểm tra dữ liệu người dùng nhập trước khi cập nhật
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time()
        end_time = self.end_time_input.time()

        # Kiểm tra nếu tên task bị bỏ trống
        if not title:
            w = MessageDialog("Invalid Input", "Task name cannot be empty.", self)
            w.exec()
            return

        # Kiểm tra nếu thời gian bắt đầu sau hoặc bằng thời gian kết thúc
        if start_time >= end_time:
            w = MessageDialog("Invalid Input", "Start time must be earlier than end time.", self)
            w.exec()
            return
        
        # Nếu dữ liệu hợp lệ, tiến hành cập nhật
        self.task.title = title
        self.task.start_time = start_time.toPython()
        self.task.end_time = end_time.toPython()
        self.task.description = self.desc_input.toPlainText().strip()
        
        # Phát tín hiệu báo cho cửa sổ chính biết rằng task đã được cập nhật
        self.task_updated.emit(self.task)
        # Đóng cửa sổ và trả về tín hiệu 'chấp nhận'
        self.accept()