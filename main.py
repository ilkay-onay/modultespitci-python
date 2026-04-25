"""
TÜBİTAK 2209-A: Privacy-Preserving Thermal Fall Detection System (Edge Node)
Author: İlkay ONAY
Description: 
    This script runs on a Raspberry Pi edge device. It captures thermal arrays 
    from an MLX90640 sensor via I2C, processes the data to detect human heat 
    signatures, and identifies fall anomalies based on spatial distribution. 
    It communicates with a central system via secure MQTT.
"""

import time
import os
import io
import base64
import logging
import signal
import sys
from typing import Tuple, Optional

import board
import busio
import numpy as np
import cv2
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt_client
from paho.mqtt.client import MQTTv5
import adafruit_mlx90640

# --- Configuration & Environment Setup ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "12b10b214cce489e91869af533703219.s1.eu.hivemq.cloud")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USER = os.getenv("MQTT_USER", "YOUR_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASS", "YOUR_PASSWORD")
MQTT_TOPIC = "fall_detection/alert"

TEMP_MIN_THRESHOLD = 30.0  
TEMP_MAX_THRESHOLD = 40.0  
FALL_PERCENTAGE_THRESHOLD = 40.0  

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ThermalEdgeAI")


class ThermalFallDetector:
    """
    Main class handling the MLX90640 sensor, thermal image processing, 
    and MQTT communication. Developed for resource-constrained Edge IoT devices.
    """
    
    def __init__(self):
        self.is_active = True
        self.frame_data = [0] * 768  # MLX90640 returns a 24x32 array (768 pixels)
        self.mlx = None
        self.mqtt_client = None
        
        self._setup_hardware()
        self._setup_mqtt()
        
        # Handle graceful shutdowns (Ctrl+C or systemd stop)
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)

    def _setup_hardware(self) -> None:
        """Initializes the I2C bus and the MLX90640 sensor."""
        logger.info("Initializing I2C bus and MLX90640 sensor...")
        try:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
            self.mlx = adafruit_mlx90640.MLX90640(i2c)
            self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
            logger.info(f"MLX90640 detected. Serial: {[hex(i) for i in self.mlx.serial_number]}")
        except Exception as e:
            logger.critical(f"Failed to initialize hardware: {e}")
            sys.exit(1)

    def _setup_mqtt(self) -> None:
        """Configures the MQTT client and connects to the HiveMQ cloud broker."""
        logger.info(f"Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...")
        
        self.mqtt_client = mqtt_client.Client(
            client_id="Pi_Thermal_Edge",
            protocol=MQTTv5
        )
        
        import ssl
        self.mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
        
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"MQTT Connection failed: {e}")

    def _on_connect(self, client, userdata, flags, rc, properties=None) -> None:
        if rc == 0:
            logger.info("Successfully connected to MQTT Broker.")
            client.subscribe(MQTT_TOPIC, qos=1)
            logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
        else:
            logger.warning(f"MQTT connection failed with code {rc}")

    def _on_message(self, client, userdata, msg) -> None:
        """Handles incoming commands from the mobile application/dashboard."""
        payload = msg.payload.decode('utf-8', errors='ignore').strip()
        logger.info(f"Incoming command on {msg.topic}: {payload}")

        if payload == "hello1":
            status = "acik" if self.is_active else "kapali"
            self._publish_message(status)
            
        elif payload == "ackapa":
            self.is_active = not self.is_active
            status_msg = "System Activated" if self.is_active else "System Paused"
            logger.info(status_msg)
            
        elif payload == "foto":
            self._send_thermal_snapshot()

    def _publish_message(self, payload: str) -> None:
        """Helper function to publish messages via MQTT."""
        result = self.mqtt_client.publish(MQTT_TOPIC, payload=payload, qos=1)
        if result.rc != mqtt_client.MQTT_ERR_SUCCESS:
            logger.error(f"Failed to send message, error code: {result.rc}")

    def _send_thermal_snapshot(self) -> None:
        """
        Captures the current thermal frame, renders a heatmap using Matplotlib 
        IN-MEMORY (without saving to disk to save SD card lifespan), and sends 
        it as a Base64 string over MQTT.
        """
        logger.info("Generating in-memory thermal snapshot...")
        try:
            frame_array = np.array(self.frame_data).reshape(24, 32)
            
            fig, ax = plt.subplots(figsize=(4, 3))
            cax = ax.imshow(frame_array, cmap='inferno', interpolation='nearest')
            ax.axis('off')
            
            buf = io.BytesIO()
            fig.savefig(buf, format='jpg', bbox_inches='tight', pad_inches=0)
            plt.close(fig) 
            
            buf.seek(0)
            encoded_image = base64.b64encode(buf.read()).decode('utf-8')
            self._publish_message(encoded_image)
            logger.info("Thermal snapshot sent successfully.")
            
        except Exception as e:
            logger.error(f"Error generating snapshot: {e}")

    def analyze_thermal_frame(self) -> Tuple[bool, float]:
        """
        Analyzes the thermal frame to detect human presence and potential falls.
        """
        flat_data = np.array(self.frame_data)
        
        mask = ((flat_data > TEMP_MIN_THRESHOLD) & (flat_data < TEMP_MAX_THRESHOLD))
        
        warmer_pixels = np.sum(mask)
        total_pixels = flat_data.size
        percentage_warmer = (warmer_pixels / total_pixels) * 100.0
        
        is_falling = percentage_warmer > FALL_PERCENTAGE_THRESHOLD
        return is_falling, percentage_warmer

    def run(self) -> None:
        """Main execution loop."""
        logger.info("Starting Edge AI Thermal Detection Loop...")
        
        while True:
            if self.is_active:
                try:
                    self.mlx.getFrame(self.frame_data)
                except ValueError:
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    logger.error(f"Sensor read error: {e}")
                    time.sleep(1)
                    continue

                is_falling, percentage = self.analyze_thermal_frame()
                logger.debug(f"Human heat signature coverage: {percentage:.2f}%")

                if is_falling:
                    logger.warning(f"🚨 ALERT! Fall detected! Heat coverage: {percentage:.2f}%")
                    self._publish_message("fallen")
            
            time.sleep(3)

    def _graceful_shutdown(self, signum, frame) -> None:
        """Handles Ctrl+C or kill signals to clean up connections properly."""
        logger.info("Graceful shutdown initiated...")
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        logger.info("System offline.")
        sys.exit(0)

if __name__ == "__main__":
    print("""
    ===================================================
    Privacy-Preserving Thermal Fall Detector (Edge)
    Powered by Raspberry Pi & MLX90640
    ===================================================
    """)
    detector = ThermalFallDetector()
    detector.run()
