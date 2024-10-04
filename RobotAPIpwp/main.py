import threading
import time
from tkinter import Tk, Label, Button
from flask import Flask
from LoginPage import main as user_main
import requests

app = Flask(__name__)

@app.route('/command', methods = ["POST"])
def command():
    return "command recived"
def home():
    return "Flask is running"


def run_flask():
    """Function to run the Flask app."""
    app.run(port=5000, debug=False, use_reloader=False)


def start_flask_in_thread():
    """Start Flask in a separate thread."""
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Daemon thread will exit when the main program exits
    flask_thread.start()


class ControlGUI(Tk):
    def FWD(self):
        global fwd_state
        fwd_state = 1
        print("Forward")
        command = 0b0001
        return fwd_state

    def BACKWD(self):
        global backwd_state
        backwd_state = 1
        print("Backward")
        command = 0b0010
        return backwd_state

    def LEFT(self):
        global left_state
        left_state = 1
        print("Left")
        command = 0b0100
        return left_state

    def RIGHT(self):
        global right_state
        right_state = 1
        print("Right")
        command = 0b1000
        return right_state

    def STOP(self):
        global stop_state
        stop_state = 1
        command = 0b0000
        print("Stopping")
        return stop_state

    def reset_states(self):
        global fwd_state, backwd_state, left_state, right_state, stop_state
        fwd_state = backwd_state = left_state = right_state = stop_state = 0
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Control GUI")

        Label(self, text="Control Panel", font=("Arial", 20)).pack(pady=20)

        # Control buttons with corresponding commands that send binary values and print actions
        Button(self, text="Forward", command=lambda: [self.reset_states(), self.FWD()]).pack(pady=10)
        Button(self, text="Backward", command=lambda: [self.reset_states(), self.BACKWD()]).pack(pady=10)
        Button(self, text="Left", command=lambda: [self.reset_states(), self.LEFT()]).pack(pady=10)
        Button(self, text="Right", command=lambda: [self.reset_states(), self.RIGHT()]).pack(pady=10)
        Button(self, text="Stop", command=lambda: [self.reset_states(), self.STOP()]).pack(pady=10)

        self.mainloop()  # Start the main loop for the control GUI

    def send_command(self, binary_value, action):
        """Send binary command to the motors and print action."""
        # Print what button was pressed
        print(f"{action} button pressed.")
        
        # Print the binary command
        print(f"Sending command: {bin(binary_value)}")

    
    





def main():
    # Start Flask in a separate thread
    print("Starting Flask server in the background...")
    start_flask_in_thread()

    # Wait for Flask to initialize
    time.sleep(2)

    # Start the main function from the user's script (which shows Login/Register options)
    print("Running the main function from the user's script...")
    user_main()

    # After user_main runs, check for successful login via the login_code function
    
    # If successful login occurred, open the control GUI
    print("Checking if login was successful...")
    

    
    successful_login = user_main
    print(successful_login)
    if successful_login:
        print("Login successful! Opening the control GUI...")
        ControlGUI()

    else:
        print("Login failed or cancelled.")


if __name__ == "__main__":
    main()

    
