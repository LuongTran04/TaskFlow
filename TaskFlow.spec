# -*- mode: python ; coding: utf-8 -*-

# --- Bước 1: Định nghĩa các file dữ liệu chung ---
# Các file này (database, icon) sẽ được thêm vào cho cả hai file .exe
common_datas = [
    ('taskflow.db', '.'),
    ('TaskFlowLogo.ico', '.')
]

# --- Bước 2: Phân tích và tạo file TaskFlow.exe (Giao diện chính) ---
# 'a' là một biến chứa kết quả phân tích file main.py
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=common_datas,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'win32com',
        'psutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
# pyz_main chứa các module Python đã được nén lại
pyz_main = PYZ(a.pure, a.zipped_data, cipher=None)

# exe_main là đối tượng định nghĩa cách tạo ra file TaskFlow.exe
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
    console=True,  # False = Chạy không có cửa sổ dòng lệnh
    icon='TaskFlowLogo.ico',
)

# --- Bước 3: Phân tích và tạo file notifier.exe (Chạy nền) ---
# 'b' là một biến chứa kết quả phân tích file notifier.py
b = Analysis(
    ['notifier.py'],
    pathex=[],
    binaries=[],
    datas=common_datas,
    hiddenimports=['plyer.platforms.win.notification'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
# pyz_notifier chứa các module Python đã được nén lại cho notifier
pyz_notifier = PYZ(b.pure, b.zipped_data, cipher=None)

# exe_notifier là đối tượng định nghĩa cách tạo ra file notifier.exe
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

# --- Bước 4: Gom tất cả lại vào một thư mục ---
# 'coll' là đối tượng cuối cùng, nó lấy kết quả từ exe_main và exe_notifier
# và đặt chúng vào một thư mục duy nhất.
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
