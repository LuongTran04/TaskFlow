import sqlite3
from datetime import datetime, date
from models.task import Task

class DBManager:
    def __init__(self, db_name="taskflow.db"):
        self.conn = sqlite3.connect(db_name)
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
        cursor = self.conn.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            task_date.isoformat(),
            int(task.completed)
        ))
        self.conn.commit()
        return cursor.lastrowid  # Return the new task ID

    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        query = "SELECT id, title, start_time, end_time, description, completed FROM tasks WHERE task_date = ?"
        cursor = self.conn.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        tasks = []
        for task_id, title, start, end, desc, completed in rows:
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            task = Task(title, start_time, end_time, desc, bool(completed))
            task.id = task_id
            tasks.append(task)
        return tasks

    def update_task(self, task: Task, task_date: date):
        query = """
        UPDATE tasks 
        SET title = ?, description = ?, start_time = ?, end_time = ?, completed = ?
        WHERE id = ?
        """
        self.conn.execute(query, (
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
        self.conn.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()