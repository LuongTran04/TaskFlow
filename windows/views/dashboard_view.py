# windows/views/dashboard_view.py
import csv
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QProgressBar, QGraphicsDropShadowEffect,
    QPushButton, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap
from PySide6.QtCharts import QChart, QChartView, QPieSeries

# --- Thêm các thư viện cần thiết cho việc tạo PDF chi tiết ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.legends import Legend


from database.db_manager import DBManager

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardView")
        
        # Kết nối tới database
        self.db = DBManager()

        # Tạo layout chính và khu vực cuộn
        main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # -- Xây dựng giao diện --
        self.setup_ui()

        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)
        
        # Cập nhật dữ liệu
        self.update_dashboard_data()

    def setup_ui(self):
        """Tạo tất cả các thành phần giao diện cho Dashboard."""
        # Header
        header_layout = QHBoxLayout()

        header_label = QLabel("Dashboard")
        header_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        header_label.setStyleSheet("color: #2d3748; background-color: transparent;")
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        self.export_button = QPushButton("Export Report")
        self.export_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #38bdf8, stop:1 #6366f1);
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                border: none;
                font-weight: bold;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px rgba(56,189,248,0.15);
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #38bdf8);
            }
        """)
        self.export_button.clicked.connect(self.export_report)
        header_layout.addWidget(self.export_button)

        subtitle_label = QLabel("Track your progress")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: #718096; background-color: transparent;")
        
        self.layout.addLayout(header_layout)
        self.layout.addWidget(subtitle_label)

        # Stats Cards
        stats_layout = QHBoxLayout()
        self.completed_card = self.create_stat_card("Completed", "0", "#10B981", "#ECFDF5")
        self.incomplete_card = self.create_stat_card("Incomplete", "0", "#EF4444", "#FFFBEB")
        self.total_card = self.create_stat_card("Total Tasks", "0", "#3B82F6", "#DBEAFE")
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
        
        self.chart = QChart()
        self.chart.addSeries(self.pie_series)
        self.chart.setTitle("")
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(self.chart)
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
        bg_color, text_title_color = ("", "")
        
        if is_completed:
            bg_color, text_title_color = ("#ECFDF5", "#10B981")
        else:
            bg_color, text_title_color = ("#FFFBEB", "#F59E0B")

        item.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(item)
        layout.setContentsMargins(8, 5, 5, 5)

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
        task_label.setFont(QFont("Segoe UI", 10))
        
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

        percentage = round((completed_count / total_count) * 100) if total_count > 0 else 0
        
        self.progress_bar.setValue(percentage)
        self.progress_percentage_label.setText(f"{percentage}%")

        for i in reversed(range(self.recent_tasks_list_layout.count())): 
            self.recent_tasks_list_layout.itemAt(i).widget().setParent(None)

        recent_tasks = self.db.get_recent_tasks(limit=4)
        for title, description, is_completed in recent_tasks:
            task_item = self.create_recent_task_item(title, description, bool(is_completed))
            self.recent_tasks_list_layout.addWidget(task_item)

    # --- CÁC HÀM XỬ LÝ XUẤT BÁO CÁO ---
    def export_report(self):
        """Mở hộp thoại để lưu file báo cáo."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "TaskFlowReport.pdf", "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        elif file_path.endswith(".pdf"):
            self.export_to_detailed_pdf(file_path)

    def export_to_detailed_pdf(self, file_path):
        """Tạo file PDF báo cáo chi tiết."""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # --- Định nghĩa style và font ---
            font_name, font_name_bold = ('Helvetica', 'Helvetica-Bold')
            try:
                pdfmetrics.registerFont(TTFont('Times-New-Roman', 'times.ttf'))
                pdfmetrics.registerFont(TTFont('Times-New-Roman-Bold', 'timesbd.ttf'))
                font_name, font_name_bold = ('Times-New-Roman', 'Times-New-Roman-Bold')
            except:
                print("Times New Roman font not found. Falling back to Helvetica.")

            styles['Title'].fontName = font_name_bold
            styles['h2'].fontName = font_name_bold
            styles['Normal'].fontName = font_name
            styles['h2'].alignment = TA_CENTER
            
            stat_style_left = ParagraphStyle('StatLeft', fontName=font_name, fontSize=12, leading=16, alignment=TA_LEFT)
            stat_style_right = ParagraphStyle('StatRight', fontName=font_name, fontSize=12, leading=16, alignment=TA_RIGHT)

            # --- Tiêu đề chính ---
            title = Paragraph("Task Statistics Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 24))

            # --- Lấy dữ liệu ---
            stats = self.db.get_all_tasks_stats()
            completed = stats.get("completed", 0)
            incomplete = stats.get("incomplete", 0)
            total = stats.get("total", 0)
            percentage = round((completed / total) * 100) if total > 0 else 0

            # --- Phần thống kê ---
            stats_data = [
                [Paragraph(f"<b>Total Tasks:</b> {total}", stat_style_left), Paragraph(f"<b>Completed Tasks:</b> {completed}", stat_style_right)],
                [Paragraph(f"<b>Completion Rate:</b> {percentage}%", stat_style_left), Paragraph(f"<b>Incomplete Tasks:</b> {incomplete}", stat_style_right)]
            ]
            stats_table = Table(stats_data, colWidths=[doc.width/2 - 10, doc.width/2 - 10])
            stats_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 24))
            
            # --- Biểu đồ tròn (Pie Chart) ---
            if total > 0:
                # --- [SỬA LỖI V4] Hiển thị % trong chart và thêm chú thích (Legend) bên dưới ---
                chart_title = Paragraph("Task Distribution", styles['h2'])
                story.append(chart_title)
                story.append(Spacer(1, 12))

                # Tăng chiều cao của "khung vẽ" để có chỗ cho chú thích
                drawing = Drawing(400, 220)

                pie = Pie()
                pie.width = 150
                pie.height = 150
                # Đẩy Pie Chart lên cao hơn để chừa không gian bên dưới cho chú thích
                pie.x = (drawing.width - pie.width) / 2
                pie.y = 50

                pie.data = [completed, incomplete]
                pie.slices.strokeWidth = 0.5
                pie.slices[0].fillColor = colors.HexColor("#5DCFAB")
                pie.slices[1].fillColor = colors.HexColor("#DF6565")

                # Hiển thị % bên trong các lát cắt
                completed_percent = (completed / total) * 100
                incomplete_percent = (incomplete / total) * 100
                pie.labels = [f'{completed_percent:.0f}%', f'{incomplete_percent:.0f}%']

                

                drawing.add(pie)

                # Tạo chú thích (Legend)
                legend = Legend()
                legend.alignment = 'right'
                # Đặt vị trí chú thích ở dưới chart
                legend.x = drawing.width / 2
                legend.y = 25 # Tọa độ y thấp hơn
                legend.columnMaximum = 2 # Hiển thị trên 1 hàng, 2 cột
                legend.colorNamePairs = [
                    (colors.HexColor("#5DCFAB"), f'Completed ({completed})'),
                    (colors.HexColor("#DF6565"), f'Incomplete ({incomplete})')
                ]
                legend.fontName = font_name
                legend.fontSize = 10

                drawing.add(legend)

                chart_table = Table([[drawing]], hAlign='CENTER')
                story.append(chart_table)
                story.append(Spacer(1, 24))

            # --- Công việc gần đây (Recent Tasks) ---
            # ... (phần code này giữ nguyên)
            recent_tasks_title = Paragraph("Recent Tasks", styles['h2'])
            story.append(recent_tasks_title)
            story.append(Spacer(1, 12))
            recent_tasks = self.db.get_recent_tasks(limit=4)
            if not recent_tasks:
                story.append(Paragraph("No recent tasks found.", styles['Normal']))
            else:
                tasks_data = [['Title', 'Description', 'Status']]
                for title, desc, is_completed in recent_tasks:
                    status = "Completed" if is_completed else "Incomplete"
                    tasks_data.append([
                        Paragraph(title, styles['Normal']),
                        Paragraph(desc if desc else 'N/A', styles['Normal']),
                        status
                    ])
                light_blue = colors.Color(red=(225/255), green=(239/255), blue=(255/255))
                tasks_table = Table(tasks_data, colWidths=[150, 250, 80], hAlign='CENTER')
                tasks_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B92F2")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (-1, -1), font_name),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), light_blue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tasks_table)
            
            doc.build(story)
            print(f"Detailed report successfully exported to {file_path}")
        except Exception as e:
            print(f"Error exporting to detailed PDF: {e}")

    def enterEvent(self, event):
        """Được gọi khi con trỏ chuột đi vào widget, hoặc khi widget được hiển thị."""
        super().enterEvent(event)
        self.update_dashboard_data()