import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        # Define default window size for feature computation
        # This is the size that all image windows will be resized to
        self.window_size = (64, 64)
        
    def compute_hog(self, image):
        """
        Compute Histogram of Oriented Gradients (HOG) features for an image
        
        HOG captures the shape of objects by looking at the distribution
        of intensity gradients (directional changes in brightness)
        
        Args:
            image: Input image (can be color or grayscale)
            
        Returns:
            numpy array of HOG features
        """
        # Convert image to grayscale if it's in color
        # HOG works on intensity values, so color isn't needed
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize image to standard size for consistent processing
        gray = cv2.resize(gray, self.window_size)
        
        # Calculate gradients in x and y directions
        # Sobel operator detects edges by approximating image gradients
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=1)  # x direction gradient
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=1)  # y direction gradient
        
        # Calculate gradient magnitude and orientation
        magnitude = np.sqrt(gx**2 + gy**2)  # Pythagorean theorem
        orientation = np.arctan2(gy, gx) * 180 / np.pi % 180  # Convert to degrees
        
        # Parameters for HOG computation
        cell_size = 16  # Size of each cell for histogram computation
        num_bins = 9   # Number of orientation bins in histogram
        
        # Compute histograms for each cell
        cell_hist = []
        for y in range(0, gray.shape[0], cell_size):
            for x in range(0, gray.shape[1], cell_size):
                # Extract cell region
                mag_cell = magnitude[y:min(y+cell_size, gray.shape[0]), 
                                  x:min(x+cell_size, gray.shape[1])]
                ori_cell = orientation[y:min(y+cell_size, gray.shape[0]), 
                                    x:min(x+cell_size, gray.shape[1])]
                
                # Compute histogram for current cell
                hist = np.zeros(num_bins)
                bin_idx = (ori_cell / 20).astype(int)  # 180 degrees / 9 bins = 20 degrees per bin
                
                # Accumulate weighted gradients in orientation bins
                for i in range(num_bins):
                    hist[i] = np.sum(mag_cell[bin_idx == i])
                
                cell_hist.extend(hist)
        
        return np.array(cell_hist)

    def find_best_match(self, search_img, template_img, threshold=0.5):
        """
        Find the single best match of template_img within search_img
        
        Args:
            search_img: Large image to search within
            template_img: Small image to find
            threshold: Minimum similarity score to consider a match
            
        Returns:
            tuple: (x, y, width, height, confidence) of best match,
                  or None if no match found above threshold
        """
        # Compute HOG features for template image
        template_features = self.compute_hog(template_img)
        
        # Variables to track best match
        best_match = None
        best_score = threshold  # Initialize with minimum threshold
        
        # Try different scales to find objects of different sizes
        print("Searching for matches at different scales...")
        for scale in np.linspace(0.5, 1.5, 8):  # Try 8 different scales
            # Resize search image according to current scale
            width = int(search_img.shape[1] * scale)
            height = int(search_img.shape[0] * scale)
            scaled_img = cv2.resize(search_img, (width, height))
            
            # Slide window over scaled image
            step_size = 16  # Pixels to move window each step
            for y in range(0, height - self.window_size[1], step_size):
                for x in range(0, width - self.window_size[0], step_size):
                    # Extract window at current position
                    window = scaled_img[y:y+self.window_size[1], 
                                     x:x+self.window_size[0]]
                    
                    # Skip if window is not complete
                    if window.shape[:2] != self.window_size:
                        continue
                    
                    # Compute HOG features for current window
                    window_features = self.compute_hog(window)
                    
                    # Calculate similarity score using normalized dot product
                    # This gives cosine similarity between feature vectors
                    score = np.dot(template_features, window_features) / (
                        np.linalg.norm(template_features) * np.linalg.norm(window_features))
                    
                    # Update best match if current score is higher
                    if score > best_score:
                        best_score = score
                        # Convert coordinates back to original scale
                        best_match = (
                            int(x / scale),  # x coordinate
                            int(y / scale),  # y coordinate
                            int(self.window_size[0] / scale),  # width
                            int(self.window_size[1] / scale),  # height
                            score  # confidence score
                        )
        
        return best_match

def main():
    """
    Main function to load images, find best match, and display results
    """
    print("Loading images...")
    # Load the template (object to find) and search image
    template_img = cv2.imread('wanted_man.png')
    search_img = cv2.imread('searchPlace.jpg')
    
    # Check if images loaded successfully
    if search_img is None or template_img is None:
        print("Error: Could not load one or both images!")
        return
        
    # Print image dimensions for reference
    print(f"Search image size: {search_img.shape}")
    print(f"Template size: {template_img.shape}")
    
    # Downsample very large images for faster processing
    max_dim = 800
    if max(search_img.shape) > max_dim:
        scale = max_dim / max(search_img.shape)
        search_img = cv2.resize(search_img, 
                              (int(search_img.shape[1] * scale),
                               int(search_img.shape[0] * scale)))
        print(f"Resized search image to: {search_img.shape}")
    
    # Create detector and find best match
    print("Searching for best match...")
    detector = ObjectDetector()
    match = detector.find_best_match(search_img, template_img, threshold=0.5)
    
    # Create visualization
    result = search_img.copy()
    
    if match is not None:
        # Unpack match coordinates and score
        x, y, w, h, confidence = match
        
        # Draw rectangle around match
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Draw circle at center of match
        center_x = x + w//2
        center_y = y + h//2
        radius = int(min(w, h) / 4)
        cv2.circle(result, (center_x, center_y), radius, (0, 0, 255), 2)
        
        # Add confidence score text
        score_text = f"Confidence: {confidence:.2%}"
        cv2.putText(result, score_text, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        print(f"Best match found with confidence: {confidence:.2%}")
    else:
        print("No match found above threshold!")
        cv2.putText(result, "No match found!", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Display results
    cv2.imshow('Template to find', template_img)
    cv2.imshow('Best Match Result', result)
    print("Press any key to exit...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
