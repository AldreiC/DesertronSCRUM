# api.py
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Flask route to receive commands externally
@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command')

    # Process the command and forward it to the robot or GUI control
    if command:
        # Forward the command to the GUI app or robot control (in this case, another Flask API endpoint)
        response = requests.post('http://192.168.1.74:5001/command', json={'command': command})
        
        if response.status_code == 200:
            return jsonify({"status": f"Command '{command}' successfully sent to GUI/Robot"}), 200
        else:
            return jsonify({"error": "Failed to send command"}), response.status_code
    else:
        return jsonify({"error": "No command provided"}), 400

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=False, port=5000)
