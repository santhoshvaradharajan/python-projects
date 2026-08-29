order = []
order_id = 1

def add_order():
    global order_id
    item = input("item: ").strip()
    quantity = int(input("quantity: "))
    order.append({
        "id": order_id,
        "item": item,
        "quantity": quantity,
        "status": "pending"
    })
    order_id += 1
    print("order added!!")
def view_order():
    pending = [o for o in order if o["status"] == "pending"]
    if not pending:
        print("No orders pending")
        return
    for o in pending:
        print(f"{o['id']}.{o['item']} X {o['quantity']} {o['status']}")

def complete_order():
    view_order()
    oid = int(input("order id to completed: "))
    for o in order:
        if o["id"] == oid:
            o["status"] = "completed"
            print("order completed")
def main():
    while True:
        print("\n1.Add order")
        print("2.View order")
        print("3.Complete order")
        print("4.quit")

        choice = input("choose: ")

        if choice == "1":
            add_order()
        elif choice == "2":
            view_order()
        elif choice == "3":
            complete_order()
        else:
            break
main()                    
