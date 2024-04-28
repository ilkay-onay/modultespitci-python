import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
import cv2

def detect_falling(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert BGR image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for orange color in HSV
    lower_orange = np.array([5, 100, 100])    # Lower bound for orange hue
    upper_orange = np.array([15, 255, 255])   # Upper bound for orange hue

    # Create a mask to isolate orange regions in the image
    mask = cv2.inRange(hsv_image, lower_orange, upper_orange)

    # Calculate the percentage of orange pixels in the image
    total_pixels = np.prod(mask.shape[:2])
    orange_pixels = cv2.countNonZero(mask)
    orange_percentage = (orange_pixels / total_pixels) * 100

    # Determine if the detected orange percentage indicates falling
    falling_threshold = 35  # Only consider falling if orange percentage > 35%
    is_falling = orange_percentage > falling_threshold

    return is_falling, orange_percentage

i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

# If using higher refresh rates yields a 'too many retries' exception,
# try decreasing this value to work with certain pi/camera combinations
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

frame = [0] * 768

# Path to the initial image
image_path = "image.jpg"

while True:
    try:
        mlx.getFrame(frame)
    except ValueError:
        # These happen, no biggie - retry
        continue

    frame_array = np.array(frame).reshape(24, 32)
    
    # Display the image with 'inferno' colormap
    plt.imshow(frame_array, cmap='inferno', interpolation='nearest')
    plt.colorbar()
    plt.savefig(image_path)  # Save the image to a file
    plt.close()  # Close the plot to avoid displaying it

    # Detect falling based on the current image
    is_falling, orange_percentage = detect_falling(image_path)

    if is_falling:
        print(f"The person might have fallen! Orange percentage: {orange_percentage:.2f}%")
        # Add code here to alert or take action
    else:
        print(f"The person is standing. Orange percentage: {orange_percentage:.2f}%")

    # Wait for 5 seconds before capturing the next frame
    time.sleep(5)