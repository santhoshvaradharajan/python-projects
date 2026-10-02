from flask import Flask, redirect, session, render_template, request, jsonify
from parse_order import extract_items, save_order, get_order_total, get_items_total
from twilio.twiml.voice_response import VoiceResponse
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
@app.route("/voice", methods =["POST"])
def voice():
    resp = VoiceResponse()
    gather = resp.gather(input = "speech", action = "/voice/order",
                         method = "POST", speech_timeout="auto")
    gather.say("Welcome. What would you like to order?")
    resp.say("Sorry, I didn't hear anything. Goodbye.")
    return str(resp), 200, {"Content-Type": "text/xml"}

pending_orders = {}
@app.route("/voice/order", methods = ["POST"])
def voice_order():
    call_sid = request.form.get("CallSid")
    speech = request.form.get("SpeechResult","")
    resp = VoiceResponse()

    items = []
    total = 0
    if speech:
        try:
            items = extract_items(speech)
            total = get_items_total(items) if items else 0
        except ValueError:
            items = []
    if not items:
        resp.say("Sorry I didn't catch any order, let's try again?")
        resp.redirect("/voice", method = "POST")
        return str(resp), 200, {"Content-Type": "text/xml"}
    
    pending_orders[call_sid] = items
    parts = [str(i["quantity"]) + " " + i["name"] for i in items]
    gather = resp.gather(input = "speech", action = "/voice/confirm",
                         method = "POST", speech_timeout = "auto")
    gather.say("So that's " + ", and ".join(parts) +
               ". The total is " + f"{total:.2f}" + " euro. Is that correct? Say yes or no.")
    resp.say("Sorry I didn't hear you. Goodbye")
    return str(resp), 200, {"Content-Type": "text/xml"}
@app.route("/voice/confirm", methods = ["POST"])
def voice_confirm():
    call_sid = request.form.get("CallSid")
    answer =  request.form.get("SpeechResult", "").lower()
    words = answer.replace(",", " ").replace(".", " ").split()
    resp = VoiceResponse()
    items = pending_orders.get(call_sid)

    if not items:
        resp.say("Sorry, something went wrong. Let's try again?")
        resp.redirect("/voice", method = "POST")
    elif any(w in words for w in ["no", "nope", "wrong", "not"]):
        pending_orders.pop(call_sid, None)
        resp.say("okay, Let's try again.")
        resp.redirect("/voice", method = "POST")
    elif any(w in words for w in ["yes", "yup", "correct", "right"]):
        try:
            order_id = save_order(items)
            pending_orders.pop(call_sid, None)
            resp.say("Thank you, Your order number is " + str(order_id) + ". Goodbye")
            resp.hangup()
        except ValueError:
            resp.say("Sorry ther is some problem, Let's try again.")
            resp.redirect("/voice", method = "POST")
    else:
        gather = resp.gather(input = "speech", action = "/voice/confirm",
                                 method = "POST", speech_timeout = "auto")
        gather.say("Sorry, I didn't catch that. Please say yes or no.")
    return str(resp), 200, {"Content-Type": "text/xml"}
init_db()
seed_menu()

if __name__ == "__main__":
    app.run(debug=True)