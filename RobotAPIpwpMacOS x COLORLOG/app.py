import platform
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from LoginPage import validate_login, register_user
import requests
import os
import subprocess
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')
RPI_IP = "192.168.1.74"
RPI_USER = "pi"
message = ""
login_logs = []
command_logs = []
StartStatus = False  

# Set up logging to both file and console
LOG_FILE_PATH = "app.log"
LOGIN_LOG_FILE_PATH = "login.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE_PATH), logging.StreamHandler()])

def log_login(username):
    """Log login attempt to login.log file."""
    login_message = f"{username} logged in at {datetime.now()}"
    with open(LOGIN_LOG_FILE_PATH, 'a') as f:
        f.write(login_message + "\n")
    logging.info(login_message)

def shutdown():
    """Gracefully shut down the Flask application."""
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Shutting down...'
    except Exception as e:
        return f'Error: {str(e)}'

def control_robot(action):
    """Send control command to the Raspberry Pi's robot control API."""
    global message
    try:
        response = requests.post(f"http://{RPI_IP}:5000/control_robot", json={'action': action})
        if response.status_code == 200:
            message = f"Command '{action}' sent successfully"
        else:
            message = f"Error sending command '{action}'"
    except Exception as e:
        message = f"Failed to connect to Raspberry Pi: {e}"
    
    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
    logging.info(message)
    return message

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password):
        session['username'] = username
        login_logs.append(f"{username} logged in at {datetime.now()}")
        log_login(username)  # Log to login.log file
        return redirect(url_for('dashboard'))
    return 'Invalid credentials', 401

@app.route('/register', methods=['POST'])
def register_user_route():
    username = request.form['username']
    password = request.form['password']
    if register_user(username, password):
        return redirect(url_for('login'))
    return 'Registration failed. Username may already exist.', 400

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], logs=login_logs, command_logs=command_logs)

@app.route('/get-login-logs')
def get_login_logs():
    # Read login logs from login.log file
    if os.path.exists(LOGIN_LOG_FILE_PATH):
        with open(LOGIN_LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()
    else:
        logs = ["Login log file not found."]
    return jsonify(logs=logs)

@app.route('/get-logs')
def get_logs():
    # Read logs from the log file
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()
    else:
        logs = ["Log file not found."]
    return jsonify(logs=logs)

@app.route('/send-command', methods=['POST'])
def send_command():
    if 'username' not in session:
        return redirect(url_for('login'))

    command = request.json.get('command')
    response_message = control_robot(command)
    
    log_entry = f"{session['username']} sent command '{command}' at {datetime.now()}"
    login_logs.append(log_entry)
    
    return jsonify({"status": response_message})

@app.route('/start-robot', methods=['POST'])
def start_robot():
    global StartStatus
    action = request.json.get('action')
    message = ""

    if action == "start":
        if StartStatus != "Hello":  
            try:
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
        if StartStatus != "Hello":  
            try:
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

    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
    logging.info(f"Command executed: {message}")
    return jsonify({"status": message})

if __name__ == '__main__':
    app.run(debug=True)
