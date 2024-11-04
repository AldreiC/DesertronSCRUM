import platform
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from LoginPage import validate_login, register_user 
import requests
import os
import subprocess
app = Flask(__name__)
app.secret_key = 'your_secret_key'
RPI_IP = "192.168.1.74"
RPI_USER = "pi"  
message = ""
# Logs
login_logs = []
command_logs = []

def control_robot(action):
    """Send control command to the Raspberry Pi's robot control API."""
    try:
        response = requests.post(f"http://{RPI_IP}:5000/control_robot", json={'action': action})
        if response.status_code == 200:
            message = f"Command '{action}' sent successfully"
        else:
            message = f"Error sending command '{action}'"
    except Exception as e:
        message = f"Failed to connect to Raspberry Pi: {e}"
    
    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
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
@app.route('/start-robot', methods=['POST'])
def start_robot():
    Strat = request.json.get('action')
    message = "" 

    if Strat == "start":
        try:
            
            ssh_command = f"ssh {RPI_USER}@{RPI_IP} 'python3 RasperryPiControl.py'"
            result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                message = "Robot started successfully."
            else:
                message = f"Failed to start RasperryPiControl.py, exit code: {result.returncode}"

        except Exception as e:
            message = f"Exception occurred: {str(e)}"
    else:
        message = "Invalid action specified."

    command_logs.append({"command": "start", "timestamp": datetime.now(), "status": message})
    print("started.. hopefully")
    return jsonify({"status": message})

if __name__ == '__main__':
    app.run(debug=True)

