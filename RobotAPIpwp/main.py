import subprocess
import time

def run_flask_controller():
    # Runs the Flask-based controller (controller.py)
    subprocess.Popen(['python', 'APIcodePWP.py'], shell=False)

def run_login_gui():
    # Runs the Tkinter-based login program (LoginPage.py)
    subprocess.Popen(['python', 'LoginPage.py'], shell=False)

def main():
    # Start Flask controller
    print("Starting the Flask controller...")
    run_flask_controller()
    
    # Give the Flask server a second to start
    time.sleep(2)
    
    # Start the login GUI
    print("Starting the Login GUI...")
    run_login_gui()

    print("Both the Flask controller and Login GUI are running.")

if __name__ == "__main__":
    main()
