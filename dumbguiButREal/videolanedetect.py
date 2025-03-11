import cv2
import numpy as np
from collections import deque
import time


def overlayImage(frame, arrow_img, rotation_angle=0):
   """
   Overlay an image onto a frame more efficiently with optional rotation
  
   Args:
       frame: The background frame
       arrow_img: The arrow image to overlay
       rotation_angle: Rotation angle in degrees (0 means no rotation)
   """
   # Make a copy of the arrow image so we don't modify the original
   if rotation_angle != 0:
       # Get the image dimensions
       h, w = arrow_img.shape[:2]
       # Calculate the center of the image
       center = (w // 2, h // 2)
       # Create the rotation matrix
       rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
       # Apply the rotation
       rotated_arrow = cv2.warpAffine(arrow_img, rotation_matrix, (w, h),
                                     flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                     borderValue=(0, 0, 0))
       arrow_to_use = rotated_arrow
   else:
       arrow_to_use = arrow_img
  
   # Get dimensions
   rows, cols, _ = arrow_to_use.shape
   roi = frame[0:rows, 0:cols]


   # Create masks for overlay
   img2gray = cv2.cvtColor(arrow_to_use, cv2.COLOR_BGR2GRAY)
   _, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
   mask_inv = cv2.bitwise_not(mask)


   # Apply masks
   img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
   img2_fg = cv2.bitwise_and(arrow_to_use, arrow_to_use, mask=mask)


   # Add the masked images
   frame[0:rows, 0:cols] = cv2.add(img1_bg, img2_fg)
   return frame


def detect_white_dashed_lanes_left_column(image, roi_mask, left_column_mask, hsv_params):
   """Optimized lane detection focusing only on necessary computations"""
   # Apply both ROI mask and left column mask in one operation
   masked_image = cv2.bitwise_and(image, image, mask=left_column_mask)
  
   # Convert to HSV for color filtering - only process the masked region
   hsv = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)
  
   # Extract parameters
   lower_white, upper_white, lower_yellow, upper_yellow = hsv_params
  
   # Create white and yellow masks in one step
   white_mask = cv2.inRange(hsv, lower_white, upper_white)
   yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
   combined_mask = cv2.bitwise_or(white_mask, yellow_mask)
  
   # Apply combined mask
   filtered_image = cv2.bitwise_and(masked_image, masked_image, mask=combined_mask)
  
   # Process grayscale and edge detection in a more optimized way
   gray = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
   gray = cv2.equalizeHist(gray)
   blurred = cv2.GaussianBlur(gray, (3, 3), 0)
   edges = cv2.Canny(blurred, 30, 200)
  
   # Use pre-defined kernel for dilation
   edges = cv2.dilate(edges, DILATION_KERNEL, iterations=2)
  
   # Detect line segments
   lines = cv2.HoughLinesP(
       edges,
       rho=1,
       theta=np.pi/180,
       threshold=30,
       minLineLength=15,
       maxLineGap=200
   )
  
   left_lines = []
  
   if lines is not None:
       for line in lines:
           x1, y1, x2, y2 = line[0]
           if x2 - x1 == 0:  # Avoid division by zero
               continue
          
           slope = (y2 - y1) / (x2 - x1)
          
           # Filter for meaningful negative slopes
           if -0.3 > slope:
               left_lines.append((x1, y1, x2, y2, slope))
  
   return left_lines


def mirror_line_to_right(left_line, frame_width):
   """Mirror a line from left to right with fixed adjustments to improve performance"""
   if left_line is None:
       return None
  
   # Unpack coordinates
   left_x1, y1, left_x2, y2 = left_line
  
   # Apply fixed adjustments for better performance
   right_x1 = frame_width - left_x1 - 750
   right_x2 = frame_width - left_x2 - 15
  
   # Determine which point is at the bottom
   if y1 > y2:
       right_y1 = y1 + 1200
       right_y2 = y2
   else:
       right_y1 = y1
       right_y2 = y2 + 1200
  
   return [right_x1, right_y1, right_x2, right_y2]


def average_lines(lines, prev_lines, frame_height, top_y):
   """Compute average line with optimized calculations"""
   if not lines:
       return None


   # Use vectorized operations for averaging
   line_array = np.array(lines)
   x1s, y1s, x2s, y2s, slopes = line_array[:, 0], line_array[:, 1], line_array[:, 2], line_array[:, 3], line_array[:, 4]
  
   avg_slope = np.mean(slopes)
   x1, y1, x2, y2 = np.mean(x1s), np.mean(y1s), np.mean(x2s), np.mean(y2s)


   if prev_lines:
       prev = np.mean(prev_lines, axis=0)
       # Weighted average for smoothing
       x1 = 0.7 * prev[0] + 0.3 * x1
       y1 = 0.7 * prev[1] + 0.3 * y1
       x2 = 0.7 * prev[2] + 0.3 * x2
       y2 = 0.7 * prev[3] + 0.3 * y2
       # Recalculate slope with small epsilon to avoid division by zero
       avg_slope = (y2 - y1) / (x2 - x1 + 1e-5)


   if avg_slope != 0:
       # Extend line to frame boundaries
       bottom_x = int(x1 + (frame_height - y1) / avg_slope)
       top_x = int(x1 + (top_y - y1) / avg_slope)
       return [bottom_x, frame_height, top_x, top_y]


   return None


def draw_centerline(left_line, right_line):
   """
   Draws the centerline between the left and right lanes.
   Simple midpoint calculation - the original approach.
   """
   if left_line is None or right_line is None:
       return None
  
   # Unpack line coordinates
   left_x1, left_y1, left_x2, left_y2 = left_line
   right_x1, right_y1, right_x2, right_y2 = right_line
  
   # Compute midpoint between corresponding points of left and right lanes
   center_x1 = (left_x1 + right_x1) // 2
   center_y1 = (left_y1 + right_y1) // 2
   center_x2 = (left_x2 + right_x2) // 2
   center_y2 = (left_y2 + right_y2) // 2
  
   return [center_x1, center_y1, center_x2, center_y2]


def create_lane_polygon(line, lane_width=50):
   """
   Create a polygon (rectangle) from a line with specified width
   Optimized version of the original function
   """
   if line is None:
       return None
  
   x1, y1, x2, y2 = line
  
   # Calculate perpendicular vector to the line
   dx = x2 - x1
   dy = y2 - y1
   length = np.sqrt(dx*dx + dy*dy)
  
   # Avoid division by zero
   if length < 1e-5:
       return None
  
   # Normalize and rotate 90 degrees to get perpendicular vector
   perpendicular_x = -dy / length
   perpendicular_y = dx / length
  
   # Calculate the four corners of the rectangle
   half_width = lane_width / 2
   points = np.array([
       [int(x1 + perpendicular_x * half_width), int(y1 + perpendicular_y * half_width)],
       [int(x2 + perpendicular_x * half_width), int(y2 + perpendicular_y * half_width)],
       [int(x2 - perpendicular_x * half_width), int(y2 - perpendicular_y * half_width)],
       [int(x1 - perpendicular_x * half_width), int(y1 - perpendicular_y * half_width)]
   ], dtype=np.int32)
  
   return points


def draw_transparent_polygon(image, polygon, color, alpha=0.4):
   """Draw semi-transparent polygon - more efficient implementation"""
   if polygon is None:
       return image
  
   # Create a mask instead of a full copy
   mask = np.zeros_like(image)
   cv2.fillPoly(mask, [polygon], color)
  
   # Use addWeighted for blending
   return cv2.addWeighted(mask, alpha, image, 1, 0)


def process_video(video_path, arrow_path, frame,frame_width, frame_height, fps):
   global DILATION_KERNEL
   DILATION_KERNEL = np.ones((3, 3), np.uint8)
   if frame is None:
        return None
   # Start time for performance measurement
   start_time = time.time()
   frames_processed = 0
  
   # Initialize video capture
   # Get video properties
   
   # Special timing for arrow rotation (2:12 to 2:32)
   start_rotation_frame = int(40) * int(fps) 
   end_rotation_frame = start_rotation_frame + 5 * int(fps)  
  
   # Preload and resize arrow image once
   arrow_img = cv2.imread(arrow_path)
   if arrow_img is None:
       print(f"Error: Could not load arrow image {arrow_path}")
       return
   arrow_img = cv2.resize(arrow_img, (300, 300))


   # Pre-compute ROI masks
   # Define ROI boundaries
   bottom_y = frame_height
   top_y = int(frame_height * 0.47)
  
   # Create full ROI mask
   roi_points = np.array([[(0, bottom_y), (0, top_y),
                          (frame_width, top_y), (frame_width, bottom_y)]], dtype=np.int32)
   roi_mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
   cv2.fillPoly(roi_mask, roi_points, 255)
  
   # Create left column mask (33% of width)
   left_column_width = int(frame_width * 0.33)
   left_column_mask = np.zeros_like(roi_mask)
   left_column_mask[:, 0:left_column_width] = roi_mask[:, 0:left_column_width]
  
   # Define HSV parameters for lane detection
   hsv_params = (
       np.array([0, 0, 180]),     # lower_white
       np.array([180, 40, 255]),  # upper_white
       np.array([15, 80, 150]),   # lower_yellow
       np.array([35, 255, 255])   # upper_yellow
   )
  
   # Buffers for smoothing
   left_lines_buffer = deque(maxlen=5)
  
   # Define default lane positions
   default_left_bottom_x = int(left_column_width * 0.7)
   default_left_top_x = int(left_column_width * 0.3)
   default_left_line = [default_left_bottom_x, bottom_y, default_left_top_x, top_y]
   default_right_line = mirror_line_to_right(default_left_line, frame_width)



   
      
   frames_processed += 1
      
       # Detect lines in left column
   left_lines = detect_white_dashed_lanes_left_column(
           frame, roi_mask, left_column_mask, hsv_params)
      
       # Process left lane
   avg_left = None
   if left_lines:
           avg_left = average_lines(left_lines, left_lines_buffer, frame_height, top_y)
           if avg_left:
               left_lines_buffer.append(avg_left)
      
       # Use default or last valid lane if needed
   if not avg_left:
           if not left_lines_buffer or len(left_lines_buffer) == 0:
               avg_left = default_left_line
           else:
               avg_left = left_lines_buffer[-1]
      
       # Mirror left lane to get right lane
   avg_right = mirror_line_to_right(avg_left, frame_width)
      
       # Create visualization frame
   result_frame = frame.copy()
      
       # Calculate center line
   if avg_left is not None and avg_right is not None:
        center_line = draw_centerline(avg_left, avg_right)
      
       # Create polygons
        center_line_polygon = create_lane_polygon(center_line, lane_width=75)
        left_lane_polygon = create_lane_polygon(avg_left, lane_width=100)
        right_lane_polygon = create_lane_polygon(avg_right, lane_width=100)
      
       # Draw polygons - order matters for overlapping
   if left_lane_polygon is not None:
           result_frame = draw_transparent_polygon(result_frame, left_lane_polygon, (0, 0, 255), alpha=0.75)
      
   if right_lane_polygon is not None:
           result_frame = draw_transparent_polygon(result_frame, right_lane_polygon, (0, 0, 255), alpha=0.75)
          
   if center_line_polygon is not None:
           result_frame = draw_transparent_polygon(result_frame, center_line_polygon, (255, 0, 0), alpha=0.75)
      
       
   arrow_rotation = 0
   if start_rotation_frame <= frames_processed < end_rotation_frame:
           # Turn to the right (90 degrees)
           arrow_rotation = -90
      
       # Overlay arrow with rotation as needed
   result_frame = overlayImage(result_frame, arrow_img, rotation_angle=arrow_rotation)
      
       # Display the result
       
       # output.write(result_frame)  # Uncomment to save video
      
       # Calculate and display FPS every 30 frames
   if frames_processed % 30 == 0:
           elapsed_time = time.time() - start_time
           current_fps = frames_processed / elapsed_time
           print(f"FPS: {current_fps:.2f}")
          
           # Show time in minutes and seconds for reference
           current_seconds = frames_processed / fps
           minutes = int(current_seconds // 60)
           seconds = int(current_seconds % 60)
           print(f"Video time: {minutes}:{seconds:02d}")

      


   
 
  
   # Print final performance stats
   total_time = time.time() - start_time
   avg_fps = frames_processed / total_time
   print(f"Total frames processed: {frames_processed}")
   print(f"Total processing time: {total_time:.2f} seconds")
   print(f"Average FPS: {avg_fps:.2f}")
   return result_frame

def main():
   # Define global constants for reuse
   global DILATION_KERNEL
   DILATION_KERNEL = np.ones((3, 3), np.uint8)
  
   video_path = "ogvld.mov"
   arrow_path = "arrowimage.png"
  
   process_video(video_path, arrow_path)

if __name__ == "__main__":
   main()

