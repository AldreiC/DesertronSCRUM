import sqlite3
import getpass
from tkinter import *
from tkinter import messagebox
from tkinter import ttk


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
    message = "The users table is empty."

    if rows:
        message = "Current users in the database:"
        for row in rows:
            message += row

    messagebox.showinfo("Display Table", message)

    conn.close()


def wipe_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')
    conn.commit()

    messagebox.showinfo("Wipe Table", "All records in the users table have been wiped and userId reset to 1.")

    conn.close()


def register():
    reg = Tk()
    reg.geometry("600x400")
    reg.title("Register")
    username = input("Enter a new username: ").strip()
    # password = getpass.getpass("Enter your password: ").strip()
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
    # password = getpass.getpass("Enter your password: ").strip()
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

    root = Tk()
    root.geometry("800x1000")
    root.title("DesertronSCRUMSite")

    t_frame = Frame(root)
    t_frame.place(relx=0, rely=0, relheight=0.4, relwidth=1)
    m_frame = Frame(root)
    m_frame.place(relx=0, rely=0.4, relheight=0.4, relwidth=1)
    b_frame = Frame(root)
    b_frame.place(relx=0, rely=0.8, relheight=0.2, relwidth=1)

    ttl_lbl = Label(t_frame, text="DESERTRON LOGIN PAGE", font=("Papyrus", 50))
    ttl_lbl.place(relx=0.5, rely=0.5, anchor="center", relheight=1, relwidth=1)

    reg_btn = Button(m_frame, text="Register", font=("Papyrus", 40), command=register)
    reg_btn.place(relx=0.25, rely=0.5, anchor="center", relheight=0.4, relwidth=0.4)
    log_btn = Button(m_frame, text="Login", font=("Papyrus", 40), command=login)
    log_btn.place(relx=0.75, rely=0.5, anchor="center", relheight=0.4, relwidth=0.4)
    ext_btn = Button(b_frame, text="Exit", font=("Papyrus", 25), command=root.destroy)
    ext_btn.place(relx=0.5, rely=0.5, anchor="center", relheight=0.5, relwidth=0.2)


    root.mainloop()


if __name__ == "__main__":
    main()
