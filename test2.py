import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import cv2

def detect_warmer_temperatures(thermal_data):
    # Define temperature thresholds for warmer regions
    min_temp_threshold = 30.0  # Adjust these values as needed
    max_temp_threshold = 40.0  # Adjust these values as needed

    # Flatten the thermal data array
    flat_data = np.array(thermal_data).flatten()

    # Create a binary mask for pixels with temperatures within the threshold range
    mask = ((flat_data > min_temp_threshold) & (flat_data < max_temp_threshold)).astype(np.uint8) * 255
    mask = mask.reshape(24, 32)

    # Save the binary mask containing the detected warmer pixels to a file
    cv2.imwrite("detected_image.jpg", mask)

    # Calculate the percentage of pixels with warmer temperatures
    total_pixels = flat_data.size
    warmer_pixels = np.sum(mask == 255)
    percentage_warmer = (warmer_pixels / total_pixels) * 100

    return percentage_warmer

i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
frame = [0] * 768

while True:
    try:
        mlx.getFrame(frame)
    except ValueError:
        # These happen, no biggie - retry
        continue

    frame_array = np.array(frame).reshape(24, 32)

    # Save the thermal image
    cv2.imwrite('image.jpg', frame_array)

    # Call temperature detection function
    percentage_warmer = detect_warmer_temperatures(frame)
    print("Percentage of warmer temperatures in the image: {:.2f}%".format(percentage_warmer))

    # Check if percentage exceeds 40%
    if percentage_warmer > 40.0:
        print("Alert: The person might have fallen!")

    time.sleep(5)  # Wait for 5 seconds before capturing the next frame




