from parse_order import save_order
import sqlite3

def count():
    with sqlite3.connect("voice_order.db") as c:
        return c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
before = count()
try:
     save_order([{"name": "chicken tikka masala", "quantity": 1},
                {"name": "nonsense", "quantity": 1}])
except ValueError as e:
    print("caught:", e)

print("orders before:",before, "after:", count())
