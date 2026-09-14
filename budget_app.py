import sqlite3

conn = sqlite3.connect("budget.db")

def create_table():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS TRANSACTIONS(
        id INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        amount INTEGER NOT NULL,
        type TEXT NOT NULL,
        category TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP)
    """)
    conn.commit()

def add_income():
    amount = int(input("Amount: "))
    description = input("Description: ")
    category = input("Category: ")
    trans_type = "INCOME"
    conn.execute("INSERT INTO TRANSACTIONS(amount, description, type, category) VALUES(?, ?, ?, ?)",
                 (amount, description, trans_type, category))
    conn.commit()
    print(f"{amount} added!!")
def add_expense():
    amount = int(input("Amount: "))
    description = input("Description: ")
    category = input("Category: ")
    trans_type = "EXPENSE"
    conn.execute("INSERT INTO TRANSACTIONS(amount, description, type, category) VALUES(?,?,?,?)",
                 (amount, description, trans_type, category))
    conn.commit()
    print(f"{amount} expense added!!")
    
def view_transaction():
    rows = conn.execute("SELECT * FROM TRANSACTIONS").fetchall()
    if not rows:
        print("No Transaction Found")
        return
    for row in rows:
        print(row)
def total_balance():
    income = conn.execute("SELECT SUM(amount) FROM TRANSACTIONS WHERE type = 'INCOME'").fetchone()[0] or 0
    expense = conn.execute("SELECT SUM(amount) FROM TRANSACTIONS WHERE type = 'EXPENSE'").fetchone()[0] or 0

    print(f"Total Balance: {income - expense}")
def category():
    cat = input("category: ")
    rows = conn.execute("SELECT * FROM TRANSACTIONS WHERE category = ?",(cat,)).fetchall()
    if not rows:
        print("no categories found")
        return
    
    for row in rows:
        print(row)   

def main():
    create_table()
    while True:
        print("\n1. Add income")
        print("2.add expense")
        print("3.view transaction")
        print("4.total balance")
        print("5.category")
        print("6.quit")

        choice = input("choose: ")

        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
           view_transaction()
        elif choice == "4":
            total_balance()
        elif choice == "5":
            category()
        elif choice == "6":
            break     

main()