import time
import sys
import os
from datetime import datetime, date, timedelta
from plyer import notification

def add_project_root_to_path():
    """
    Hàm này thêm thư mục gốc của dự án vào đường dẫn hệ thống.
    Việc này đảm bảo rằng kịch bản có thể import các module khác 
    (như db_manager) một cách chính xác khi được chạy độc lập.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Chạy hàm này ngay khi file được import để thiết lập đường dẫn
add_project_root_to_path()

from database.db_manager import DBManager, resource_path

# --- PHẦN CÀI ĐẶT ---
CHECK_INTERVAL_SECONDS = 60  # Khoảng thời gian kiểm tra lại, tính bằng giây (60 giây = 1 phút)
NOTIFY_BEFORE_MINUTES = 30   # Gửi thông báo trước 30 phút so với hạn chót

def check_tasks():
    # In ra thời gian hiện tại để biết kịch bản vẫn đang chạy
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for upcoming tasks...")
    
    # Khởi tạo đối tượng quản lý database
    db = DBManager()
    today = date.today()
    icon_path = ""
    
    # Lấy đường dẫn đến file icon, xử lý trường hợp không tìm thấy
    try:
        icon_path = resource_path("TaskFlowLogo.ico")
    except Exception:
        print("Icon file not found. Using default icon.")

    # Đường dẫn đến file log để lưu lại các task đã được thông báo
    notified_file = resource_path("notified_tasks.log")
    
    # Đọc file log để lấy danh sách ID của các task đã được thông báo trong ngày hôm nay
    try:
        with open(notified_file, 'r') as f:
            # Tạo một tập hợp (set) chứa các ID đã thông báo của ngày hôm nay
            notified_ids_today = {int(line.strip().split(':')[1]) for line in f if line.strip().startswith(today.isoformat())}
    except FileNotFoundError:
        # Nếu file log không tồn tại, tạo một tập hợp rỗng
        notified_ids_today = set()

    tasks_today = db.get_tasks_by_date(today)

    # Lặp qua từng công việc để kiểm tra
    for task in tasks_today:
        if task.completed or task.id in notified_ids_today:
            continue

        # --- THAY ĐỔI: Sử dụng thời gian thông báo của từng task ---
        notify_before_minutes = task.notification_time
        # Bỏ qua nếu người dùng đặt thời gian là 0
        if notify_before_minutes == 0:
            continue
        
        now_dt = datetime.now()
        end_dt = datetime.combine(today, task.end_time)
        time_until_end = end_dt - now_dt
        
        # Kiểm tra nếu thời gian còn lại <= thời gian người dùng đã chọn
        if timedelta(minutes=0) < time_until_end <= timedelta(minutes=notify_before_minutes):
            try:
                notification.notify(
                    title=f"Task Ending Soon: {task.title}",
                    message=f"This task is due at {task.end_time.strftime('%H:%M')}.",
                    app_name="Task Flow",
                    app_icon=icon_path,
                    timeout=10
                )
                print(f"Sent notification for task: '{task.title}'")
                
                with open(notified_file, 'a') as f:
                    f.write(f"{today.isoformat()}:{task.id}\n")
            except Exception as e:
                print(f"ERROR sending notification: {e}")
    
    db.close()

# Đoạn code này chỉ chạy khi bạn thực thi file notifier.py trực tiếp
if __name__ == "__main__":
    # Vòng lặp vô tận để giữ cho kịch bản luôn chạy
    while True:
        # Gọi hàm kiểm tra công việc
        check_tasks()
        # Dừng lại trong một khoảng thời gian đã định trước khi kiểm tra lại
        time.sleep(CHECK_INTERVAL_SECONDS)
