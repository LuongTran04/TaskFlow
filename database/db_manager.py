import sqlite3
import sys
import os
from datetime import datetime, date
from models.task import Task

def resource_path(relative_path):
    """
    Hàm này lấy đường dẫn tuyệt đối đến một tài nguyên (như database, icon).
    Nó hoạt động cho cả môi trường phát triển (chạy code trực tiếp)
    và môi trường đã đóng gói thành file .exe bằng PyInstaller.
    """
    try:
        # Khi chạy từ file .exe (đặc biệt là --onefile), PyInstaller sẽ tạo một
        # thư mục tạm và lưu đường dẫn của nó vào biến sys._MEIPASS.
        base_path = sys._MEIPASS
    except Exception:
        # Nếu không tìm thấy _MEIPASS, nghĩa là đang chạy code ở môi trường phát triển.
        # Khi đó, đường dẫn gốc là thư mục làm việc hiện tại.
        base_path = os.path.abspath(".")

    # Kết hợp đường dẫn gốc với tên file tương đối để có đường dẫn đầy đủ.
    return os.path.join(base_path, relative_path)


def get_db_path(db_name="taskflow.db"):
    # Hàm này đảm bảo ứng dụng luôn làm việc với một file database cố định,
    # giúp dữ liệu không bị mất mỗi khi khởi động lại phiên bản .exe.
    
    # Kiểm tra xem ứng dụng có đang chạy từ file .exe của PyInstaller không.
    if hasattr(sys, "_MEIPASS"):
        # Đường dẫn đến file DB gốc được đóng gói bên trong thư mục tạm.
        temp_db_path = os.path.join(sys._MEIPASS, db_name)
        # Đường dẫn đến file DB mà người dùng sẽ thực sự tương tác,
        # nằm cùng cấp với file .exe.
        real_db_path = os.path.join(os.getcwd(), db_name)

        # Lần đầu tiên chạy ứng dụng, file DB bên ngoài chưa tồn tại.
        if not os.path.exists(real_db_path):
            # Sao chép file DB từ bên trong gói .exe ra ngoài.
            import shutil
            shutil.copyfile(temp_db_path, real_db_path)

        # Từ lần thứ hai trở đi, hàm sẽ trả về đường dẫn của file DB bên ngoài này.
        return real_db_path
    else:
        # Nếu đang chạy code ở môi trường phát triển, chỉ cần trả về
        # đường dẫn file DB trong thư mục dự án.
        return os.path.join(os.getcwd(), db_name)


class DBManager:
    def __init__(self, db_name="taskflow.db"):
        # Lấy đường dẫn chính xác đến file database
        db_path = get_db_path(db_name)
        # Kết nối đến file database
        self.conn = sqlite3.connect(db_path)
        # Gọi hàm để tạo bảng nếu nó chưa tồn tại
        self.create_table()

    def create_table(self):
        # Hàm này tạo bảng 'tasks' trong database nếu nó chưa có
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            task_date TEXT,
            completed INTEGER DEFAULT 0
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_task(self, task: Task, task_date: date):
        # Hàm này thêm một công việc mới vào bảng 'tasks'
        query = """
        INSERT INTO tasks (title, description, start_time, end_time, task_date, completed)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"), # Chuyển đổi giờ thành chuỗi
            task.end_time.strftime("%H:%M"),   # Chuyển đổi giờ thành chuỗi
            task_date.isoformat(),             # Chuyển đổi ngày thành chuỗi
            int(task.completed)                # Chuyển đổi bool thành số (0 hoặc 1)
        ))
        self.conn.commit()
        # Trả về ID của công việc vừa được tạo
        return cursor.lastrowid

    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        # Hàm này lấy tất cả các công việc của một ngày cụ thể
        query = "SELECT id, title, start_time, end_time, description, completed FROM tasks WHERE task_date = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        # Tạo một danh sách rỗng để chứa các đối tượng Task
        tasks = []
        # Lặp qua từng hàng kết quả từ database
        for row in rows:
            task_id, title, start_str, end_str, desc, completed_int = row
            
            # Chuyển đổi dữ liệu chuỗi từ database về lại đúng định dạng
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            # Tạo một đối tượng Task từ dữ liệu đã lấy
            task = Task(
                id=task_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=desc,
                completed=bool(completed_int)
            )
            # Thêm đối tượng Task vào danh sách
            tasks.append(task)
            
        # Trả về danh sách các công việc
        return tasks

    def update_task(self, task: Task):
        # Hàm này cập nhật thông tin của một công việc đã có dựa trên ID
        query = """
        UPDATE tasks 
        SET title = ?, description = ?, start_time = ?, end_time = ?, completed = ?
        WHERE id = ?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            int(task.completed),
            task.id
        ))
        self.conn.commit()

    def delete_task(self, task_id: int):
        # Hàm này xóa một công việc khỏi database dựa trên ID
        query = "DELETE FROM tasks WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        # Hàm này đóng kết nối với database khi không cần dùng nữa
        self.conn.close()