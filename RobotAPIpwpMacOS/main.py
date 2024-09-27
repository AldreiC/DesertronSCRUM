import threading
import time
from tkinter import Tk, Label, Button
from flask import Flask
from LoginPage import main as user_main, login_code  # Import main function and login_code from your script

# Flask app setup (example route)
app = Flask(__name__)

@app.route('/')
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
    """Tkinter-based control GUI."""
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Control GUI")

        Label(self, text="Control Panel", font=("Arial", 20)).pack(pady=20)

        # Control buttons with corresponding commands that send binary values and print actions
        Button(self, text="Forward", command=lambda: self.send_command(0b0001, "Forward")).pack(pady=10)
        Button(self, text="Backward", command=lambda: self.send_command(0b0010, "Backward")).pack(pady=10)
        Button(self, text="Left", command=lambda: self.send_command(0b0100, "Left")).pack(pady=10)
        Button(self, text="Right", command=lambda: self.send_command(0b1000, "Right")).pack(pady=10)
        Button(self, text="Stop", command=lambda: self.send_command(0b0000, "Stop")).pack(pady=10)

        self.mainloop()  # Start the main loop for the control GUI

    def send_command(self, binary_value, action):
        """Send binary command to the motors and print action."""
        # Print what button was pressed
        print(f"{action} button pressed.")
        
        # Print the binary command
        print(f"Sending command: {bin(binary_value)}")

        # Here, you can add code to actually send this command to your motor controller
        # e.g., via serial communication or GPIO pins on a Raspberry Pi





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
    # Assuming login_code has been invoked inside your script's login() function
    # If successful login occurred, open the control GUI
    print("Checking if login was successful...")
    
    # Simulating a login check logic (replace with actual tracking)
    successful_login = login_code

    if successful_login:
        print("Login successful! Opening the control GUI...")
        ControlGUI()
    else:
        print("Login failed or cancelled.")


if __name__ == "__main__":
    main()
