#import flask
#plus three helpers to help flask
#render template helps to loads the html file
#requests helps to reads the data from form
#sends the browser back to webpage, then we can see the updated page
from flask import Flask, render_template, request, redirect
#sqlite3 is one of the sql database
import sqlite3
# every flask app starts with this line
# name tells where the file exactly is and helps find the template
app = Flask(__name__)
#define the database
def init_db():
#connecting the database and create a file if it not exists    
    conn = sqlite3.connect("orders.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            item NOT NULL,
            status TEXT DEFAULT 'pending',
            time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
#saves the changes permanantly
#close the connection properly or else it's open unnnecessarily
    conn.commit()
    conn.close()

#define html index and connect with database
#create variable called orders and show whatever in the orders
#fetchall used to return them as a tuple
#loads the html file
#leftside orders says to create a variable in html.index
#rightside orders defines our python variable which we created before
@app.route("/")
def index():
    with sqlite3.connect("orders.db") as conn:
        orders = conn.execute("SELECT * FROM orders").fetchall()
    return render_template("index.html", orders=orders)

#add is the submit button and only accepts post form
@app.route("/add", methods = ["POST"])
#create a variable called item which represents one string which is whatever we types
def add():
    item = request.form.get("item")
    with sqlite3.connect("orders.db") as conn:
# use ? for protect from sql injection attaack
        conn.execute("INSERT INTO orders (item) VALUES(?)",(item,))
        conn.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    with sqlite3.connect("orders.db") as conn:
        conn.execute("DELETE FROM orders WHERE id = ?",(id,))
        conn.commit()
    return redirect("/")

@app.route("/complete/<int:id>")    
def complete(id):
    with sqlite3.connect("orders.db") as conn:
        conn.execute("UPDATE orders SET status = 'completed' WHERE id = ?",(id,))
        conn.commit()
    return redirect("/")    
init_db()

if __name__ == "__main__":
    app.run(debug=True)