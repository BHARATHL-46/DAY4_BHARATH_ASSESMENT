import os
import sqlite3
from contextlib import closing
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "tasks.db")


def get_db():
    return sqlite3.connect(app.config["DATABASE"])


def init_db():
    with closing(get_db()) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def home():
    if session.get("logged_in"):
        return redirect(url_for("tasks"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "admin" and password == "password123":
            session["logged_in"] = True
            return redirect(url_for("tasks"))
        error = "Incorrect username or password."
    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tasks")
@login_required
def tasks():
    with closing(get_db()) as db:
        db.row_factory = sqlite3.Row
        task_rows = db.execute(
            "SELECT id, title, description, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
    return render_template("tasks.html", tasks=task_rows)


@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    task_data = request.get_json(silent=True) or {}
    title = str(task_data.get("title", "")).strip()
    description = str(task_data.get("description", "")).strip()
    if not title:
        return jsonify(error="A task title is required."), 400

    with closing(get_db()) as db:
        cursor = db.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description),
        )
        db.commit()
        task_id = cursor.lastrowid

    return jsonify(
        id=task_id,
        title=title,
        description=description,
        completed=False,
    ), 201


init_db()


if __name__ == "__main__":
    app.run(port=5002)
