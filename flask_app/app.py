from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("orders.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            item NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    with sqlite3.connect("orders.db") as conn:
        orders = conn.execute("SELECT * FROM orders").fetchall()
    return render_template("index.html", orders=orders)


@app.route("/add", methods = ["POST"])
def add():
    item = request.form.get("item")
    with sqlite3.connect("orders.db") as conn:
        conn.execute("INSERT INTO orders (item) VALUES(?)",(item,))
        conn.commit()
    return redirect("/")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
