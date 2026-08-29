import sqlite3

conn = sqlite3.connect("student.db")

def create_Table():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS STUDENTS(
    id INTEGER PRIMARY KEY,
    NAME TEXT NOT NULL,
    GRADE INTEGER NOT NULL,
    SUBJECT TEXT NOT NULL
   )
""")
    conn.commit()
def add_student():
    name = input("name: ")
    subject = input("subject: ")
    grade = int(input("grade: "))
    conn.execute("INSERT INTO STUDENTS (name, subject, grade) VALUES (?, ?, ?)",
                 (name, subject, grade))
    conn.commit()
    print(f"{name} added!")
def view_student():
    rows = conn.execute("SELECT * FROM STUDENTS").fetchall()
    if not rows:
        print("No Students!!")
        return
    for row in rows:
       print(f"{row[0]}. {row[1]} | {row[2]} | {row[3]}")

def average_grade():
    result = conn.execute("SELECT subject, AVG(grade) FROM STUDENTS GROUP BY subject")
    for row in result:
        print(f"{row[0]} -> Average: {row[1]:.1f}")                    

def main():
    create_Table()
    while True:
        print("\n1. Add student")
        print("2. view student")
        print("3. Average by subject")
        print("4. quit")

        choice  = input("choose: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            view_student()
        elif choice == "3":
            average_grade()
        elif choice == "4":
            break

main()
conn.close()
