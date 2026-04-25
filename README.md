# 🌡️ Privacy-Preserving Thermal Fall Detection System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Raspberry_Pi-C51A4A.svg)]()
[![Sensor](https://img.shields.io/badge/Sensor-MLX90640_Thermal-orange.svg)]()
[![MQTT](https://img.shields.io/badge/Protocol-MQTT-660066.svg)]()
[![Grant](https://img.shields.io/badge/Grant-TÜBİTAK_2209--A-red.svg)]()

> **🏆 Supported by TÜBİTAK (The Scientific and Technological Research Council of Turkey) under the 2209-A University Students Research Projects Support Program.**

## 📌 Overview

Falls are a major health risk for the elderly and mobility-impaired individuals, especially in high-risk indoor environments like bathrooms or bedrooms. Traditional camera-based monitoring systems heavily compromise user privacy. 

This project solves that problem by using an **MLX90640 Thermal Camera** paired with a **Raspberry Pi**. Instead of capturing RGB video, the system analyzes low-resolution thermal heatmaps. It detects human presence based on temperature thresholds (30°C - 40°C) and identifies sudden falls by analyzing the spatial distribution of these heat signatures.

When a fall is detected, the system immediately triggers an alert via **MQTT**, which is then pushed to a companion mobile application built with Flutter.

*(Insert your hardware/thermal heatmap photo here)*

## 🚀 Key Features

* **100% Privacy-Preserving:** No recognizable visual data is ever captured, making it safe for bedrooms and bathrooms.
* **Edge Computing:** All thermal image processing (masking, thresholding, blob detection) is done locally on the Raspberry Pi using OpenCV and NumPy.
* **Real-time IoT Communication:** Integrates seamlessly with a Cloud MQTT Broker (HiveMQ) over TLS for secure, instant alert transmission.
* **Remote Control:** The system can be armed/disarmed remotely, and authorized users can request a snapshot of the thermal heatmap via the mobile app.
* **Cross-Platform Companion App:** Works in tandem with the [Takip Sistem Flutter App](https://github.com/ilkay-onay/takipsistem) for real-time notifications.

## 🏗️ System Architecture

1. **Hardware:** MLX90640 Infrared Thermal Camera + Raspberry Pi 4.
2. **Detection Logic:** 
   * Captures 24x32 thermal arrays.
   * Flattens and masks temperatures within the human body range (30.0°C - 40.0°C).
   * Calculates the percentage of the frame occupied by the heat signature.
   * Exceeding a dynamically calibrated threshold triggers the "Fall Detected" state.
3. **Communication:** Alerts and Base64-encoded thermal snapshots are published to an MQTT topic (`fall_detection/alert`).

## 💻 Hardware & Software Requirements

* **Hardware:**
  * Raspberry Pi (3B+ or 4)
  * MLX90640 I2C Thermal Camera
* **Software/Libraries:**
  * Python 3
  * `adafruit-circuitpython-mlx90640`
  * `opencv-python-headless`
  * `paho-mqtt`
  * `numpy` & `matplotlib`

## ⚙️ Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ilkay-onay/Thermal-Fall-Detection-IoT.git
   cd Thermal-Fall-Detection-IoT
   ```

2. **Install dependencies:**
   Ensure I2C is enabled on your Raspberry Pi.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MQTT:**
   Set your MQTT credentials in the `.env` file.

4. **Run the system:**
   ```bash
   python main.py
   ```

## 📜 License
This project is licensed under the [GNU General Public License v3.0](LICENSE).
