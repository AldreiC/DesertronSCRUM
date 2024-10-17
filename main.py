import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor


i2c = busio.IWC(SCL, SDA)
pca = PCA9685(i2c, address=0x60)
pca.frequency = 100

motor1 = motor.DCMotor(pca.channels[9], pca.channels[10])
motor2 = motor.DCMotor(pca.channels[11], pca.channels[12])
motor1.decay_mode = (
    motor.SLOW_DECAY
)
motor2.decay_mode = (
    motor.SLOW_DECAY
)

print("Forwards")
motor1.throttle = 0.5
motor2.throttle = 0.5
time.sleep(1)

print("Backwards slow")
motor1.throttle = -0.5
motor2.throttle = -0.5
time.sleep(1)

print("Left")
motor1.throttle = 0
motor2.throttle = 0.5
time.sleep(1)

print("Right")
motor1.throttle = 0.5
motor2.throttle = 0
time.sleep(1)

print("Stop")
motor1.throttle = 0
motor2.throttle = 0
time.sleep(1)

pca.deinit()
