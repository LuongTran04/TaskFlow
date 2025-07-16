import sqlite3
import sys
import os
from datetime import datetime, date
from models.task import Task

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả môi trường dev và PyInstaller. """
    try:
        # PyInstaller tạo một thư mục tạm và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class DBManager:
    def __init__(self, db_name="taskflow.db"):
        db_path = resource_path(db_name)
        self.conn = sqlite3.connect(db_path)

        self.create_table()

    def create_table(self):
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
        query = """
        INSERT INTO tasks (title, description, start_time, end_time, task_date, completed)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            task_date.isoformat(),
            int(task.completed)
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        query = "SELECT id, title, start_time, end_time, description, completed FROM tasks WHERE task_date = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            task_id, title, start_str, end_str, desc, completed_int = row
            
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            
            task = Task(
                id=task_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=desc,
                completed=bool(completed_int)
            )
            tasks.append(task)
            
        return tasks

    def update_task(self, task: Task):
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
        query = "DELETE FROM tasks WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()