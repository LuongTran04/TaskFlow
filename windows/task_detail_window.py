from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFrame
from models.task import Task
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, 
                            MessageDialog, SubtitleLabel, SwitchButton, TitleLabel)

class TaskDetailWindow(QDialog):
    # Tạo tín hiệu để thông báo cho cửa sổ chính khi task được cập nhật
    task_updated = Signal(Task)
    # Tạo tín hiệu để thông báo cho cửa sổ chính khi task bị xóa (truyền đi ID của task)
    task_deleted = Signal(int)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        # Thiết lập các thuộc tính cơ bản cho cửa sổ
        self.setWindowTitle("Task Details")
        self.task = task
        self.setMinimumSize(400, 200)
        
        # --- BỐ CỤC GIAO DIỆN ---

        # Tạo layout chính theo chiều dọc cho toàn bộ cửa sổ
        main_layout = QVBoxLayout(self)
        # Đặt lề và khoảng cách giữa các thành phần
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Chứa Tiêu đề và Nút gạt Trạng thái
        header_layout = QHBoxLayout()
        self.title_label = TitleLabel(self.task.title)
        # Cho phép tiêu đề tự động xuống dòng nếu quá dài
        self.title_label.setWordWrap(True)
        
        # Tạo nút gạt để thay đổi trạng thái hoàn thành
        self.completion_switch = SwitchButton()
        # Đặt chữ hiển thị cho trạng thái Bật (On) và Tắt (Off)
        self.completion_switch.setOnText("Done")
        self.completion_switch.setOffText("Not Done")
        # Đặt trạng thái ban đầu của nút gạt dựa trên task
        self.completion_switch.setChecked(self.task.completed)
        # Kết nối sự kiện khi trạng thái nút gạt thay đổi với hàm toggle_completion
        self.completion_switch.checkedChanged.connect(self.toggle_completion)

        # Thêm tiêu đề và nút gạt vào layout header
        header_layout.addWidget(self.title_label, 1) # Tham số 1 cho phép tiêu đề chiếm phần lớn không gian
        header_layout.addWidget(self.completion_switch, 0, Qt.AlignRight) # Căn chỉnh nút gạt sang bên phải

        # Chứa các thông tin chi tiết
        body_layout = QVBoxLayout()
        body_layout.setSpacing(10)
        
        # Tạo các nhãn để hiển thị thời gian và mô tả
        self.duration_label = BodyLabel()
        self.desc_label = BodyLabel()
        self.desc_label.setWordWrap(True)

        # Thêm các nhãn vào layout body
        body_layout.addWidget(self.duration_label)   
        body_layout.addWidget(self.desc_label)

        # Chứa các nút hành động (Edit, Delete)
        footer_layout = QHBoxLayout()
        self.edit_btn = PrimaryPushButton("Edit") # Dùng PrimaryPushButton cho hành động chính
        self.delete_btn = PushButton("Delete")

        # Thêm một khoảng trống co giãn để đẩy các nút về bên phải
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.edit_btn)
        footer_layout.addWidget(self.delete_btn)
        
        # Thêm các layout con vào layout chính
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.create_separator()) # Thêm đường kẻ ngang ngăn cách
        main_layout.addLayout(body_layout)
        main_layout.addStretch(1) # Đẩy footer xuống dưới cùng
        main_layout.addLayout(footer_layout)

        # Kết nối sự kiện click của các nút với các hàm tương ứng
        self.edit_btn.clicked.connect(self.edit_task)
        self.delete_btn.clicked.connect(self.confirm_delete)

        # Gọi hàm để hiển thị toàn bộ thông tin của task lên giao diện
        self.update_all_displays()

    def create_separator(self):
        # Hàm tiện ích để tạo một đường kẻ ngang trang trí
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #e0e0e0;")
        return line

    def edit_task(self):
        # Hàm này mở cửa sổ chỉnh sửa công việc
        from windows.edit_task_window import EditTaskWindow
        edit_window = EditTaskWindow(self.task, self)
        
        # Kết nối tín hiệu 'task_updated' từ cửa sổ edit với một hàm xử lý trong cửa sổ này
        edit_window.task_updated.connect(self.handle_task_updated_from_edit)
        
        # Mở cửa sổ edit và chờ cho đến khi nó được đóng
        edit_window.exec()

    def handle_task_updated_from_edit(self, updated_task: Task):
        # Hàm này được gọi khi cửa sổ edit phát ra tín hiệu đã cập nhật xong
        # Cập nhật lại đối tượng task hiện tại của cửa sổ chi tiết
        self.task = updated_task
        # Phát tiếp tín hiệu 'task_updated' lên cho cửa sổ chính (MainWindow)
        self.task_updated.emit(self.task)
        # Cập nhật lại giao diện của cửa sổ chi tiết để hiển thị thông tin mới
        self.update_all_displays()

    def confirm_delete(self):
        # Hàm này hiển thị hộp thoại xác nhận trước khi xóa
        title = "Confirm Delete"
        content = "Are you sure you want to delete this task?"
        w = MessageDialog(title, content, self)
        w.setFixedSize(380, 190)
        # Nếu người dùng nhấn "Yes" (w.exec() trả về True)...
        if w.exec():
            # ...phát tín hiệu task_deleted mang theo ID của task
            self.task_deleted.emit(self.task.id)
            # và đóng cửa sổ chi tiết
            self.accept()

    def toggle_completion(self):
        # Hàm này được gọi khi người dùng gạt nút switch
        is_checked = self.completion_switch.isChecked()
        # Cập nhật trạng thái 'completed' của đối tượng task
        self.task.completed = is_checked
        # Phát tín hiệu báo cho cửa sổ chính biết rằng task đã được cập nhật
        self.task_updated.emit(self.task)
        # Cập nhật lại giao diện của cửa sổ chi tiết
        self.update_all_displays()
    
    def update_all_displays(self):
        # Hàm này đồng bộ hóa toàn bộ giao diện với dữ liệu hiện tại của task
        self.title_label.setText(self.task.title)
        # Thêm/bỏ hiệu ứng gạch ngang dựa trên trạng thái 'completed'
        if self.task.completed:
            self.title_label.setStyleSheet("text-decoration: line-through; color: #888;")
        else:
            self.title_label.setStyleSheet("text-decoration: none;")
        
        # Cập nhật lại các nhãn thông tin khác
        self.duration_label.setText(f"Time: {self.task.start_time.strftime('%H:%M')} → {self.task.end_time.strftime('%H:%M')}")
        self.desc_label.setText(f"Description: {self.task.description}" or 'No description provided.')
        
        # Đảm bảo trạng thái của nút gạt luôn khớp với dữ liệu
        self.completion_switch.setChecked(self.task.completed)