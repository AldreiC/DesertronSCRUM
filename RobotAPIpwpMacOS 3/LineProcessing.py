import cv2
import numpy as np


# Variables for smoothing
previous_mid_x = None
alpha = 0.7  # Smoothing factor for exponential moving average


def calculate_distance(x1, y1, x2, y2):
   """Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)."""
   return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def smooth_value(new_value, previous_value, alpha=0.7):
   """Smooth a value using exponential moving average."""
   if previous_value is None:
       return new_value
   return int(alpha * previous_value + (1 - alpha) * new_value)


def separate_lines(lines):
   """Separate lines into left and right lanes based on their slopes."""
   left_lines = []
   right_lines = []


   for line in lines:
       for x1, y1, x2, y2 in line:
           slope = (y2 - y1) / (x2 - x1 + 1e-6)  # Add small value to prevent division by zero
           intercept = y1 - slope * x1
           if slope < 0:  # Left lane
               left_lines.append((slope, intercept))
           elif slope > 0:  # Right lane
               right_lines.append((slope, intercept))


   # Average the slopes and intercepts
   left_lane = np.mean(left_lines, axis=0) if left_lines else None
   right_lane = np.mean(right_lines, axis=0) if right_lines else None


   return left_lane, right_lane


def draw_lane_lines(frame, left_lane, right_lane):
   """Draw the left, right, and center lanes."""
   global previous_mid_x


   # Create blank line image
   line_image = np.zeros_like(frame)
   height = frame.shape[0]
  
   # Define bottom and top y-coordinates
   y_bottom = height
   y_top = int(height*.4)  # Draw up to 60% of the frame


   if left_lane is not None and right_lane is not None:
       # Get slopes and intercepts
       left_slope, left_intercept = left_lane
       right_slope, right_intercept = right_lane
      
       # Calculate x-coordinates for bottom points
       left_x_bottom = int((y_bottom - left_intercept) / left_slope)
       right_x_bottom = int((y_bottom - right_intercept) / right_slope)
      
       # Calculate x-coordinates for top points
       left_x_top = int((y_top - left_intercept) / left_slope)
       right_x_top = int((y_top - right_intercept) / right_slope)
      
       # Draw the lanes
       cv2.line(line_image, (left_x_bottom, y_bottom), (left_x_top, y_top), (255, 0, 0), 3)  # Blue
       cv2.line(line_image, (right_x_bottom, y_bottom), (right_x_top, y_top), (255, 0, 0), 3)  # Blue
      
       # Calculate center points
       mid_x_bottom = int((left_x_bottom + right_x_bottom) / 2)
       mid_x_top = int((left_x_top + right_x_top) / 2)
      
       # Apply smoothing only to the bottom point
       if previous_mid_x is None:
           previous_mid_x = mid_x_bottom
          
       smoothed_mid_x_bottom = smooth_value(mid_x_bottom, previous_mid_x, alpha=0.8)
       previous_mid_x = smoothed_mid_x_bottom
      
       # Calculate center line slope based on midpoints
       center_slope = (y_top - y_bottom) / (mid_x_top - smoothed_mid_x_bottom + 1e-6)
       center_intercept = y_bottom - center_slope * smoothed_mid_x_bottom
      
       # Draw the center line
       cv2.line(line_image, (smoothed_mid_x_bottom, y_bottom), (mid_x_top, y_top), (0, 0, 255), 3)  # Red
  
   elif left_lane is not None:
       # Draw just the left lane
       slope, intercept = left_lane
       left_x1 = int((y_bottom - intercept) / slope)
       left_x2 = int((y_top - intercept) / slope)
       cv2.line(line_image, (left_x1, y_bottom), (left_x2, y_top), (255, 0, 0), 3)
  
   elif right_lane is not None:
       # Draw just the right lane
       slope, intercept = right_lane
       right_x1 = int((y_bottom - intercept) / slope)
       right_x2 = int((y_top - intercept) / slope)
       cv2.line(line_image, (right_x1, y_bottom), (right_x2, y_top), (255, 0, 0), 3)


   return line_image


def FINAL_OVERLAY(frame):
   """
   The main function that processes the frame and returns the processed frame.
   It runs all the steps including color filtering, edge detection, line detection, and lane drawing.
  
   Parameters:
       frame: The raw frame from the video stream
  
   Returns:
       frame: The processed frame with the overlayed lane lines
   """
   global previous_mid_x


   try:
       # Resize frame for performance
       frame = cv2.resize(frame, (640, 480))


       # Convert the frame from BGR to HSV color space
       hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
      
       # Define the HSV range for the color of the tape (change this to fit your tape)
       lower_color = np.array([90, 100, 50])  # Broadened lower bound (H, S, V)
       upper_color = np.array([150, 255, 255])  # Broadened upper bound (H, S, V)åßß
      
       # Create a mask to filter for the color of the tape
       mask = cv2.inRange(hsv, lower_color, upper_color)
      
       # Apply the mask to the original frame (only show tape-colored areas)
       masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
      
       # Convert the masked frame to grayscale
       gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
      
       # Apply GaussianBlur to reduce noise and make edge detection smoother
       blurred = cv2.GaussianBlur(gray, (5, 5), 0)
      
       # Detect edges using Canny edge detection
       edges = cv2.Canny(blurred, 50, 150)
      
       # Detect lines using Hough Line Transform
       lines = cv2.HoughLinesP(edges,
                               rho=1,
                               theta=np.pi/180,
                               threshold=50,
                               minLineLength=40,
                               maxLineGap=10)
      
       if lines is not None:
           left_lane, right_lane = separate_lines(lines)
           lane_image = draw_lane_lines(frame, left_lane, right_lane)
           frame = cv2.addWeighted(frame, 0.8, lane_image, 1, 0)


   except Exception as e:
       print(f"Error processing frame: {e}")


   return frame


