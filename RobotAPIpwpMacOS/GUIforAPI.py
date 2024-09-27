
from flask import Flask, request, jsonify
from tkinter import *
import threading

app = Flask(__name__)

fwd_state = 0
backwd_state = 0
left_state = 0
right_state = 0
stop_state = 0


def FWD():
    global fwd_state
    fwd_state = 1
    print("Forward")
    return fwd_state

def BACKWD():
    global backwd_state
    backwd_state = 1
    print("Backward")
    return backwd_state

def LEFT():
    global left_state
    left_state = 1
    print("Left")
    return left_state

def RIGHT():
    global right_state
    right_state = 1
    print("Right")
    return right_state

def STOP():
    global stop_state
    stop_state = 1
    print("Stopping")
    return stop_state

def reset_states():
    global fwd_state, backwd_state, left_state, right_state, stop_state
    fwd_state = backwd_state = left_state = right_state = stop_state = 0

def open_controller_gui():
    root = Tk()
    root.geometry("400x400")
    root.title("Controller")

    Label(root, text="Control Panel", font=("Arial", 20)).pack(pady=20)

    Button(root, text="Forward", command=lambda: [reset_states(), FWD()]).pack(pady=10)
    Button(root, text="Backward", command=lambda: [reset_states(), BACKWD()]).pack(pady=10)
    Button(root, text="Left", command=lambda: [reset_states(), LEFT()]).pack(pady=10)
    Button(root, text="Right", command=lambda: [reset_states(), RIGHT()]).pack(pady=10)
    Button(root, text="Stop", command=lambda: [reset_states(), STOP()]).pack(pady=10)

    root.mainloop()


@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command')

    if command == 'forward':
        reset_states()
        FWD()
    elif command == 'backward':
        reset_states()
        BACKWD()
    elif command == 'left':
        reset_states()
        LEFT()
    elif command == 'right':
        reset_states()
        RIGHT()
    elif command == 'stop':
        reset_states()
        STOP()

    return jsonify({"status": f"Command '{command}' executed in GUI"}), 200

def run_gui():
    open_controller_gui()

if __name__ == '__main__':

    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()

    app.run(debug=False, port=5001)
