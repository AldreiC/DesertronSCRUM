import threading
import time
from tkinter import Tk, Label, Button
from flask import Flask, request, jsonify
import requests

# Flask app initialization
app = Flask(__name__)

# Raspberry Pi URL for motor control
raspberry_pi_url = 'http://192.168.1.74:5001/action'

# Movement control functions
def send_command_to_robot(direction):
    """Send a movement command to the Raspberry Pi controlling the robot."""
    try:
        response = requests.post(raspberry_pi_url, json={'direction': direction})
        if response.status_code == 200:
            print(f"Sent command: {direction}")
        else:
            print(f"Failed to send command: {direction}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# GUI for robot control
class ControlGUI(Tk):
    def FWD(self):
        print("Forward")
        send_command_to_robot('forward')

    def BACKWD(self):
        print("Backward")
        send_command_to_robot('backward')

    def LEFT(self):
        print("Left")
        send_command_to_robot('left')

    def RIGHT(self):
        print("Right")
        send_command_to_robot('right')

    def STOP(self):
        print("Stopping")
        send_command_to_robot('stop')

    def reset_states(self):
        """Reset all movement states (Optional - if needed)."""
        pass

    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Control GUI")

        Label(self, text="Control Panel", font=("Arial", 20)).pack(pady=20)

        # Control buttons with corresponding commands
        Button(self, text="Forward", command=self.FWD).pack(pady=10)
        Button(self, text="Backward", command=self.BACKWD).pack(pady=10)
        Button(self, text="Left", command=self.LEFT).pack(pady=10)
        Button(self, text="Right", command=self.RIGHT).pack(pady=10)
        Button(self, text="Stop", command=self.STOP).pack(pady=10)

# Flask route to handle commands via API
@app.route('/command', methods=['POST'])
def handle_command():
    """Handle incoming commands from the Flask API."""
    data = request.get_json()
    command = data.get('command')

    if command in ['forward', 'backward', 'left', 'right', 'stop']:
        send_command_to_robot(command)
        return jsonify({"status": f"Command '{command}' executed via API"}), 200
    else:
        return jsonify({"error": "Invalid command"}), 400

@app.route('/')
def home():
    return "Flask is running"

# Function to run the Flask server
def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

# Function to start Flask in a separate thread
def start_flask_in_thread():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Daemon thread will exit when the main program exits
    flask_thread.start()

# Main function to start the Flask API and GUI
def main():
    # Start Flask in a separate thread
    print("Starting Flask server in the background...")
    start_flask_in_thread()

    # Wait for Flask to initialize
    time.sleep(2)

    # Open the control GUI
    print("Opening the Control GUI...")
    ControlGUI().mainloop()

if __name__ == "__main__":
    main()
