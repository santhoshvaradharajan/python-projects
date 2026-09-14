from flask import Flask, redirect, session, render_template, request
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    conn =sqlite3.connect("users.db")
    conn.execute("""
         CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL)

    """)
    conn.commit()
@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    return render_template("index.html", username = session["username"])

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect("users.db") as conn:
            conn.execute("INSERT INTO users (username, password) VALUES(?, ?)",
                         (username, password))
            conn.commit()

        return redirect("/login")
    return render_template("register.html")
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect("users.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ? and password = ?",
                         (username, password)).fetchone()
            conn.commit()
        if user:
            session["username"] = username
            return redirect("/")
        return "Invalid Credentials!!"
    return render_template("login.html")
@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
