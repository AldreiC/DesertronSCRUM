# Import necessary modules
import platform
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from datetime import datetime
import requests
import os
import subprocess
import logging
from queue import Queue
from threading import Lock
import json
from LoginPage import validate_login, register_user
from LineProcessing import FINAL_OVERLAY  # Import frame processing from LineProcessing.py
import cv2

# Initialize Flask application and set up security
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')
# Configuration for Raspberry Pi connection
RPI_IP = "192.168.240.22"  # IP address of the Raspberry Pi
RPI_USER = "pi"            # Username for SSH access

# Global variables for application state
message = ""               # Stores latest system message
login_logs = []           # Tracks login attempts
command_logs = []         # Tracks commands sent to robot
StartStatus = False       # Tracks if robot is running
event_queue = Queue()     # Queue for event handling
clients = set()           # Set of connected clients
clients_lock = Lock()     # Thread safety for client operations

# Set up logging configuration
LOG_FILE_PATH = "app.log"
LOGIN_LOG_FILE_PATH = "login.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

def broadcast_event(event_type, data):
    """
    Broadcasts events to all connected clients
    Args:
        event_type: Type of event (e.g., 'login_log', 'command_log')
        data: Event data to broadcast
    """
    event = {'type': event_type, 'data': data}
    with clients_lock:
        for client_queue in clients:
            client_queue.put(event)

def log_login(username):
    """
    Logs user login attempts and broadcasts to connected clients
    Args:
        username: Username of the logging in user
    """
    login_message = f"{username} logged in at {datetime.now()}"
    with open(LOGIN_LOG_FILE_PATH, 'a') as f:
        f.write(login_message + "\n")
    logging.info(login_message)
    broadcast_event('login_log', login_message)

def check_services():
    """
    Checks if required Python scripts are running on Raspberry Pi
    Returns:
        bool: True if services are running, False otherwise
    """
    try:
        cmd = f"ssh {RPI_USER}@{RPI_IP} 'pgrep -f \"python3 (RPIcameraStream|rasperryPiControl).py\"'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def control_robot(action):
    """
    Sends control commands to the robot via HTTP
    Args:
        action: Command to send to robot (e.g., 'forward', 'backward')
    Returns:
        str: Status message indicating success or failure
    """
    global message
    try:
        response = requests.post(f"http://{RPI_IP}:5000/control_robot", json={'action': action})
        if response.status_code == 200:
            message = f"Command '{action}' sent successfully"
        else:
            message = f"Error sending command '{action}'"
    except Exception as e:
        message = f"Failed to connect to Raspberry Pi: {e}"
    
    # Log the command and broadcast to clients
    log_entry = {
        "command": action,
        "timestamp": str(datetime.now()),
        "status": message
    }
    command_logs.append(log_entry)
    logging.info(message)
    broadcast_event('command_log', log_entry)
    return message

# Route handlers
@app.route('/')
def login():
    """Renders the login page"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    """
    Handles user login authentication
    Returns:
        redirect: Redirects to dashboard on success
        str: Error message on failure
    """
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):
        session['username'] = username
        log_login(username)
        return redirect(url_for('dashboard'))
    return 'Invalid credentials', 401

@app.route('/register', methods=['POST'])
def register_user_route():
    """
    Handles new user registration
    Returns:
        redirect: Redirects to login on success
        str: Error message on failure
    """
    username = request.form['username']
    password = request.form['password']
    if register_user(username, password):
        return redirect(url_for('login'))
    return 'Registration failed. Username may already exist.', 400

@app.route('/dashboard')
def dashboard():
    """
    Renders main dashboard if user is authenticated
    Returns:
        template: Dashboard template
        redirect: Login page if not authenticated
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Video feed routes
@app.route('/video_feed/raw')
def raw_video_feed():
    """
    Redirects to raw video stream from Raspberry Pi
    Returns:
        redirect: Raw video stream URL
        str: Error message if stream unavailable
    """
    try:
        return redirect(f"http://{RPI_IP}:5001/video_feed/raw")
    except Exception as e:
        logging.error(f"Failed to connect to raw video stream: {str(e)}")
        return "Raw video stream unavailable", 503

@app.route("/video_feed/overlay")
def overlayvideofeed():
    """
    Redirects to processed video stream with overlay
    Returns:
        redirect: Overlay video stream URL
        str: Error message if stream unavailable
    """
    try:
        return redirect(f"http://{RPI_IP}:5001/video_feed/overlay")
    except Exception as e:
        logging.error(f"Failed to connect to overlay stream: {str(e)}")
        return "Overlaid video stream unavailable", 503 

@app.route('/events')
def events():
    """
    Server-Sent Events (SSE) endpoint for real-time updates
    Returns:
        Response: Event stream for client updates
    """
    def generate():
        client_queue = Queue()
        with clients_lock:
            clients.add(client_queue)
        try:
            while True:
                message = client_queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        finally:
            with clients_lock:
                clients.remove(client_queue)
    
    return Response(generate(), mimetype='text/event-stream')

# Log retrieval routes
@app.route('/get-login-logs')
def get_login_logs():
    """Returns all login logs"""
    if os.path.exists(LOGIN_LOG_FILE_PATH):
        with open(LOGIN_LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()
    else:
        logs = ["Login log file not found."]
    return jsonify(logs=logs)

@app.route('/get-logs')
def get_logs():
    """Returns all system logs"""
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()
    else:
        logs = ["Log file not found."]
    return jsonify(logs=logs)

@app.route('/send-command', methods=['POST'])
def send_command():
    """
    Handles robot control command requests
    Returns:
        json: Command status message
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    command = request.json.get('command')
    response_message = control_robot(command)
    
    return jsonify({"status": response_message})

@app.route('/start-robot', methods=['POST'])
def start_robot():
    """
    Starts or stops the robot and associated services
    Returns:
        json: Status message indicating success or failure
    """
    global StartStatus
    action = request.json.get('action')
    message = ""

    if action == "start":
        if not StartStatus:
            try:
                # Commands to start robot services
                ssh_commands = [
                    f"ssh{RPI_USER}@{RPI_IP} sudo pkill motion"
                    f"ssh {RPI_USER}@{RPI_IP} 'python3 RasperryPiControl.py &'",
                    f"ssh {RPI_USER}@{RPI_IP} 'python3 LineProcessingRPI.py &'"
                ]
                
                for cmd in ssh_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        raise Exception(f"Command failed: {result.stderr}")
                
                StartStatus = True
                message = "Robot, camera stream, and video overlay started successfully."
            except Exception as e:
                message = f"Error starting scripts: {str(e)}"
        else:
            message = "Robot is already running."
    elif action == "stop":
        if StartStatus:
            try:
                # Commands to stop robot services
                ssh_commands = [
                    f"ssh {RPI_USER}@{RPI_IP} 'pkill -f RasperryPiControl.py'",
                    f"ssh {RPI_USER}@{RPI_IP} 'pkill -f LineProcessingRPI.py'"
                ]
                
                for cmd in ssh_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        raise Exception(f"Command failed: {result.stderr}")
                
                StartStatus = False
                message = "Robot, camera stream, and video overlay stopped successfully."
            except Exception as e:
                message = f"Error stopping scripts: {str(e)}"
        else:
            message = "Robot is not currently running."
    
    # Log and broadcast the action
    log_entry = {
        "command": action,
        "timestamp": str(datetime.now()),
        "status": message
    } 
    command_logs.append(log_entry)
    logging.info(f"Command executed: {message}")
    broadcast_event('command_log', log_entry)
    return jsonify({"status": message})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5001)