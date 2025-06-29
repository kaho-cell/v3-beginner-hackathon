
import sqlite3

DB_NAME = "./schedule_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        deadline TEXT,
        status TEXT,
        priority TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    title TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    is_all_day BOOLEAN,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
    )
    """)
    conn.commit()
    conn.close()

def add_task(title, description, priority, deadline, estimated_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, priority, deadline, estimated_time)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, priority, deadline, estimated_time))
    conn.commit()
    conn.close()

def add_schedule(title, date, start_time, end_time, is_all_day, task_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    start_time_str = f"{date} {start_time}"
    end_time_str = f"{date} {end_time}"

    cursor.execute("""
        INSERT INTO schedules (task_id, title, start_time, end_time, is_all_day)
        VALUES (?, ?, ?, ?, ?)
    """, (task_id, title, start_time_str, end_time_str, is_all_day))
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, deadline, status, priority FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_all_tasks(df):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")  # 全削除して入れ直す方針
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO tasks (title, deadline, status, priority)
            VALUES (?, ?, ?, ?)
        """, (row["内容"], row["期限"], row["進行状況"], row["優先度"]))
    conn.commit()
    conn.close()

def update_schedule_datetime(event_id, new_start, new_end):
    """
    イベントIDに基づいて、開始日時と終了日時を更新する
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE schedules
        SET start_time = ?, end_time = ?
        WHERE id = ?
    """, (new_start, new_end, event_id))

    conn.commit()
    conn.close()