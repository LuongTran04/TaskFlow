import sqlite3
import sys
import os
import shutil
from datetime import datetime, date
from models.task import Task

def resource_path(relative_path):
    # Hàm này giúp lấy đường dẫn tuyệt đối đến tài nguyên trong thư mục gốc của ứng dụng
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DBManager:
    # Khởi tạo kết nối đến cơ sở dữ liệu
    # Đường dẫn đến cơ sở dữ liệu sẽ được lưu trong thư mục AppData của người dùng
    def __init__(self, db_name="taskflow.db"):
        # Xác định đường dẫn thư mục AppData của người dùng
        app_data_path = os.path.join(os.getenv('APPDATA'), 'TaskFlow')
        os.makedirs(app_data_path, exist_ok=True)
        
        # Đường dẫn cuối cùng đến file database mà ứng dụng sẽ sử dụng
        self.db_path = os.path.join(app_data_path, db_name)

        # Kết nối đến đường dẫn đó. Nếu file chưa tồn tại, sqlite3 sẽ tự tạp mới.
        self.conn = sqlite3.connect(self.db_path)
        
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        
        # Tạo bảng tasks nếu chưa tồn tại
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            task_date TEXT,
            completed INTEGER DEFAULT 0,
            notification_time INTEGER DEFAULT 30
        );
        """
        cursor.execute(query)
        self.conn.commit()

    # Thêm cột 'notification_time' nếu chưa tồn tại
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN notification_time INTEGER DEFAULT 30")
        except sqlite3.OperationalError:
            pass # Bỏ qua lỗi nếu cột đã tồn tại
        
        self.conn.commit()

    # Thêm một công việc mới vào cơ sở dữ liệu
    def add_task(self, task: Task, task_date: date):
        query = """
        INSERT INTO tasks (title, description, start_time, end_time, task_date, completed, notification_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            task_date.isoformat(),
            int(task.completed),
            task.notification_time # Thêm giá trị mới
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    # Lấy danh sách các công việc theo ngày
    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        query = "SELECT id, title, start_time, end_time, description, completed, notification_time FROM tasks WHERE task_date = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            # Thêm noti_time vào danh sách các biến được gán
            task_id, title, start_str, end_str, desc, completed_int, noti_time = row
            
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            # Thêm notification_time khi tạo đối tượng Task
            task = Task(
                id=task_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=desc,
                completed=bool(completed_int),
                notification_time=noti_time if noti_time is not None else 30
            )
            tasks.append(task)
            
        return tasks

    # Cập nhật thông tin của một công việc
    def update_task(self, task: Task):
        query = """
        UPDATE tasks 
        SET title = ?, description = ?, start_time = ?, end_time = ?, completed = ?, notification_time = ?
        WHERE id = ?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            int(task.completed),
            task.notification_time,
            task.id
        ))
        self.conn.commit()

    # Xóa một công việc
    def delete_task(self, task_id: int):
        query = "DELETE FROM tasks WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
