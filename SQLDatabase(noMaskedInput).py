import sqlite3
import getpass  

def create_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def display_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    if rows:
        print("\nCurrent users in the database:")
        for row in rows:
            print(row)
    else:
        print("\nThe users table is empty.")
    conn.close()

def wipe_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    
    cursor.execute('DELETE FROM users')

    cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')

    conn.commit()

    print("All records in the users table have been wiped and userId reset to 1.")
    conn.close()

def register():
    username = input("Enter a new username: ").strip()
    #password = getpass.getpass("Enter your password: ").strip()
    password = getpass.getpass("Enter a new password: ").strip()

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Error: Username already exists. Please choose a different one.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def login():
    username = input("Enter your username: ").strip()
    #password = getpass.getpass("Enter your password: ").strip()
    password = getpass.getpass("Enter your password: ").strip()

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    result = cursor.fetchone()

    if result:
        print("Login successful!")
    else:
        print("Error: Invalid username or password.")

    conn.close()

def main():
    create_table()
    while True:
        print("\nSelect an option:")
        print("1. Register")
        print("2. Login")
        print("3. Wipe Table (For Testing)")
        print("4. Display Table (For Testing)")
        print("5. Exit")

        choice = input("Enter choice (1, 2, 3, 4, 5): ").strip()

        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            wipe_table()
        elif choice == '4':
            display_table()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
