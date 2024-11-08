# Import necessary modules
import platform
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from LoginPage import validate_login, register_user  # Import login and registration functions
import requests
import os
import subprocess
import logging

# Initialize the Flask application
app = Flask(__name__)
RPI_IP = "192.168.1.74"  # IP address of the Raspberry Pi
RPI_USER = "pi"  # Username for Raspberry Pi SSH access
message = ""  # Message to store status feedback for commands
login_logs = []  # List to keep track of login logs
command_logs = []  # List to store command history logs
StartStatus = False  # Flag to indicate if the robot is started

# Set up logging to both a file and the console
LOG_FILE_PATH = "app.log"  # Path for main log file
LOGIN_LOG_FILE_PATH = "login.log"  # Path for login log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE_PATH), logging.StreamHandler()]  # Log to file and console
)
# This Logs who has logged in
def log_login(username):
    """Log login attempt to login.log file."""
    login_message = f"{username} logged in at {datetime.now()}"  # Format log message
    with open(LOGIN_LOG_FILE_PATH, 'a') as f:  # Append log to login file
        f.write(login_message + "\n")
    logging.info(login_message)  # Log to console and main log file

def shutdown():
    # Shut down the Flask application
    try:
        func = request.environ.get('werkzeug.server.shutdown')  # Get server shutdown function
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()  # Call shutdown function
        return 'Shutting down...'
    except Exception as e:
        return f'Error: {str(e)}'  # Return error message if shutdown fails

def control_robot(action):
    # Send control command to the Raspberry Pi's robot control API
    global message
    try:
        # Send a POST request to Raspberry Pi API with the action
        response = requests.post(f"http://{RPI_IP}:5000/control_robot", json={'action': action})
        if response.status_code == 200:
            message = f"Command '{action}' sent successfully"
        else:
            message = f"Error sending command '{action}'"
    except Exception as e:
        message = f"Failed to connect to Raspberry Pi: {e}"
    
    # Append command details to command log and log to console
    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
    logging.info(message)
    return message

@app.route('/')
# Load Login Page GUI
def login():
    """Render the login page."""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
#Login Functionality
def login_user():
    """Authenticate user login and redirect to dashboard if successful."""
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):  # Validate user credentials
        session['username'] = username  # Store username in session
        login_logs.append(f"{username} logged in at {datetime.now()}")
        log_login(username)  # Log the login event
        return redirect(url_for('dashboard'))  # Redirect to dashboard if login succeeds
    return 'Invalid credentials', 401  # Return error for invalid login

@app.route('/register', methods=['POST'])
#Register Functionality
def register_user_route():
    """Handle user registration and redirect to login page upon success."""
    username = request.form['username']
    password = request.form['password']
    if register_user(username, password):  # Register the user
        return redirect(url_for('login'))  # Redirect to login page on success
    return 'Registration failed. Username may already exist.', 400  # Return error on failure

@app.route('/dashboard')
#Main Page with the remote control and logs
def dashboard():
    """Render the dashboard page with login and command logs."""
    if 'username' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login if not
    # Pass username and logs to the dashboard template
    return render_template('dashboard.html', username=session['username'], logs=login_logs, command_logs=command_logs)

@app.route('/get-login-logs')
def get_login_logs():
    """Return login logs from login.log file as JSON."""
    if os.path.exists(LOGIN_LOG_FILE_PATH):  # Check if log file exists
        with open(LOGIN_LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()  # Read logs from file
    else:
        logs = ["Login log file not found."]  # Return message if file not found
    return jsonify(logs=logs)  # Return logs as JSON

@app.route('/get-logs')
def get_logs():
    """Return general logs from app.log file as JSON."""
    if os.path.exists(LOG_FILE_PATH):  # Check if log file exists
        with open(LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()  # Read logs from file
    else:
        logs = ["Log file not found."]  # Return message if file not found
    return jsonify(logs=logs)  # Return logs as JSON

@app.route('/send-command', methods=['POST'])
def send_command():
    # Send a control command to the robot and log the action
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if user not logged in

    command = request.json.get('command')  # Extract command from JSON
    response_message = control_robot(command)  # Send command to robot
    
    log_entry = f"{session['username']} sent command '{command}' at {datetime.now()}"
    login_logs.append(log_entry)  # Log command entry
    
    return jsonify({"status": response_message})  # Return command status as JSON

@app.route('/start-robot', methods=['POST'])
#This will start the robot and stop it
def start_robot():
    """Start or stop the robot based on the action provided."""
    global StartStatus
    action = request.json.get('action')
    message = ""

    if action == "start":
        if StartStatus != "Hello":  # Check if robot is already running
            try:
                # Execute SSH command to start Raspberry Pi control script
                ssh_command = f"ssh -o StrictHostKeyChecking=no {RPI_USER}@{RPI_IP} 'python3 RasperryPiControl.py &'"
                result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    StartStatus = True
                    message = "Robot started successfully."
                else:
                    message = f"Failed to start RasperryPiControl.py, exit code: {result.returncode}"
            except Exception as e:
                message = f"Exception occurred: {str(e)}"
        else:
            message = "Robot is already running."

    elif action == "exit":
        if StartStatus != "Hello":  # Check if robot is running
            try:
                # Execute SSH command to stop Raspberry Pi control script
                ssh_command = f"ssh {RPI_USER}@{RPI_IP} 'pkill -f RasperryPiControl.py'"
                result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    StartStatus = False
                    message = "Robot stopped successfully."
                else:
                    message = f"Failed to stop RasperryPiControl.py, exit code: {result.returncode}"
            except Exception as e:
                message = f"Exception occurred: {str(e)}"
        else:
            message = "The robot is not currently running."

    # Log command status and return response
    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
    logging.info(f"Command executed: {message}")
    return jsonify({"status": message})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for detailed error messages
