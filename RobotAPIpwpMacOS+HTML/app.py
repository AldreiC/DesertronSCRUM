from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from LoginPage import validate_login  # Assuming 'validate_login' exists
from RaspberryPiControl import control_robot  # Import robot control function

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Logs
login_logs = []

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

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], logs=login_logs)

@app.route('/send-command', methods=['POST'])
def send_command():
    if 'username' not in session:
        return redirect(url_for('login'))

    command = request.json.get('command')
    username = session['username']

    # Directly call the command function from RaspberryPiControl.py
    response_message = control_robot(command)  # Assuming control_robot is set up to handle string commands

    # Log the command
    log_entry = f"{username} sent command '{command}' at {datetime.now()}"
    login_logs.append(log_entry)

    return jsonify({"status": response_message})

if __name__ == '__main__':
    app.run(debug=True)
