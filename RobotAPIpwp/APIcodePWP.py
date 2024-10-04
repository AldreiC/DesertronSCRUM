# api.py

from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# API to control the GUI states
@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command')

    # Send command to the GUI via HTTP POST request to the app
    response = requests.post('http://127.0.0.1:5001/command', json={'command': command})
    return jsonify(), 200
    #return jsonify({"status": f"Command '{command}' sent to GUI", "response": response.json()}), 200

if __name__ == '__main__':
    app.run(debug=False, port=5000)
