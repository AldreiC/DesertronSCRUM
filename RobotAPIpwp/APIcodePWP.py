from flask import Flask, request, jsonify
from tkinter import *

app = Flask(__name__)


def open_controller_gui():
    root = Tk()
    root.geometry("400x400")
    root.title("Controller")

    Label(root, text="Control Panel", font=("Arial", 20)).pack(pady=20)

    Button(root, text="Forward", command=lambda: print("Moving Forward")).pack(pady=10)
    Button(root, text="Backward", command=lambda: print("Moving Backward")).pack(pady=10)
    Button(root, text="Left", command=lambda: print("Turning Left")).pack(pady=10)
    Button(root, text="Right", command=lambda: print("Turning Right")).pack(pady=10)
    Button(root, text="Stop", command=lambda: print("Stopping")).pack(pady=10)

    root.mainloop()


@app.route('/open_controller', methods=['POST'])
def open_controller():
    open_controller_gui()  
    return jsonify({"status": "Controller opened"}), 200

if __name__ == '__main__':
    app.run(debug=True)


#curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d r '{"email": "a@a.com", "password": "AAAAAA")'
#curl -X GET http://127.0.0.1:5000/movement -H "Content-Type: application/json"
#curl -X POST http://127.0.0.1:5000/command -H "Content-Type: application/json" -d '{"command": "forward"}'
