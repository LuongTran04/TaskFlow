from PySide6.QtWidgets import (
    QMainWindow, QWidget, QCalendarWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QScrollArea, QFrame, QToolButton, QStyle
)
from PySide6.QtCore import QDate, Qt, QTime, QTimer
from PySide6.QtGui import QTextCharFormat, QFont, QColor, QIcon
from plyer import notification
from windows.add_task_window import AddTaskWindow
from models.task import Task
from database.db_manager import DBManager, resource_path
from windows.task_detail_window import TaskDetailWindow

class MainWindow(QMainWindow):
    def __init__(self):
        # Khởi tạo lớp cha QMainWindow
        super().__init__()
        # Đặt tiêu đề và kích thước ban đầu cho cửa sổ chính
        self.setWindowTitle("Task Flow")
        self.setGeometry(100, 100, 1000, 600)

        # Thử đặt icon cho ứng dụng
        try:
            # Lấy đường dẫn chính xác đến file icon, hoạt động cả khi đã đóng gói
            self.icon_path = resource_path("TaskFlowLogo.ico") 
            self.setWindowIcon(QIcon(self.icon_path))
        except Exception as e:
            # Nếu không tìm thấy file, in ra lỗi và đặt icon_path là None
            print(f"Không tìm thấy file icon: {e}")
            self.icon_path = None # Đặt là None nếu không tìm thấy
    
        # Khởi tạo đối tượng quản lý cơ sở dữ liệu
        self.db = DBManager()

        # Tạo widget trung tâm và layout chính theo chiều ngang
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Tạo widget lịch
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Kết nối sự kiện click chuột trên lịch với hàm tải công việc
        self.calendar.clicked.connect(self.load_tasks_for_day)
        
        # Gọi hàm để tùy chỉnh giao diện cho lịch
        self.customize_calendar()

        # Tạo layout dọc cho phần bên phải
        self.right_layout = QVBoxLayout()
        
        # Tạo khu vực hiển thị task theo giờ
        self.hourly_view = self.create_hourly_view()
        # Thêm khu vực này vào layout bên phải
        self.right_layout.addWidget(self.hourly_view)

        # Thêm lịch và layout bên phải vào layout chính, chia tỉ lệ
        main_layout.addWidget(self.calendar, 2) # Lịch chiếm 2/5
        main_layout.addLayout(self.right_layout, 3) # Khu vực task chiếm 3/5

        # Đặt widget trung tâm cho cửa sổ chính
        self.setCentralWidget(main_widget)
        # Lấy ngày đang được chọn ban đầu
        self.selected_date = self.calendar.selectedDate().toPython()
        # Tải các công việc của ngày đó
        self.load_tasks_for_day(self.calendar.selectedDate())

        # Khởi tạo hệ thống thông báo
        self.setup_notifications()

    def setup_notifications(self):
        """Hàm này thiết lập bộ đếm thời gian để kiểm tra task mỗi phút."""
        # Tạo một tập hợp (set) để lưu ID của các task đã được thông báo, giúp kiểm tra nhanh hơn
        self.notified_tasks_today = set() 

        # Tạo một QTimer
        self.notification_timer = QTimer(self)
        # Kết nối tín hiệu timeout (khi hết giờ) của timer với hàm kiểm tra task
        self.notification_timer.timeout.connect(self.check_upcoming_tasks)
        # Bắt đầu chạy timer, kích hoạt mỗi 60,000 milliseconds (1 phút)
        self.notification_timer.start(60000) 
        
        # Chạy kiểm tra ngay lần đầu tiên khi ứng dụng khởi động
        self.check_upcoming_tasks()

    def check_upcoming_tasks(self):
        """Hàm này được gọi mỗi phút để kiểm tra và gửi thông báo cho các task sắp hết hạn."""
        # Lấy ngày và giờ hiện tại
        today = QDate.currentDate().toPython()
        now = QTime.currentTime()

        # Kiểm tra nếu đã sang ngày mới thì xóa danh sách các task đã thông báo
        if QDate.currentDate() != getattr(self, '_last_checked_date', None):
            self.notified_tasks_today.clear()
            self._last_checked_date = QDate.currentDate()
            
        # Lấy tất cả các task của ngày hôm nay từ database
        tasks_today = self.db.get_tasks_by_date(today)

        # Lặp qua từng task để kiểm tra
        for task in tasks_today:
            # Bỏ qua nếu task đã hoàn thành hoặc đã được thông báo
            if task.completed or task.id in self.notified_tasks_today:
                continue

            # Lấy thời gian kết thúc của task
            end_time = QTime(task.end_time.hour, task.end_time.minute)
            # Tính số giây còn lại cho đến khi task kết thúc
            seconds_until_end = now.secsTo(end_time)

            # Nếu thời gian còn lại nhỏ hơn hoặc bằng 30 phút (1800 giây)
            if 0 < seconds_until_end <= 1800:
                try:
                    # Gửi thông báo trên Windows
                    notification.notify(
                        title=f"Task Ending Soon: {task.title}",
                        message=f"This task is due at {end_time.toString('HH:mm')}.",
                        app_name="Task Flow",
                        app_icon=self.icon_path,
                        timeout=10
                    )
                    # Thêm ID của task vào danh sách đã thông báo để không gửi lại
                    self.notified_tasks_today.add(task.id)
                except Exception as e:
                    print(f"Lỗi khi gửi thông báo: {e}")

    def customize_calendar(self):
        """Hàm tập hợp các tùy chỉnh cho QCalendarWidget."""
        
        # Ẩn cột hiển thị số tuần ở bên trái lịch
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Lấy các icon mũi tên tiêu chuẩn từ style của hệ thống
        style = self.style()
        left_arrow_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)
        right_arrow_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        
        # Tìm các nút bấm chuyển tháng
        prev_button = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        
        # Thay thế icon mặc định bằng icon tiêu chuẩn
        if prev_button:
            prev_button.setIcon(left_arrow_icon)
        if next_button:
            next_button.setIcon(right_arrow_icon)

        # Sử dụng QSS (tương tự CSS) để tùy chỉnh màu sắc và giao diện
        stylesheet = """
            QCalendarWidget QTableView { 
                gridline-color: transparent; 
                outline: 0px; /* Bỏ viền focus khi chọn ngày */
            }
            
            /* Tùy chỉnh thanh điều hướng tháng/năm */
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #B2EBF2;
            }

            /* Đổi màu chữ và icon trên thanh điều hướng */
            QCalendarWidget QToolButton, QCalendarWidget QLabel#qt_calendar_monthbutton, QCalendarWidget QLabel#qt_calendar_yearbutton {
                color: #333333;
            }
            
            /* Tùy chỉnh ô ngày đang được chọn */
            QCalendarWidget QAbstractItemView:item:selected {
                background-color: #E0F7FA;
                color: #212121;
            }
        """
        self.calendar.setStyleSheet(stylesheet)

        # Làm nổi bật ngày hôm nay
        today = QDate.currentDate()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#F5F5F5")) # Đặt màu nền xám nhạt
        fmt.setFontWeight(QFont.Bold) # Đặt chữ in đậm
        self.calendar.setDateTextFormat(today, fmt)
        
    def create_hourly_view(self):
        """Hàm này tạo ra toàn bộ khu vực hiển thị các công việc theo giờ."""
        # Tạo một khu vực có thể cuộn
        scroll = QScrollArea()
        scroll.setWidgetResizable(True) 
        scroll.setFrameShape(QFrame.NoFrame) # Bỏ viền của khu vực cuộn
        scroll.setStyleSheet("QScrollArea { background-color: white; border: none; }")

        # Tạo một widget container để chứa tất cả các khung giờ
        container = QWidget()
        
        # Tạo layout dọc cho container
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tạo một danh sách để lưu lại tham chiếu đến 24 khung giờ
        self.hour_blocks = []

        # Lặp 24 lần để tạo 24 khung giờ
        for hour in range(24):
            # Mỗi khung giờ là một QFrame
            block_frame = QFrame()
            block_frame.setMinimumHeight(60)
            
            # Tạo layout dọc bên trong mỗi khung giờ để chứa các task
            block_layout = QVBoxLayout(block_frame)
            block_layout.setAlignment(Qt.AlignTop) # Căn chỉnh các task về phía trên
            block_layout.setContentsMargins(50, 5, 5, 5) # Đặt lề để có chỗ cho nhãn giờ
            block_layout.setSpacing(5) # Đặt khoảng cách giữa các task

            # Tạo nhãn hiển thị giờ (ví dụ: 09:00)
            time_label = QLabel(f"{hour:02d}:00", block_frame)
            time_label.setStyleSheet("color: #606060; background-color: transparent;")
            time_label.move(5, 5)
            
            # Bắt sự kiện double-click trên khung giờ để mở cửa sổ thêm task
            # Dùng lambda để "bắt" giá trị 'hour' hiện tại của vòng lặp
            block_frame.mouseDoubleClickEvent = lambda event, h=hour: self.open_add_task_window_at_hour(h)

            # Thêm khung giờ vào layout chính
            layout.addWidget(block_frame)
            # Thêm khung giờ vào danh sách để truy cập sau này
            self.hour_blocks.append(block_frame)

        # Đặt container làm widget chính cho khu vực cuộn
        scroll.setWidget(container)
        return scroll

    def load_tasks_for_day(self, qdate: QDate):
        """Hàm này tải và hiển thị các công việc cho ngày được chọn."""
        # Cập nhật ngày đang được chọn
        self.selected_date = qdate.toPython()

        # Lưu lại vị trí của thanh cuộn trước khi vẽ lại giao diện
        scroll_position = 0
        if hasattr(self, 'hourly_view') and self.hourly_view:
            scroll_bar = self.hourly_view.verticalScrollBar()
            if scroll_bar:
                scroll_position = scroll_bar.value()
            # Xóa bỏ hoàn toàn hourly_view cũ để tránh lỗi hiển thị
            self.hourly_view.setParent(None)
            self.hourly_view.deleteLater()

        # Tạo lại khu vực hiển thị task để xóa sạch dữ liệu cũ
        self.hourly_view = self.create_hourly_view()
        self.right_layout.addWidget(self.hourly_view)

        # Lấy các task của ngày mới từ database
        tasks = self.db.get_tasks_by_date(self.selected_date)
        # Hiển thị từng task lên giao diện
        for task in tasks:
            self.display_task(task)

        # Đặt lại vị trí thanh cuộn về vị trí đã lưu
        # Dùng QTimer.singleShot để đảm bảo lệnh được chạy sau khi giao diện đã được vẽ xong
        QTimer.singleShot(0, lambda: self.hourly_view.verticalScrollBar().setValue(scroll_position))

    def open_add_task_window_at_hour(self, hour: int | None):
        """Mở cửa sổ AddTask, truyền vào giờ đã được double-click."""
        dialog = AddTaskWindow(default_hour=hour, parent=self)
        # Nếu người dùng nhấn Save (dialog.exec() trả về True)...
        if dialog.exec():
            task = dialog.get_task_data()
            if task:
                # ...thì xử lý việc thêm task mới
                self.handle_new_task(task)

    def handle_new_task(self, task: Task):
        """Hàm này xử lý việc thêm task mới vào database và cập nhật giao diện."""
        self.db.add_task(task, self.selected_date)
        self.load_tasks_for_day(self.calendar.selectedDate())
    
    def handle_task_updated(self, task: Task):
        """Hàm này xử lý việc cập nhật task trong database và giao diện."""
        self.db.update_task(task)
        self.load_tasks_for_day(self.calendar.selectedDate())

    def handle_task_deleted(self, task_id: int):
        """Hàm này xử lý việc xóa task khỏi database và giao diện."""
        self.db.delete_task(task_id)
        self.load_tasks_for_day(self.calendar.selectedDate())

    def display_task(self, task: Task):
        """Hàm này tạo và hiển thị một nhãn cho một task."""
        # Lấy giờ bắt đầu để xác định vị trí đặt task
        start_hour = task.start_time.hour
        block = self.hour_blocks[start_hour]
        
        layout = block.layout()

        # Tạo nhãn với tên công việc, có gạch ngang nếu đã hoàn thành
        label = QLabel(f"{task.title}" if not task.completed else f"<s>{task.title}</s>")
        label.setWordWrap(True) # Cho phép xuống dòng nếu tên quá dài

        # Đặt màu nền khác nhau cho task đã và chưa hoàn thành
        if task.completed:
            label.setStyleSheet("""
                background-color: #E8F5E9; border: 1px solid #C8E6C9;
                color: #555; padding: 6px 8px; border-radius: 4px;
                text-decoration: line-through;
            """)
        else:
            label.setStyleSheet(""" 
                background-color: #E3F2FD; border: 1px solid #BBDEFB;
                padding: 6px 8px; border-radius: 4px;
            """)
        
        # Đổi con trỏ chuột khi di vào task để cho biết có thể click
        label.setCursor(Qt.PointingHandCursor)

        # Tạo một hàm nội bộ để mở cửa sổ chi tiết
        def open_detail():
            detail_window = TaskDetailWindow(task, self)
            # Kết nối các tín hiệu từ cửa sổ chi tiết với các hàm xử lý ở đây
            detail_window.task_updated.connect(self.handle_task_updated)
            detail_window.task_deleted.connect(self.handle_task_deleted)
            detail_window.exec()

        # Gán sự kiện click chuột trên nhãn với hàm vừa tạo
        label.mousePressEvent = lambda e: open_detail()
        # Thêm nhãn task vào khung giờ tương ứng
        layout.addWidget(label)
