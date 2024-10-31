from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    result = subprocess.run(['python3', 'main.py'], capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    app.run(debug=True)
