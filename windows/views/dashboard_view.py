# windows/views/dashboard_view.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QProgressBar, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries

from database.db_manager import DBManager

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardView")
        
        # Kết nối tới database
        self.db = DBManager()

        # Tạo layout chính và khu vực cuộn
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # -- Xây dựng giao diện --
        self.setup_ui()

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)
        
        # Cập nhật dữ liệu
        self.update_dashboard_data()

    def setup_ui(self):
        """Tạo tất cả các thành phần giao diện cho Dashboard."""
        # Header
        header_label = QLabel("Dashboard")
        header_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        header_label.setStyleSheet("color: #2d3748; background-color: transparent;")
        
        subtitle_label = QLabel("Track your progress")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: #718096; background-color: transparent;")
        
        self.layout.addWidget(header_label)
        self.layout.addWidget(subtitle_label)

        # Stats Cards
        stats_layout = QHBoxLayout()
        self.completed_card = self.create_stat_card("Completed", "0", "#10B981", "#ECFDF5")      # Xanh lá nhạt
        self.incomplete_card = self.create_stat_card("Incomplete", "0", "#EF4444", "#FFFBEB")    # Vàng nhạt
        self.total_card = self.create_stat_card("Total Tasks", "0", "#3B82F6", "#DBEAFE")      # Xanh dương nhạt
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.completed_card)
        stats_layout.addWidget(self.incomplete_card)
        self.layout.addLayout(stats_layout)

        # Chart Section
        chart_content, chart_container = self.create_shadow_frame()
        chart_layout = QVBoxLayout(chart_content)
        
        chart_title = QLabel("Task Distribution")
        chart_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        chart_title.setStyleSheet("background-color: transparent;")
        chart_layout.addWidget(chart_title)
        
        self.pie_series = QPieSeries()
        self.pie_series.setHoleSize(0.4)
        
        chart = QChart()
        chart.addSeries(self.pie_series)
        chart.setTitle("")
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        chart_layout.addWidget(chart_view)
        self.layout.addWidget(chart_container)

        # Progress Overview
        progress_content, progress_container = self.create_shadow_frame()
        progress_layout = QVBoxLayout(progress_content)
        
        progress_title = QLabel("Completion Rate")
        progress_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        progress_title.setStyleSheet("background-color: transparent;")
        
        progress_bar_layout = QHBoxLayout()
        progress_text_label = QLabel("Overall Progress")
        progress_text_label.setStyleSheet("background-color: transparent;")
        self.progress_percentage_label = QLabel("0%")
        self.progress_percentage_label.setStyleSheet("background-color: transparent;")
        progress_bar_layout.addWidget(progress_text_label)
        progress_bar_layout.addStretch()
        progress_bar_layout.addWidget(self.progress_percentage_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; background-color: #e5e7eb; height: 12px; border-radius: 6px; }
            QProgressBar::chunk { background-color: #10B981; border-radius: 6px; }
        """)

        progress_layout.addWidget(progress_title)
        progress_layout.addLayout(progress_bar_layout)
        progress_layout.addWidget(self.progress_bar)
        self.layout.addWidget(progress_container)

        # Recent Tasks
        recent_tasks_content, recent_tasks_container = self.create_shadow_frame()
        recent_tasks_layout = QVBoxLayout(recent_tasks_content)

        recent_tasks_title = QLabel("Recent Tasks")
        recent_tasks_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        recent_tasks_title.setStyleSheet("background-color: transparent;")

        self.recent_tasks_list_layout = QVBoxLayout()
        self.recent_tasks_list_layout.setContentsMargins(0, 10, 0, 0)
        self.recent_tasks_list_layout.setSpacing(10)

        recent_tasks_layout.addWidget(recent_tasks_title)
        recent_tasks_layout.addLayout(self.recent_tasks_list_layout)
        
        self.layout.addWidget(recent_tasks_container)
        
        self.layout.addStretch()

    def create_shadow_frame(self):
        """Tạo một cặp widget: container trong suốt và content có đổ bóng."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        content_widget = QFrame()
        content_widget.setObjectName("ContentWidget")
        content_widget.setStyleSheet("#ContentWidget { background-color: white; border-radius: 12px; padding: 15px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        content_widget.setGraphicsEffect(shadow)
        
        container_layout.addWidget(content_widget)
        return content_widget, container

    def create_stat_card(self, title, initial_value, accent_color, bg_color="#fff"):
        """Tạo một thẻ thống kê có đổ bóng."""
        content_widget, container = self.create_shadow_frame()
        card_layout = QVBoxLayout(content_widget)

        content_widget.setStyleSheet(
            f"#ContentWidget {{ background-color: {bg_color}; border-radius: 12px; padding: 15px; }}"
        )

        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #4a5568; background-color: transparent;")
        
        value_label = QLabel(initial_value)
        value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {accent_color}; background-color: transparent;")
        value_label.setObjectName("valueLabel")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        return container

    def create_recent_task_item(self, title, description, is_completed):
        """Tạo một widget cho một công việc gần đây với màu sắc động."""
        item = QFrame()
        
        # --- ĐỊNH NGHĨA MÀU SẮC DỰA TRÊN TRẠNG THÁI ---
        bg_color = ""
        text_title_color = ""
        
        if is_completed:
            bg_color = "#ECFDF5"  # Xanh lá nhạt
            text_title_color = "#10B981" # Tiêu đề cũng xanh lá
        else:
            bg_color = "#FFFBEB"  # Vàng nhạt
            text_title_color = "#F59E0B" # Tiêu đề cũng vàng cam

        item.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(item)
        layout.setContentsMargins(8, 5, 5, 5) # Tăng lề trái để có khoảng cách với border-left

        # Sử dụng HTML để định dạng text
        description_text = description if description else "n/a"
        html_text = (
            f"<span>"
            f"<b style='color: {text_title_color};'>Title: {title}</b> "
            f"<b style='color: {text_title_color};'>- Description: {description_text}</b>"
            f"</span>"
        )
        
        task_label = QLabel(html_text)
        task_label.setWordWrap(True)
        task_label.setAlignment(Qt.AlignTop)
        task_label.setFont(QFont("Segoe UI", 10)) # Đặt font cho label
        
        layout.addWidget(task_label)

        return item
        
    def update_dashboard_data(self):
        """Lấy dữ liệu từ DB và cập nhật giao diện."""
        stats = self.db.get_all_tasks_stats()
        
        completed_count = stats.get("completed", 0)
        incomplete_count = stats.get("incomplete", 0)
        total_count = stats.get("total", 0)

        self.completed_card.findChild(QLabel, "valueLabel").setText(str(completed_count))
        self.incomplete_card.findChild(QLabel, "valueLabel").setText(str(incomplete_count))
        self.total_card.findChild(QLabel, "valueLabel").setText(str(total_count))

        self.pie_series.clear()
        self.pie_series.append("Completed", completed_count).setColor(QColor("#10B981"))
        self.pie_series.append("Incomplete", incomplete_count).setColor(QColor("#EF4444"))

        percentage = 0
        if total_count > 0:
            percentage = round((completed_count / total_count) * 100)
        
        self.progress_bar.setValue(percentage)
        self.progress_percentage_label.setText(f"{percentage}%")

        # Cập nhật danh sách công việc gần đây
        for i in reversed(range(self.recent_tasks_list_layout.count())): 
            self.recent_tasks_list_layout.itemAt(i).widget().setParent(None)

        recent_tasks = self.db.get_recent_tasks(limit=4)
        for title, description, is_completed in recent_tasks:
            task_item = self.create_recent_task_item(title, description, bool(is_completed))
            self.recent_tasks_list_layout.addWidget(task_item)

    def enterEvent(self, event):
        """Được gọi khi con trỏ chuột đi vào widget, hoặc khi widget được hiển thị."""
        super().enterEvent(event)
        self.update_dashboard_data()