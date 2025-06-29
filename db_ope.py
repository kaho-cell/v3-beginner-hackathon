import sqlite3

conn = sqlite3.connect("schedule_app.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM schedules")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
