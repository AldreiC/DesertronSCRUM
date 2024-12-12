import cv2
import numpy as np
from flask import Flask, Response

app = Flask(__name__)

# Global variables
previous_mid_x = None  # Stores the previous middle x-coordinate for smoothing
alpha = 0.7  # Controls how much weight is given to previous values vs new values in smoothing

# Helper function to calculate distance between two points
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Smooths values over time to reduce jitter
def smooth_value(new_value, previous_value, alpha=0.7):
    if previous_value is None:
        return new_value
    return int(alpha * previous_value + (1 - alpha) * new_value)

# Separates detected lines into left and right lane markers
def separate_lines(lines):
    left_lines = []
    right_lines = []
    # Separate lines based on their slope (negative slope = left lane, positive = right lane)
    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = (y2 - y1) / (x2 - x1 + 1e-6)  # Add small number to prevent division by zero
            intercept = y1 - slope * x1
            if slope < 0:  # Left lane
                left_lines.append((slope, intercept))
            elif slope > 0:  # Right lane
                right_lines.append((slope, intercept))
    
    # Average all detected lines for each side
    left_lane = np.mean(left_lines, axis=0) if left_lines else None
    right_lane = np.mean(right_lines, axis=0) if right_lines else None
    return left_lane, right_lane

# Draws the detected lane lines and middle line on the image
def draw_lane_lines(frame, left_lane, right_lane):
    global previous_mid_x
    line_image = np.zeros_like(frame)

    # Draw left lane line
    if left_lane is not None:
        slope, intercept = left_lane
        left_x1 = int((frame.shape[0] - intercept) / slope)
        left_x2 = int((-intercept) / slope)
        cv2.line(line_image, (left_x1, frame.shape[0]), (left_x2, 0), (255, 0, 0), 3)

    # Draw right lane line and middle line
    if right_lane is not None:
        slope, intercept = right_lane
        right_x1 = int((frame.shape[0] - intercept) / slope)
        right_x2 = int((-intercept) / slope)
        cv2.line(line_image, (right_x1, frame.shape[0]), (right_x2, 0), (255, 0, 0), 3)
        
        # Calculate and draw middle line if both lanes are detected
        if left_lane is not None:
            mid_x_bottom = int((left_x1 + right_x1) / 2)
            mid_x_top = int((left_x2 + right_x2) / 2)
            # Smooth the middle line position
            mid_x_bottom = smooth_value(mid_x_bottom, previous_mid_x)
            mid_x_top = smooth_value(mid_x_top, previous_mid_x)
            previous_mid_x = mid_x_bottom
            cv2.line(line_image, (mid_x_bottom, frame.shape[0]), (mid_x_top, 0), (0, 0, 255), 3)

    return line_image

# Main processing function for detecting and drawing lanes
def FINAL_OVERLAY(frame):
    global previous_mid_x
    try:
        # Resize frame for consistent processing
        frame = cv2.resize(frame, (640, 480))
        
        # Convert to HSV color space for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define blue color range for detecting blue tape
        lower_color = np.array([100, 150, 50])
        upper_color = np.array([140, 255, 255])

        # Create mask for blue colors and apply it
        mask = cv2.inRange(hsv, lower_color, upper_color)
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Process image to detect edges
        gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Detect lines in the image
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50, minLineLength=40, maxLineGap=10)
        if lines is not None:
            left_lane, right_lane = separate_lines(lines)
            lane_image = draw_lane_lines(frame, left_lane, right_lane)
            frame = cv2.addWeighted(frame, 0.8, lane_image, 1, 0)
    except Exception as e:
        print(f"Error processing frame: {e}")

    return frame

# Generator function for video frames
def generate_frames(processed=False):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not open camera.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if processed:
                frame = FINAL_OVERLAY(frame)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

# Flask routes for video streams
@app.route('/video_feed/raw')
def raw_video_feed():
    """Endpoint for raw video stream."""
    return Response(generate_frames(processed=False), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/overlay')
def overlay_video_feed():
    """Endpoint for processed video stream."""
    return Response(generate_frames(processed=True), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)