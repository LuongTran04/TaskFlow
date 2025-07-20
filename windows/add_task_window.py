from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from models.task import Task
from qfluentwidgets import (LineEdit, TimeEdit, TextEdit, PushButton, 
                            PrimaryPushButton, BodyLabel, MessageDialog)

class AddTaskWindow(QDialog):
    def __init__(self, default_hour: int = None, parent=None):
        super().__init__(parent)
        # Thiết lập tiêu đề và chiều rộng tối thiểu cho cửa sổ
        self.setWindowTitle("Add New Task")
        self.setMinimumWidth(400)

        # Tạo layout chính theo chiều dọc
        layout = QVBoxLayout(self)

        # Thêm nhãn và ô nhập liệu cho tên công việc
        layout.addWidget(BodyLabel("Task Name:"))
        self.title_input = LineEdit()
        self.title_input.setPlaceholderText("Enter task name...")
        layout.addWidget(self.title_input)

        # Thêm nhãn và ô chọn thời gian bắt đầu
        layout.addWidget(BodyLabel("Start Time:"))
        self.start_time_input = TimeEdit()
        # Đặt định dạng hiển thị 24 giờ 
        self.start_time_input.setDisplayFormat("HH:mm")
        layout.addWidget(self.start_time_input)

        # Thêm nhãn và ô chọn thời gian kết thúc
        layout.addWidget(BodyLabel("End Time:"))
        self.end_time_input = TimeEdit()
        # Đặt định dạng hiển thị 24 giờ 
        self.end_time_input.setDisplayFormat("HH:mm")
        layout.addWidget(self.end_time_input)
        
        # Kiểm tra xem có giờ mặc định được truyền vào không
        if default_hour is not None:
            # Nếu có, đặt giờ bắt đầu là giờ được click
            self.start_time_input.setTime(QTime(default_hour, 0))
            # Và đặt giờ kết thúc sau đó 1 tiếng
            self.end_time_input.setTime(QTime(default_hour + 1, 0))
        else:
            # Nếu không, lấy giờ hiện tại của hệ thống
            self.start_time_input.setTime(QTime.currentTime())
            self.end_time_input.setTime(QTime.currentTime().addSecs(3600))
        
        # Thêm nhãn và ô nhập liệu cho mô tả
        layout.addWidget(BodyLabel("Description:"))
        self.description_input = TextEdit()
        self.description_input.setPlaceholderText("Enter a description...")
        layout.addWidget(self.description_input)

        # Tạo layout ngang cho các nút bấm
        button_layout = QHBoxLayout()
        self.save_btn = PrimaryPushButton("Save")
        self.cancel_btn = PushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Kết nối sự kiện click của các nút với các hàm tương ứng
        self.save_btn.clicked.connect(self.validate_and_save)
        self.cancel_btn.clicked.connect(self.reject)

    def validate_and_save(self):
        # Hàm này kiểm tra dữ liệu người dùng nhập trước khi lưu
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time()
        end_time = self.end_time_input.time()

        # Kiểm tra nếu người dùng chưa nhập tên công việc
        if not title:
            # Hiển thị thông báo lỗi và dừng hàm
            w = MessageDialog("Invalid Input", "Task name cannot be empty.", self)
            w.exec()
            return

        # Kiểm tra nếu thời gian bắt đầu sau hoặc bằng thời gian kết thúc
        if start_time >= end_time:
            # Hiển thị thông báo lỗi và dừng hàm
            w = MessageDialog("Invalid Input", "Start time must be earlier than end time.", self)
            w.exec()
            return

        # Nếu mọi thứ hợp lệ, hiển thị thông báo thành công
        successDialog = MessageDialog("Success", "Task added successfully!", self)
        # Sau khi người dùng nhấn OK trên thông báo thành công...
        if successDialog.exec():
            # ...đóng cửa sổ AddTask và trả về tín hiệu 'chấp nhận'
            self.accept()

    def get_task_data(self):
        # Hàm này lấy dữ liệu từ các ô nhập liệu và tạo đối tượng Task
        title = self.title_input.text().strip()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()
        description = self.description_input.toPlainText().strip()

        # Trả về một đối tượng Task mới chứa thông tin đã nhập
        return Task(title=title, start_time=start_time, end_time=end_time, description=description)