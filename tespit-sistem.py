import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import cv2
import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import base64
import lzma
from paho import mqtt
acikmi = True

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

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
    else:
        print("Failed to connect, return code ", rc)

def on_publish(client, userdata, mid):
    print("Message published successfully")

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    global acikmi
    print("Received message:", msg.topic, str(msg.payload))
    if str(msg.payload) == "b'hello1'":
        if acikmi:
            client.publish("fall_detection/alert", payload="acik", qos=1)
            print("Response sent: acik")
        else:
            client.publish("fall_detection/alert", payload="kapali", qos=1)
            print("Response sent: kapali")
    if str(msg.payload) == "b'ackapa'":
        acikmi = not acikmi
    if str(msg.payload) == "b'foto'":
        with open("image.jpg", "rb") as img_file:
            #Encode the image file content as base64
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
        client.publish("fall_detection/alert", payload=encoded_image, qos=1)

        


# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client

client = paho.Client(paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("cokgucluisim", "cokguclubirsifre")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("12b10b214cce489e91869af533703219.s1.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish
client.loop_start()


i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
frame = [0] * 768
client.subscribe("fall_detection/alert", qos=1)
while True:
    if acikmi:
        try:
            mlx.getFrame(frame)
        except ValueError:
            # These happen, no biggie - retry
            continue

        frame_array = np.array(frame).reshape(24, 32)
        plt.imshow(frame_array, cmap='inferno', interpolation='nearest')
        plt.axis('off')
        image_path = "image.jpg"
        # Save the thermal image
        plt.savefig(image_path)

        # Call temperature detection function
        percentage_warmer = detect_warmer_temperatures(frame)
        print("Percentage of warmer temperatures in the image: {:.2f}%".format(percentage_warmer))

        # Check if percentage exceeds 40%
        if percentage_warmer > 40.0:
            print("Alert: The person might have fallen!")
            result = client.publish("fall_detection/alert", payload="fallen", qos=1)
            if result.rc == paho.MQTT_ERR_SUCCESS:
                print("Message sent successfully")
            else:
                print("Failed to send message, error code: ", result.rc)

        time.sleep(5)  # Wait for 5 seconds before capturing the next frame

