import sqlite3
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
rows = conn.execute("""
    SELECT m.name, m.price, oi.quantity
    FROM order_items oi
    JOIN menu_items m ON m.id = oi.menu_item_id
    WHERE oi.order_id = 1
""").fetchall()

total = 0
for r in rows:
    total += r["price"] * r["quantity"]
print("total:", total)