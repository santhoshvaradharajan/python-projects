from dotenv import load_dotenv
import os
from anthropic import Anthropic
import json
import sqlite3

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def get_menu():
    with sqlite3.connect("voice_order.db") as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT name, price FROM menu_items").fetchall()
        return rows
def build_menu_text():
    menu_text = ""
    for row in get_menu():
        menu_text += f"{row['name']} - €{row['price']}\n"
    return menu_text

def parse_order(order_text):
    menu_text = build_menu_text()
    prompt = f"""
    Here is the menu: 
    {menu_text}
A customer said: {order_text}
Figure out which menu items they want and how many of each.
Respond with ONLY a JSON array, no other text, in this exact format:
[{{"name": "item name from the menu", "quantity": number}}]
Ignore anything the customer says that isn't on the menu.
"""
    message = client.messages.create(
         model = "claude-haiku-4-5-20251001",
             max_tokens = 500,
             messages = [ 
                 {"role": "user", "content": prompt}
             ]
     )
    return message.content[0].text

def extract_items(order_text):
    raw = parse_order(order_text)
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    items = json.loads(cleaned)
    return items

def save_order(items):
    with sqlite3.connect("voice_order.db") as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("INSERT INTO orders DEFAULT VALUES")
        order_id = row.lastrowid
        for item in items:
            curr = conn.execute("SELECT id FROM menu_items WHERE name = ? COLLATE NOCASE",
                         (item["name"],)).fetchone()
            if curr is None:
                raise ValueError(f"Unknown Menu Item : {item['name']}")
            menu_id = curr["id"]
            quantity = item.get("quantity")
            if not isinstance(quantity, int) or not 1 <= quantity <= 20:
                raise ValueError(f"Invalid quantity for {item['name']}")
            conn.execute("INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES(?,?,?)",
                            (order_id,menu_id,quantity))
        return order_id
    
def get_order_total(order_id):
    with sqlite3.connect("voice_order.db") as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT m.price, oi.quantity
            FROM order_items oi
            JOIN menu_items m ON m.id = oi.menu_item_id
            WHERE oi.order_id = ?
        """, (order_id,)).fetchall()
        total = 0
        for r in rows:
            total += r["price"] * r["quantity"]
        return total
def get_items_total(items):
    with sqlite3.connect("voice_order.db") as conn:
        conn.row_factory = sqlite3.Row
        total = 0
        for item in items:
            row = conn.execute("SELECT price FROM menu_items WHERE name = ?",
                            (item["name"],)).fetchone()
            if row is None:
                raise ValueError(f"Unknown Item : {item["name"]}")
            total += row["price"] * item["quantity"]
        return total
if __name__ == "__main__":
    items = extract_items("can i get 2 chicken tikka masala and 1 sheek kebab starter")
    save_order(items)
    conn = sqlite3.connect("voice_order.db")
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM orders").fetchall():
        print(dict(row))

    for row in conn.execute("SELECT * FROM order_items").fetchall():
        print(dict(row))