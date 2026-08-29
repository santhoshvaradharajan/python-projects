import csv

expenses = []

def add_expense():
    name = input("Enter the name: ").strip()
    amount = float(input("Enter the amount: "))
    category = input("Enter the category: ").strip()

    expenses.append({'name':name, 'amount':amount, 'category': category})
    print(f"added {name} - £{amount:.2f}!!")

def view_expense():
    if not expenses:
        print("No expenses")
        return
    else:
        print("\n Your expenses:")
        for i, e in enumerate(expenses, 1):
            print(f"{i}.{e['name']} | £{e['amount']:.2f} |{e['category']}")
def total_expense():
    print(f"Toatal: £{sum(e['amount'] for e in expenses):.2f}")

def main():
    while True:
        print("\n1. add expenses")
        print("2. view expenses")
        print("3. total expenses")
        print("4. quit")

        choice = input("choose: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expense()
        elif choice == "3":
            total_expense()
        elif choice == "4":
            print("Good Bye")
            break
main()
