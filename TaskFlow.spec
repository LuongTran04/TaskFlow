# -*- mode: python ; coding: utf-8 -*-

# Đây là file cấu hình cho PyInstaller.
# Nó sẽ tạo ra một thư mục chứa cả 2 file: TaskFlow.exe và notifier.exe.

# Phân tích cho ứng dụng giao diện chính (main.py)
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('taskflow.db', '.'),
        ('TaskFlowLogo.ico', '.')
    ],
    hiddenimports=['plyer.platforms.win.notification', 'win32com', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz_main = PYZ(a.pure, a.zipped_data, cipher=None)

# Tạo file thực thi cho giao diện chính
exe_main = EXE(
    pyz_main,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TaskFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = Ứng dụng không có cửa sổ dòng lệnh
    icon='TaskFlowLogo.ico',
)

# Phân tích cho dịch vụ thông báo (notifier.py)
b = Analysis(
    ['notifier.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('taskflow.db', '.'),
        ('TaskFlowLogo.ico', '.')
    ],
    hiddenimports=['plyer.platforms.win.notification'], # Quan trọng để plyer hoạt động
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz_notifier = PYZ(b.pure, b.zipped_data, cipher=None)

# Tạo file thực thi cho dịch vụ thông báo
exe_notifier = EXE(
    pyz_notifier,
    b.scripts,
    [],
    exclude_binaries=True,
    name='notifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # False = Chạy ẩn, không có cửa sổ dòng lệnh
)

# Gom tất cả lại vào một thư mục duy nhất
coll = COLLECT(
    exe_main,
    exe_notifier,
    a.binaries,
    b.binaries,
    a.zipfiles,
    b.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TaskFlow', # Tên của thư mục output cuối cùng
)