import os
import sqlite3
from contextlib import closing

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
DATABASE = "users.db"

with closing(sqlite3.connect(DATABASE)) as db:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    db.commit()


@app.route("/")
def home():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        try:
            with closing(sqlite3.connect(DATABASE)) as db:
                db.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
        except sqlite3.IntegrityError:
            return "That email is already registered.", 409

        return redirect(url_for("success"))

    return render_template("register.html")


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        with closing(sqlite3.connect(DATABASE)) as db:
            db.row_factory = sqlite3.Row
            user = db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        return "Invalid email or password.", 401

    return render_template("login.html")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    with closing(sqlite3.connect(DATABASE)) as db:
        db.row_factory = sqlite3.Row
        user = db.execute(
            "SELECT name, email FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run()
