from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("notes.db")
    conn.execute("""
            CREATE TABLE IF NOT EXISTS notes(
                id INTEGER PRIMARY KEY,
                 content TEXT NOT NULL,
                 title TEXT NOT NULL,
                 date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    with sqlite3.connect("notes.db") as conn:
        notes = conn.execute("SELECT * FROM notes").fetchall()
    return render_template("index.html", notes = notes)

@app.route("/add", methods = ["POST"])
def add():
    title  = request.form.get("title")
    content = request.form.get("content")

    with sqlite3.connect("notes.db") as conn:
        conn.execute("INSERT INTO notes(title, content) VALUES(?, ?)",
                     (title, content))
        conn.commit()
        return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    with sqlite3.connect("notes.db") as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (id,))
        conn.commit()
    return redirect("/")

init_db()

if __name__ == "__main__":
    app.run(debug=True)