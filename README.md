# modultespitci-python

## Overview

The `modultespitci-python` project is a sophisticated thermal imaging and fall detection system designed for real-time monitoring. Leveraging the MLX90640 thermal camera, this system captures thermal data, processes it to identify warmer regions, and employs advanced algorithms to detect potential falls. The system integrates with an MQTT broker for remote monitoring and alerts, enabling seamless communication and actionable insights.

This project is built with a focus on robustness and accuracy, providing a reliable solution for applications requiring continuous thermal surveillance and immediate fall detection.

## Features

*   **Real-time Thermal Imaging:** Captures and processes thermal data from the MLX90640 sensor.
*   **Advanced Fall Detection:** Implements algorithms to detect potential falls based on thermal data analysis and image processing.
*   **MQTT Integration:** Connects to an MQTT broker for publishing alerts and receiving commands.
*   **Customizable Thresholds:** Allows for adjustment of temperature thresholds for warmer region detection.
*   **Image Processing:** Utilizes libraries like OpenCV and Matplotlib for image manipulation, saving, and visualization.
*   **Error Handling:** Includes mechanisms to handle potential errors during sensor reading and data processing.
*   **Secure Communication:** Supports TLS for secure MQTT connections.

## Project Structure

```
.
├── LICENSE
├── asd.py
├── tespit-sistem.py
├── test.py
├── test2.py
└── testtt.py
```

## Getting Started

To run the `modultespitci-python` project, you will need to have the necessary hardware (MLX90640 thermal camera, Raspberry Pi or compatible board) and Python libraries installed.

1.  **Install Dependencies:**
    Ensure you have the required libraries installed. You can install them using pip:

    ```bash
    pip install adafruit-circuitpython-mlx90640 paho-mqtt numpy opencv-python matplotlib
    ```

2.  **Configure MQTT:**
    The `tespit-sistem.py` script requires MQTT credentials and broker details. Update the following lines in `tespit-sistem.py` with your specific information:

    ```python
    client.username_pw_set("cokgucluisim", "cokguclubirsifre")
    client.connect("12b10b214cce489e91869af533703219.s1.eu.hivemq.cloud", 8883)
    ```

3.  **Run the System:**
    To start the thermal imaging and fall detection system, execute the main script:

    ```bash
    python tespit-sistem.py
    ```

    This will initialize the thermal camera, connect to the MQTT broker, and begin processing thermal data for fall detection.

    **Note:** The `asd.py` script is for live camera display, and `test.py`, `test2.py`, and `testtt.py` are for testing specific functionalities of the thermal camera and detection algorithms.

## License

This project is licensed under the GNU General Public License v3.0. See the `LICENSE` file for more details.