from flask import Flask, render_template, request, redirect, url_for

import sqlite3

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

app = Flask(__name__)
init_db()
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

if __name__ == "__main__":
    app.run(debug=True)
