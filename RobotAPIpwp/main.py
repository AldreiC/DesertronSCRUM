import threading
import time
from tkinter import Tk, Label, Button
from flask import Flask
from LoginPage import main as user_main
import requests
from GUIforAPI import ControlGUI

app = Flask(__name__)

@app.route('/command', methods = ["POST"])
def command():
    return "command recived"
def home():
    return "Flask is running"


def run_flask():
    """Function to run the Flask app."""
    app.run(host ="0.0.0.0",port=5000, debug=False, use_reloader=False)


def start_flask_in_thread():
    """Start Flask in a separate thread."""
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Daemon thread will exit when the main program exits
    flask_thread.start()


# class ControlGUI(Tk):
#     def FWD(self):
        
       
#         print("Forward")
#         command = 0b0001
#         return command

#     def BACKWD(self):
        
        
#         print("Backward")
#         command = 0b0010
#         return command

#     def LEFT(self):
        
        
#         print("Left")
#         command = 0b0100
#         return command

#     def RIGHT(self):
        
        
#         print("Right")
#         command = 0b1000
#         return command

#     def STOP(self):
        
        
#         command = 0b0000
#         print("Stopping")
#         return command

#     def reset_states(self):
#         global command
#         command = 0b000
#     def __init__(self):
#         super().__init__()
#         self.geometry("400x400")
#         self.title("Control GUI")

#         Label(self, text="Control Panel", font=("Arial", 20)).pack(pady=20)

#         # Control buttons with corresponding commands that send binary values and print actions
#         Button(self, text="Forward", command=lambda: [self.reset_states(), self.FWD()]).pack(pady=10)
#         Button(self, text="Backward", command=lambda: [self.reset_states(), self.BACKWD()]).pack(pady=10)
#         Button(self, text="Left", command=lambda: [self.reset_states(), self.LEFT()]).pack(pady=10)
#         Button(self, text="Right", command=lambda: [self.reset_states(), self.RIGHT()]).pack(pady=10)
#         Button(self, text="Stop", command=lambda: [self.reset_states(), self.STOP()]).pack(pady=10)

#         self.mainloop()  # Start the main loop for the control GUI

#     def send_command(self, binary_value, action):
#         """Send binary command to the motors and print action."""
#         # Print what button was pressed
#         print(f"{action} button pressed.")
        
#         # Print the binary command
#         print(f"Sending command: {bin(binary_value)}")

    
    





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

    
