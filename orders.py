import sqlite3

conn = sqlite3.connect("orders.db")

def create_table():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        item TEXT NOT NULL,
        quantity INT NOT NULL,
        status TEXT DEFAULT 'pending',
        time DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
def add_order():
    item = input("item: ").strip()
    quantity = int(input("quantity: "))
    conn.execute("INSERT INTO orders(item, quantity) VALUES(?,?)",
                (item, quantity))
    print("order added!!")
def view_order():
    rows = conn.execute("SELECT * FROM orders WHERE status = 'pending'").fetchall()
    if not rows:
        print("NO orders pending")
        return
    for row in rows:
        print(f"{row[0]}.{row[1]} X {row[2]} | {row[3]} | {row[4]}")
def complete_order():
    view_order()
    order_id = int(input("order id to complete: "))
    conn.execute("UPDATE orders SET status = 'completed' WHERE id= ?", (order_id,))
    conn.commit()
    print("Order Completed!!")
def daily_summary():
    rows = conn.execute("""
         SELECT item, SUM(quantity), COUNT(*)
         FROM orders
         WHERE DATE(time) = DATE('now')
         GROUP BY item
    """).fetchall()
    print("\n today's summary:")
    for row in rows:
        print(f"{row[0]} -> {row[1]} sold, {row[2]} orders")
def avg_order():
    Average = conn.execute("""
        SELECT item, AVG(quantity)
        FROM orders
        GROUP BY item""").fetchall()
    for row in Average:
        print(f"{row[0]} -> Average: {row[1]}")
def delete_order():
    view_order()
    order_id = int(input("give order_id to delete!!: "))
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    print("order deleted!!")
def search_order():
    item = input("search the order: ").strip() 
    rows = conn.execute("SELECT * FROM orders WHERE item LIKE?", (f"%{item}%")).fetchall() 
    if not rows:
        print("no item found")
        return
    for row in rows:
        print(f"{row[0]}.{row[1]} X {row[2]} | {row[3]} | {row[4]}")
def main():
    create_table()
    while True:
        print("\n1.add order")
        print("2.view order")
        print("3.complete order")
        print("4.daily summary")
        print("5.average order")
        print("6.delete order")
        print("7.search order")
        print("8.quit")

        choice = input("choose: ")

        if choice == "1":
            add_order()
        elif choice == "2":
            view_order()
        elif choice == "3":
            complete_order()
        elif choice == "4":
            daily_summary()
        elif choice == "5":
            avg_order()
        elif choice == "6":
            delete_order()
        elif choice == "7":
            search_order()
        elif choice == "8":         
            break
main()
conn.close()     
