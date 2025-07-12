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
            task_date TEXT
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_task(self, task: Task, task_date: date):
        query = """
        INSERT INTO tasks (title, description, start_time, end_time, task_date)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (
            task.title,
            task.description,
            task.start_time.strftime("%H:%M"),
            task.end_time.strftime("%H:%M"),
            task_date.isoformat()
        ))
        self.conn.commit()

    def get_tasks_by_date(self, task_date: date) -> list[Task]:
        query = "SELECT title, start_time, end_time, description FROM tasks WHERE task_date = ?"
        cursor = self.conn.execute(query, (task_date.isoformat(),))
        rows = cursor.fetchall()

        tasks = []
        for title, start, end, desc in rows:
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            tasks.append(Task(title, start_time, end_time, desc))
        return tasks

    def close(self):
        self.conn.close()
