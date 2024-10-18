import datetime
import sqlite3
import requests
from tkinter import *
from tkinter import messagebox

successfulLogin = None
def create_table():
    conn = sqlite3.connect('PWP_database.db')
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
    conn = sqlite3.connect('PWP_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    if rows:
        print("\nCurrent users in the database:")
        for row in rows:
            print(row)
    else:
        print("The users table is empty.")

    conn.close()


def wipe_table():
    conn = sqlite3.connect('PWP_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')
    conn.commit()

    print("All records in the users table have been wiped and userId reset to 1.")

    conn.close()


def register():
    reg = Tk()
    reg.geometry("600x600")
    reg.resizable(False, False)
    reg.title("Register")

    treg_frame = Frame(reg)
    treg_frame.place(relx=0, rely=0, relheight=0.3, relwidth=1)
    mreg_frame = Frame(reg)
    mreg_frame.place(relx=0, rely=0.3, relheight=0.4, relwidth=1)
    breg_frame = Frame(reg)
    breg_frame.place(relx=0, rely=0.7, relheight=0.3, relwidth=1)

    usr_en_var = StringVar()
    pwd_en_var = StringVar()

    ttl_lbl = Label(treg_frame, text="Register", font=("Papyrus", 50))
    ttl_lbl.place(relx=0.5, rely=0.5, anchor="center", relheight=1, relwidth=1)
    usr_lbl = Label(mreg_frame, text="Username:", font=("Papyrus", 20))
    usr_lbl.place(relx=0.25, rely=0.1, anchor="center", relheight=0.2, relwidth=0.2)
    pwp_lbl = Label(mreg_frame, text="Password:", font=("Papyrus", 20))
    pwp_lbl.place(relx=0.25, rely=0.4, anchor="center", relheight=0.2, relwidth=0.3)

    usr_en = Entry(mreg_frame, textvariable=usr_en_var)
    usr_en.place(relx=0.65, rely=0.1, anchor="center", relheight=0.2, relwidth=0.5)
    pwd_en = Entry(mreg_frame, textvariable=pwd_en_var, show="*")  # Masked password entry
    pwd_en.place(relx=0.65, rely=0.4, anchor="center", relheight=0.2, relwidth=0.5)

    sub_btn = Button(mreg_frame, text="Register", command=lambda: register_code(usr_en, pwd_en, reg))
    sub_btn.place(relx=0.5, rely=0.8, anchor="center", relheight=0.2, relwidth=0.3)
    ext_btn = Button(breg_frame, text="Exit", command=reg.destroy)
    ext_btn.place(relx=0.5, rely=0.5, anchor="center", relheight=0.2, relwidth=0.3)

    reg.mainloop()


def register_code(usr, pwd, reg_window):
    username = usr.get().strip()
    password = pwd.get().strip()
    message = ["", ""]

    if not username or not password:
        messagebox.showinfo("Error", "Username and Password cannot be empty.")
        return

    conn = sqlite3.connect('PWP_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        message = ["Success", "User registered successfully!"]
        reg_window.destroy()  
    except sqlite3.IntegrityError:
        message = ["Error", "Error: Username already exists. Please choose a different one."]
    except Exception as e:
        message = ["Error", f"An error occurred: {e}"]
    finally:
        conn.close()
    
    messagebox.showinfo(message[0], message[1])


def login():
    log = Tk()
    log.geometry("600x600")
    log.resizable(False, False)
    log.title("Login")

    logframe1 = Frame(log)
    logframe1.place(relx=0, rely=0, relheight=0.3, relwidth=1)
    logframe2 = Frame(log)
    logframe2.place(relx=0, rely=0.3, relheight=0.4, relwidth=1)
    logframe3 = Frame(log)
    logframe3.place(relx=0, rely=0.7, relheight=0.3, relwidth=1)

    username_var = StringVar()
    password_var = StringVar()

    loglabel1 = Label(logframe1, text="Login", font=("Papyrus", 50))
    loglabel1.place(relx=0.5, rely=0.5, anchor="center", relheight=1, relwidth=1)
    username_label = Label(logframe2, text="Username:", font=("Papyrus", 20))
    username_label.place(relx=0.25, rely=0.1, anchor="center", relheight=0.2, relwidth=0.2)
    password_label = Label(logframe2, text="Password:", font=("Papyrus", 20))
    password_label.place(relx=0.25, rely=0.4, anchor="center", relheight=0.2, relwidth=0.3)

    username_entry = Entry(logframe2, textvariable=username_var)
    username_entry.place(relx=0.65, rely=0.1, anchor="center", relheight=0.2, relwidth=0.5)
    password_entry = Entry(logframe2, textvariable=password_var, show="*")  # Masked password entry
    password_entry.place(relx=0.65, rely=0.4, anchor="center", relheight=0.2, relwidth=0.5)

    logbutton = Button(logframe2, text="Log in", command=lambda: login_code(username_entry, password_entry, log))
    logbutton.place(relx=0.5, rely=0.8, anchor="center", relheight=0.2, relwidth=0.3)
    exitbutton = Button(logframe3, text="Exit", command=log.destroy)
    exitbutton.place(relx=0.5, rely=0.5, anchor="center", relheight=0.2, relwidth=0.3)

    log.mainloop()


def login_code(user, passw, log_window):
    successfulLogin = False  # Default to failure
    username2 = user.get().strip()
    password2 = passw.get().strip()

    conn = sqlite3.connect('PWP_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username2, password2))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Success", "Logged in successfully!")
        print(username2 + " has logged in at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".")
        log_window.destroy()
        successfulLogin = True  # Set success flag

        try:
            response = requests.post('http://127.0.0.1:5000/command')
            if response.status_code == 200:
                print("Controller launched successfully.")
            else:
                print("Failed to launch controller:", response.status_code)
        except Exception as e:
            print("Error connecting to the controller:", e)
    else:
        retry = messagebox.askretrycancel("Failure", "Username or password incorrect. Try again or register a new account.")
        log_window.destroy()

        if retry:
            login()  # Restart the login process
        else:
            register()  # Open registration
        
    conn.close()
    return successfulLogin  # Return success status
def destroy(root):
    global successfulLogin
    successfulLogin = False
    root.destroy()

def main():
    global successfulLogin
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
    ext_btn = Button(b_frame, text="Exit", font=("Papyrus", 25), command=lambda: destroy(root))
    ext_btn.place(relx=0.5, rely=0.5, anchor="center", relheight=0.5, relwidth=0.2)
    
    root.mainloop()
    return successfulLogin

if __name__ == "__main__":
    #wipe_table()
    main()
    #display_table()