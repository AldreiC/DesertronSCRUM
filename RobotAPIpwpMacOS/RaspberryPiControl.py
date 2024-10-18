from flask import Flask, request
import RPi.GPIO as GPIO
import time

# Initialize Flask app
app = Flask(__name__)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for motors
LEFT_MOTOR_FORWARD = 17
LEFT_MOTOR_BACKWARD = 18
RIGHT_MOTOR_FORWARD = 22
RIGHT_MOTOR_BACKWARD = 23

# Setup GPIO pins
GPIO.setup(LEFT_MOTOR_FORWARD, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_BACKWARD, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_FORWARD, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_BACKWARD, GPIO.OUT)

def move_forward(duration):
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.HIGH)
    print("Moving forward")
    time.sleep(duration)
    stop_motors()

def move_backward(duration):
    GPIO.output(LEFT_MOTOR_BACKWARD, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_BACKWARD, GPIO.HIGH)
    print("Moving backward")
    time.sleep(duration)
    stop_motors()

def stop_motors():
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.LOW)
    GPIO.output(LEFT_MOTOR_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_BACKWARD, GPIO.LOW)
    print("Stopping")

def turn_left(duration=1):
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.LOW)  # Stop left motor
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.HIGH)  # Move right motor forward
    print("Turning left")
    time.sleep(duration)
    stop_motors()

def turn_right(duration=1):
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.HIGH)  # Move left motor forward
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.LOW)  # Stop right motor
    print("Turning right")
    time.sleep(duration)
    stop_motors()

@app.route('/control_robot', methods=['POST'])
def control_robot():
    action = request.json.get('action')

    if action == 'forward':
        move_forward(2)  # Move forward for 2 seconds
        return "Moving forward", 200

    elif action == 'backward':
        move_backward(2)  # Move backward for 2 seconds
        return "Moving backward", 200

    elif action == 'left':
        turn_left()  # Default duration is 1 second
        return "Turning left", 200

    elif action == 'right':
        turn_right()  # Default duration is 1 second
        return "Turning right", 200

    elif action == 'stop':
        stop_motors()
        return "Stopped", 200

    else:
        return "Invalid action", 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)  # Run the Flask app on Raspberry Pi
    except KeyboardInterrupt:
        stop_motors()
        GPIO.cleanup()
