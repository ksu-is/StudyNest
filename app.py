from flask import Flask, render_template, request, redirect, url_for

import sqlite3
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
def init_sessions_db():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_settings_db():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            timer_length INTEGER DEFAULT 25,
            task_goal INTEGER DEFAULT 3
        )
    ''')
    # Insert default row if not exists
    c.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
    conn.commit()
    conn.close()


app = Flask(__name__)
init_db()
init_sessions_db()
init_settings_db()
tasks = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/todo", methods = ["GET", "POST"])
def todo():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    
    if request.method == "POST":
        task = request.form["task"]
        if task:
            c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            conn.commit()
        return redirect(url_for("todo"))
    c.execute("SELECT id, task FROM tasks WHERE completed = 0")
    tasks = c.fetchall()
    c.execute("SELECT id, task From tasks WHERE completed = 1")
    completed_tasks = c.fetchall()
    conn.close()
    return render_template("todo.html", tasks=tasks, completed_tasks=completed_tasks)

@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("todo"))

@app.route("/complete/<int:task_id>")
def complete(task_id):
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("todo"))

@app.route("/undo/<int:task_id>")
def undo(task_id):
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("todo"))


@app.route("/timer")
def timer():
    return render_template("timer.html")

@app.route("/stats")
def stats():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
    total_completed_tasks = c.fetchone()[0]
   
    c.execute("SELECT COUNT(*) FROM sessions")
    result = c.fetchone()
    total_sessions = result[0] if result else 0

    # Get all session timestamps
    c.execute("SELECT timestamp FROM sessions ORDER BY timestamp DESC")
    session_dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in c.fetchall()]

    streak = 0
    today = datetime.now().date()

    for date in session_dates:
        if date.date() == today or date.date() == today - timedelta(days=streak):
            streak += 1
        else:
            break


    conn.close()

    labels = ['Completed Tasks', 'Study Sessions']
    values = [total_completed_tasks, total_sessions]

    plt.figure(figsize=(5,5))
    plt.bar(labels, values, color=['green', 'blue'])
    plt.title('Study Progress')
    plt.ylabel('Count')

    # Save chart to static folder
    chart_path = os.path.join('static', 'chart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template("stats.html", total_completed_tasks=total_completed_tasks, total_sessions=total_sessions, streak=streak)


@app.route("/start_session")
def start_session():
    conn = sqlite3.connect('studynest.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions DEFAULT VALUES")
    conn.commit()
    conn.close()
    return redirect(url_for("timer"))



if __name__ == "__main__":
    app.run(debug=True)





