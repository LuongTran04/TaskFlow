import sqlite3
import sys
import os
import shutil
from datetime import datetime, date
from models.task import Task

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DBManager:
    def __init__(self, db_name="taskflow.db"):
        app_data_path = os.path.join(os.getenv('APPDATA'), 'TaskFlow')
        os.makedirs(app_data_path, exist_ok=True)
        
        self.db_path = os.path.join(app_data_path, db_name)
        self.conn = sqlite3.connect(self.db_path)
        
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        
        # Tạo bảng tasks nếu chưa tồn tại
        tasks_query = """
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
        cursor.execute(tasks_query)
        
        # Tạo bảng attachments nếu chưa tồn tại
        attachments_query = """
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            file_path TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        );
        """
        cursor.execute(attachments_query)
        
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN notification_time INTEGER DEFAULT 30")
        except sqlite3.OperationalError:
            pass
        
        self.conn.commit()

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
            task.notification_time
        ))
        task_id = cursor.lastrowid
        
        # Thêm file đính kèm
        for file_path in task.attachments:
            self.add_attachment(task_id, file_path)
            
        self.conn.commit()
        return task_id

    def add_attachment(self, task_id: int, file_path: str):
        query = "INSERT INTO attachments (task_id, file_path) VALUES (?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id, file_path))
        self.conn.commit()

    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        query = "SELECT id, title, start_time, end_time, description, completed, notification_time FROM tasks WHERE task_date = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            task_id, title, start_str, end_str, desc, completed_int, noti_time = row
            
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            attachments = self.get_attachments_for_task(task_id)
            
            task = Task(
                id=task_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=desc,
                completed=bool(completed_int),
                notification_time=noti_time if noti_time is not None else 30,
                attachments=attachments
            )
            tasks.append(task)
            
        return tasks

    def get_attachments_for_task(self, task_id: int) -> list[str]:
        query = "SELECT file_path FROM attachments WHERE task_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        return [row[0] for row in cursor.fetchall()]

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
        
        # Cập nhật file đính kèm
        self.delete_attachments_for_task(task.id)
        for file_path in task.attachments:
            self.add_attachment(task.id, file_path)
            
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.delete_attachments_for_task(task_id)
        
        query = "DELETE FROM tasks WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        self.conn.commit()

    def delete_attachments_for_task(self, task_id: int):
        query = "DELETE FROM attachments WHERE task_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_all_tasks_stats(self):
        query = "SELECT COUNT(id), SUM(completed) FROM tasks"
        cursor = self.conn.cursor()
        cursor.execute(query)
        total_tasks, completed_tasks = cursor.fetchone()

        if total_tasks is None or total_tasks == 0:
            return {"total": 0, "completed": 0, "incomplete": 0}
        
        if completed_tasks is None:
            completed_tasks = 0

        incomplete_tasks = total_tasks - completed_tasks
        return {
            "total": total_tasks,
            "completed": completed_tasks,
            "incomplete": incomplete_tasks
        }
    
    def get_recent_tasks(self, limit=4):
        query = "SELECT title, description, completed FROM tasks ORDER BY id DESC LIMIT ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (limit,))
        return cursor.fetchall()