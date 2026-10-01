from flask import Flask, redirect, session, render_template, request, jsonify
from parse_order import extract_items, save_order, get_order_total
import sqlite3

app = Flask(__name__)

def init_db():
    conn =sqlite3.connect("voice_order.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS menu_items(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
            )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )

    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            menu_item_id INTEGER,
            quantity INTEGER
            )
    """)
    conn.commit()
    conn.close()
def seed_menu():
    conn = sqlite3.connect("voice_order.db")
    count = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                    ("chicken tikka masala", 15.50))
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                    ("chicken korma", 16.00))
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                    ("sheek kebab starter", 7.00))
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                        ("sheek kebab main", 14.00))
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                        ("chicken tikka starter", 6.50))
        conn.execute("INSERT INTO menu_items(name, price) VALUES(?, ?)",
                        ("tandoori chicken", 7.00))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return "VOICE ORDER API is running"
@app.route("/talk")
def talk():
    return render_template("index.html")
    
@app.route("/order", methods = ["POST"])
def create_order():
    data = request.get_json()
    if not data or ("text" not in data and "items" not in data):
        return jsonify({"error" : "text or items required"}),400
    try:
        items = data.get("items") or extract_items(data["text"])
        if not items:
            return jsonify({"error" : "no valid items found"}),400
        order_id = save_order(items)
        total = get_order_total(order_id)
    except ValueError as e:
        return jsonify({"error" : str(e)}),400

    return jsonify({"message" : "order_saved",
                    "order_id" : order_id,
                    "items" : items,
                    "total" : total}),201
@app.route("/parse", methods = ["POST"])
def parse_only():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Text fiels required"}),400
    try:
        items = extract_items(data["text"])
    except ValueError as e:
        return jsonify({"error": str(e)}),400
    if not items:
        return jsonify({"error" : "no valid items found"}),400
    return jsonify({"items": items}),200

init_db()
seed_menu()

if __name__ == "__main__":
    app.run(debug=True)