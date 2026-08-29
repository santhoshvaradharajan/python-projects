import csv
contacts = []

def add_contacts():
    name = input("Name: ").strip()
    phone = input("phone: ").strip()
    mail = input("mail: ").strip()

    contacts.append({
        "name":name,
        "phone":phone,
        "mail":mail
    })
    print(f"your contact '{name}' is added!!")

def view_contacts():
    if not contacts:
        print("no contact is available")
    else:
        print("\nYour Contacts:")
        for i, contact in enumerate(contacts, 1):
            print(f"{i}.{contact['name']} | {contact['phone']} | {contact['mail']}")     
def search_contacts():
    if not contacts:
        print("no contacts available")
        return

    search = input("search the name: ").strip().lower()
    found = False
    for contact in contacts:
        if search in contact["name"]:
            print("\n Found")
            print(f"Name: {contact['name']}")
            print(f"phone: {contact['phone']}")
            print(f"mail: {contact['mail']}")
            found = True

    if not found:
        print("No Contact Found")        
def delete_contacts():
    if not contacts:
        print("No contact Found")
        return
    view_contacts()
    try:
       number = int(input("which one needs to be deleted: "))
       if 1<= number <= len(contacts):
           removed = contacts.pop(number -1)
           print(f"'{removed['name']}' deleted!!")
       else:
           print("Invalid Number")
    except ValueError:
        print("give a valid number")       
def load_contacts():
    with open("contacts.csv", "w", newline = "") as file:
        writer = csv.DictWriter(file, fieldnames = ["name", "phone", "mail"])
        writer.writeheader()
        writer.writerows(contacts)
    print("contacts saved")    
def main():
    while True:
        print("\nContact Book")
        print("1. add contacts")
        print("2. view contact")
        print("3. search contact")
        print("4. delete contact")
        print("5. quit")

        choice = int(input("choose: "))

        if choice == 1:
            add_contacts()
        elif choice == 2:
            view_contacts()
        elif choice == 3:
            search_contacts()
        elif choice == 4:
            delete_contacts()
        elif choice == 5:
            print("Good Bye")
            break
        else:   
            print("Invalid choice")

main()            

