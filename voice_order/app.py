from flask import Flask, redirect, session, render_template, request, jsonify
from parse_order import extract_items, save_order, get_order_total, get_items_total, get_recent_orders, save_pending, get_pending, delete_pending, DB_PATH
from twilio.twiml.voice_response import VoiceResponse
import os
from dotenv import load_dotenv
import hmac
from functools import wraps
import sqlite3

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")
STAFF_PASSWORD = os.environ.get("STAFF_PASSWORD")
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")
if  not app.secret_key or not STAFF_PASSWORD:
    raise RuntimeError("Set security key and staff password in .env")

def init_db():
    conn =sqlite3.connect(DB_PATH)
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_calls(
            call_sid TEXT PRIMARY KEY,
            items TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
    """)
    conn.commit()
    conn.close()
def seed_menu():
    conn = sqlite3.connect(DB_PATH)
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

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("staff"):
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapper

@app.route("/talk")
@login_required
def talk(): 
    return render_template("index.html")
@app.route("/login", methods = ["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password.encode(), STAFF_PASSWORD.encode()):
            session["staff"] = True
            return redirect("/kitchen")
        error = "wrong password"
    return render_template("login.html", error = error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/order", methods = ["POST"])
@login_required
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
@login_required
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
    gather = resp.gather(input = "speech", action = BASE_URL + "/voice/order",
                         method = "POST", speech_timeout="3", language="en-GB",
                         hints="chicken tikka masala, chicken korma, sheek kebab starter, sheek kebab main, chicken tikka starter, tandoori chicken")
    gather.say("Welcome. What would you like to order?")
    resp.say("Sorry, I didn't hear anything. Goodbye.")
    return str(resp), 200, {"Content-Type": "text/xml"}

def ask_or_confirm(call_sid, items, tries = 0):
    resp = VoiceResponse()
    unclear = [i for i in items if "ambiguous" in i]
    if unclear:
        options = unclear[0]["ambiguous"]
        gather = resp.gather(input = "speech", action = BASE_URL + f"/voice/clarify?tries={tries}",
                             method = "POST", speech_timeout = "3", language="en-GB",
                             hints=", ".join(options))
        gather.say("Did you mean " + " or ".join(options) + "?")
        resp.say("Sorry I didn't hear you. Goodbye")
        return str(resp), 200, {"Content-Type": "text/xml"}

    total = get_items_total(items)
    parts = [str(i["quantity"]) + " " + i["name"] for i in items]
    gather = resp.gather(input = "speech", action = BASE_URL + "/voice/confirm",
                         method = "POST", speech_timeout = "3", language="en-GB",
                         hints="chicken tikka masala, chicken korma, sheek kebab starter, sheek kebab main, chicken tikka starter, tandoori chicken")
    gather.say("So that's " + ", and ".join(parts) +
               ". The total is " + f"{total:.2f}" + " euro. Is that correct? Say yes or no.")
    resp.say("Sorry I didn't hear you. Goodbye")
    return str(resp), 200, {"Content-Type": "text/xml"}

@app.route("/voice/order", methods = ["POST"])
def voice_order():
    call_sid = request.form.get("CallSid")
    speech = request.form.get("SpeechResult","")
    resp = VoiceResponse()

    items = []
    if speech:
        try:
            items = extract_items(speech)
        except ValueError:
            items = []
    if not items:
        resp.say("Sorry I didn't catch any order, let's try again?")
        resp.redirect(BASE_URL + "/voice", method = "POST")
        return str(resp), 200, {"Content-Type": "text/xml"}

    save_pending(call_sid, items)
    return ask_or_confirm(call_sid, items)

@app.route("/voice/clarify", methods = ["POST"])
def voice_clarify():
    tries = int(request.args.get("tries", 0))
    call_sid = request.form.get("CallSid")
    answer = request.form.get("SpeechResult", "").lower()
    words = answer.replace(",", " ").replace(".", " ").split()
    items = get_pending(call_sid)
    resp = VoiceResponse()

    if not items:
        resp.say("Sorry, something went wrong. Let's try again?")
        resp.redirect(BASE_URL + "/voice", method = "POST")
        return str(resp), 200, {"Content-Type": "text/xml"}

    unclear = [i for i in items if "ambiguous" in i]
    if not unclear:
        return ask_or_confirm(call_sid, items)

    item = unclear[0]
    options = item["ambiguous"]
    matches = []
    for option in options:
        others = [w for o in options if o != option for w in o.split()]
        distinct = [w for w in option.split() if w not in others]
        if any(w == d or (len(w) >= 4 and d.startswith(w)) for w in words for d in distinct):
            matches.append(option)

    if len(matches) == 1:
        del item["ambiguous"]
        item["name"] = matches[0]
        save_pending(call_sid, items)
        return ask_or_confirm(call_sid, items)

    if tries >= 2:
        delete_pending(call_sid)
        resp.say("Sorry, I couldn't understand. Please call again.")
        resp.hangup()
        return str(resp), 200, {"Content-Type": "text/xml"}

    return ask_or_confirm(call_sid, items, tries + 1)

@app.route("/voice/confirm", methods = ["POST"])
def voice_confirm():
    tries = int(request.args.get("tries", 0))
    call_sid = request.form.get("CallSid")
    answer =  request.form.get("SpeechResult", "").lower()
    words = answer.replace(",", " ").replace(".", " ").split()
    resp = VoiceResponse()
    items = get_pending(call_sid)

    if not items:
        resp.say("Sorry, something went wrong. Let's try again?")
        resp.redirect(BASE_URL + "/voice", method = "POST")
    elif any(w in words for w in ["no", "nope", "wrong", "not"]):
        delete_pending(call_sid)
        resp.say("okay, Let's try again.")
        resp.redirect(BASE_URL + "/voice", method = "POST")
    elif any(w in words for w in ["yes", "yeah", "correct", "right"]):
        try:
            order_id = save_order(items)
            delete_pending(call_sid)
            resp.say("Thank you, Your order number is " + str(order_id) + ". Goodbye")
            resp.hangup()
        except ValueError:
            resp.say("Sorry there is some problem, Let's try again.")
            resp.redirect(BASE_URL + "/voice", method = "POST")
    elif tries >= 2:
        delete_pending(call_sid)
        resp.say("sorry, I couldn't understand anything, please Call me again")
        resp.hangup()    
    else:
       gather = resp.gather(input="speech", action=BASE_URL + f"/voice/confirm?tries={tries + 1}", speech_timeout="auto")
       gather.say("Sorry, I didn't catch that. Please say yes or no.")
    return str(resp), 200, {"Content-Type": "text/xml"}

@app.route("/orders")
@login_required
def orders_data():
    return jsonify(get_recent_orders())
@app.route("/kitchen")
@login_required
def kitchen():
    return render_template("orders.html")
init_db()
seed_menu()

if __name__ == "__main__":
    app.run(debug=True)