# windows/views/settings_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FluentIcon, 
                            InfoBar, InfoBarPosition)

# Import đối tượng config từ module utils
from utils.config import config

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsView")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)

        # Tiêu đề
        title_label = QLabel("Settings")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        
        self.layout.addWidget(title_label)
        self.layout.addSpacing(20)

        # -- Nhóm cài đặt Thông báo --
        self.notification_group = SettingCardGroup("Notifications", self)
        
        # Card bật/tắt thông báo
        self.notification_switch = SwitchSettingCard(
            FluentIcon.MESSAGE,
            "Enable Notifications",
            "Receive alerts for upcoming tasks",
            parent=self.notification_group
        )
        self.notification_group.addSettingCard(self.notification_switch)
        
        self.layout.addWidget(self.notification_group)

        # Load trạng thái ban đầu và kết nối tín hiệu
        self.load_initial_settings()
        self.connect_signals()

    def load_initial_settings(self):
        """Tải và áp dụng các cài đặt đã lưu."""
        notifications_enabled = config.get("notifications_enabled")
        self.notification_switch.setChecked(notifications_enabled)

    def connect_signals(self):
        """Kết nối các sự kiện thay đổi trên giao diện với hàm xử lý."""
        self.notification_switch.checkedChanged.connect(self.on_notification_toggled)

    def on_notification_toggled(self, is_checked):
        """Xử lý khi người dùng bật/tắt thông báo."""
        config.set("notifications_enabled", is_checked)
        
        status = "enabled" if is_checked else "disabled"
        InfoBar.success(
            title='Settings Updated',
            content=f"Notifications have been {status}.",
            duration=2000,
            position=InfoBarPosition.TOP,
            parent=self.window()
        ).show()