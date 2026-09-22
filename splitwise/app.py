from flask import Flask, redirect, session, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "dev-secret-change-later"

def init_db():
    conn = sqlite3.connect("splitwise.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL
            )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS groups(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_by INTEGER NOT NULL
            )
    
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS group_members(
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expense_splits(
            id INTEGER PRIMARY KEY,
            expense_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            share_amount REAL NOT NULL
            )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    with sqlite3.connect("splitwise.db") as conn:
        conn.row_factory = sqlite3.Row
        user_row = conn.execute("SELECT id FROM users WHERE username= ?",(username,)).fetchone()
        user_id = user_row["id"]

        groups = conn.execute(
            "SELECT groups.id, groups.name "
            "FROM group_members "
            "JOIN groups ON group_members.group_id = groups.id "
            "WHERE group_members.user_id = ?",
             (user_id,) ).fetchall()
    return render_template("index.html", user_id = user_id, groups = groups)    

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))

        with sqlite3.connect("splitwise.db") as conn:
            conn.execute("INSERT INTO users(username, password_hash) VALUES(?, ?)",
                         (username, password_hash))
            conn.commit()
        return redirect("/")
    return render_template("register.html")
@app.route("/login", methods = ["GET", "POST"])        
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect("splitwise.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?",
                         (username,)).fetchone()
            conn.commit()
        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/")
        return "Invalid UserName or Password"
    
    return render_template("login.html")

@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/create_group", methods = ["GET", "POST"])
def create_group():
   if "username" not in session:
       return redirect("/login")
   if request.method == "POST":
       group_name = request.form.get("group_name")

       username = session["username"]
       with sqlite3.connect("splitwise.db") as conn:
            user_row = conn.execute("SELECT id FROM users WHERE username = ?",
                              (username,)).fetchone()
            user_id = user_row[0]

            cat = conn.execute("INSERT INTO groups (name, created_by) VALUES(?, ?)",
                              (group_name, user_id))

            group_id = cat.lastrowid

            conn.execute("INSERT INTO group_members(group_id, user_id) VALUES(?, ?)",
                        (group_id, user_id))  
           
       return redirect("/")
   return render_template("create_group.html")

@app.route("/group/<int:group_id>")
def view_group(group_id):
    if "username" not in session:
        return redirect("/login")
    with sqlite3.connect("splitwise.db") as conn:
        conn.row_factory = sqlite3.Row
        group = conn.execute("SELECT * FROM groups WHERE id = ?",
                    (group_id,)).fetchone()
        members = conn.execute(
            "SELECT users.id, users.username "
            "FROM group_members JOIN users "
            "ON group_members.user_id = users.id "
            "WHERE group_members.group_id = ? ",
            (group_id,)
            ).fetchall()
        paid_rows = conn.execute("SELECT paid_by, SUM(amount) AS total_paid FROM expenses WHERE group_id = ? GROUP BY paid_by",
                                   (group_id,)).fetchall()
        paid_totals = {row["paid_by"]: row["total_paid"] for row in paid_rows}

        share_rows = conn.execute(
            "SELECT expense_splits.user_id, SUM(expense_splits.share_amount) AS total_share "
            "FROM expense_splits JOIN expenses ON expense_splits.expense_id = expenses.id "
            "WHERE expenses.group_id = ? GROUP BY expense_splits.user_id",
            (group_id,)
        ).fetchall()
        share_totals = {row["user_id"]: row["total_share"] for row in share_rows}

    balances = {}
    for member in members:
        paid = paid_totals.get(member["id"], 0)
        share = share_totals.get(member["id"], 0)
        balances[member["username"]] = balance(paid, share)

    return render_template("group.html", group = group, members = members, balances = balances)
@app.route("/group/<int:group_id>/add_member", methods = ["POST"])
def add_member(group_id):
    if "username" not in session:
        return redirect("/login")
    username = request.form.get("username")
    if not username:
        return "username not provided", 400
    with sqlite3.connect("splitwise.db") as conn:
        user_row = conn.execute("SELECT id FROM users WHERE username = ?",
                              (username,)).fetchone()
        if user_row is None:
            return "Invalid Username", 400
        target_id = user_row[0]
        conn.execute("INSERT INTO group_members(group_id, user_id) VALUES(?, ?)",
                              (group_id, target_id))
    return redirect(f"/group/{group_id}")
@app.route("/group/<int:group_id>/add_expense", methods = ["POST"])
def add_expense(group_id):
    if "username" not in session:
        return redirect("/login")
    description = request.form.get("description")
    amount = request.form.get("amount")
    if not description or not amount:
        return "description is misssing", 400
    try:
        amount = float(amount)
    except ValueError:
        return "amount must be a number", 400

    username = session["username"]

    with sqlite3.connect("splitwise.db") as conn:
        conn.row_factory = sqlite3.Row
        payer_row = conn.execute("SELECT id FROM users WHERE username = ?",
                     (username,)).fetchone()
        if payer_row is None:

            return "LoggedIn USER NOT FOUND", 400
        paid_by = payer_row["id"]

        curr = conn.execute("INSERT INTO expenses(group_id, description, amount, paid_by) VALUES(?, ?, ?, ?)",
                           (group_id, description, amount, paid_by))
        expense_id = curr.lastrowid

        members = conn.execute("SELECT user_id FROM group_members WHERE group_id = ?",
                     (group_id,)).fetchall()

        if not members:
            return "group has no members", 400

        share_amount = amount/ len(members)

        for m in members:
            conn.execute("INSERT INTO expense_splits(expense_id, user_id, share_amount) VALUES(?,?,?)",
                         (expense_id, m["user_id"], share_amount))
    return redirect(f"/group/{group_id}")
def balance(paid_totals, share_amount):
    balance = paid_totals - share_amount
    return balance

init_db()
if __name__ == "__main__":
    app.run(debug=True)