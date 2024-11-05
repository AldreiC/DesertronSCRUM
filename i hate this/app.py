import subprocess
from flask import jsonify, request
from datetime import datetime

StartStatus = False  # Assuming global variable is defined somewhere
command_logs = []  # Assuming command_logs is defined somewhere

def start_robot():
    global StartStatus
    action = request.json.get('action')
    message = ""

    if action == "start":
        if not StartStatus:  # Only start if not already running
            try:
                # Use tmux to start a detached session running the Python script
                ssh_command = f"ssh {RPI_USER}@{RPI_IP} 'tmux new -d -s robot_session \"python3 /path/to/RasperryPiControl.py\"'"
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
        if StartStatus:  # Only stop if it is running
            try:
                # Use tmux to kill the session by name
                ssh_command = f"ssh {RPI_USER}@{RPI_IP} 'tmux kill-session -t robot_session'"
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

    else:
        message = "Invalid action. Use 'start' or 'exit'."

    command_logs.append({"command": action, "timestamp": datetime.now(), "status": message})
    print("Command executed:", message)
    return jsonify({"status": message})
