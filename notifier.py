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
    """
    Hàm chính để kiểm tra các công việc sắp hết hạn.
    Hàm này được gọi định kỳ bởi vòng lặp ở dưới.
    """
    # In ra thời gian hiện tại để biết kịch bản vẫn đang chạy
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Bắt đầu kiểm tra công việc...")
    
    # Khởi tạo đối tượng quản lý database
    db = DBManager()
    today = date.today()
    icon_path = ""
    
    # Lấy đường dẫn đến file icon, xử lý trường hợp không tìm thấy
    try:
        icon_path = resource_path("TaskFlowLogo.ico")
    except Exception:
        print(" - Không tìm thấy file icon, sẽ gửi thông báo không có icon.")

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

    print(f" - Ngày hôm nay: {today.isoformat()}")
    # Lấy tất cả các công việc của ngày hôm nay từ database
    tasks_today = db.get_tasks_by_date(today)
    print(f" - Tìm thấy {len(tasks_today)} công việc cho ngày hôm nay.")

    # Lặp qua từng công việc để kiểm tra
    for task in tasks_today:
        print(f"\n--- Đang xử lý task: '{task.title}' (ID: {task.id}) ---")
        print(f"   + Trạng thái hoàn thành: {task.completed}")
        print(f"   + Đã thông báo hôm nay chưa: {task.id in notified_ids_today}")

        # Bỏ qua nếu công việc đã hoàn thành hoặc đã được thông báo
        if task.completed or task.id in notified_ids_today:
            print("   -> Bỏ qua task này.")
            continue

        # Lấy thời gian hiện tại và thời gian kết thúc của công việc
        now_dt = datetime.now()
        end_dt = datetime.combine(today, task.end_time)
        
        # Tính toán khoảng thời gian còn lại
        time_until_end = end_dt - now_dt
        
        print(f"   + Thời gian hiện tại: {now_dt.strftime('%H:%M:%S')}")
        print(f"   + Thời gian kết thúc: {end_dt.strftime('%H:%M:%S')}")
        print(f"   + Thời gian còn lại: {time_until_end}")

        # Kiểm tra xem thời gian còn lại có nằm trong khoảng thông báo hay không
        if timedelta(minutes=0) < time_until_end <= timedelta(minutes=NOTIFY_BEFORE_MINUTES):
            print("   !!! ĐIỀU KIỆN THÔNG BÁO ĐƯỢC THỎA MÃN. Đang gửi thông báo...")
            try:
                # Gửi thông báo trên Windows
                notification.notify(
                    title=f"Task Ending Soon: {task.title}",
                    message=f"This task is due at {task.end_time.strftime('%H:%M')}.",
                    app_name="Task Flow",
                    app_icon=icon_path,
                    timeout=10 # Thông báo hiển thị trong 10 giây
                )
                print(f"   +++ Gửi thông báo THÀNH CÔNG cho task: '{task.title}'")
                
                # Ghi lại ID của task đã thông báo vào file log để không gửi lại
                with open(notified_file, 'a') as f:
                    f.write(f"{today.isoformat()}:{task.id}\n")
            except Exception as e:
                print(f"   --- LỖI khi gửi thông báo cho task: {e}")
        else:
            print("   -> Chưa đến giờ thông báo.")

    # Đóng kết nối database sau khi kiểm tra xong
    db.close()

# Đoạn code này chỉ chạy khi bạn thực thi file notifier.py trực tiếp
if __name__ == "__main__":
    # Vòng lặp vô tận để giữ cho kịch bản luôn chạy
    while True:
        # Gọi hàm kiểm tra công việc
        check_tasks()
        # Dừng lại trong một khoảng thời gian đã định trước khi kiểm tra lại
        time.sleep(CHECK_INTERVAL_SECONDS)
