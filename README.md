# Smart City IoT System for Traffic and Air Quality Monitoring with GenAI-Assisted Route Optimization

## Overview
This project implements an IoT-based system for monitoring urban air quality and supporting route optimization decisions.

The system collects environmental data from distributed IoT nodes, transmits it to a cloud database in real time, and uses the data to evaluate routes based on multiple factors such as air quality and traffic conditions.

---

## Objectives
- Monitor air quality using low-cost sensors  
- Collect and transmit real-time environmental data  
- Build a unified data pipeline from device to cloud  
- Support route evaluation based on environmental conditions  
- Integrate AI-assisted logic for route optimization  

---

## System Architecture

### 1. IoT Layer
- Microcontroller: ESP32-WROOM  
- Sensors:
  - GP2Y1010AU0F (dust concentration)  
  - MQ-135 (gas/air quality index)  
  - AHT10 (temperature and humidity)  
- Data is sampled, filtered, and preprocessed locally  

Additional device (not yet integrated in current firmware):
- ESP32-CAM  
  - Captures images of roads and traffic conditions  
  - Intended for future integration into traffic analysis  

---

### 2. Communication Layer
- 4G module (SIM A7680C or equivalent)  
- Protocol: MQTT  
- ESP32-WROOM publishes data to Node-RED via MQTT  

---

### 3. Data Processing Layer
- Node-RED acts as the central data handler:
  - Receives MQTT data from ESP32  
  - Processes and formats sensor data  
  - Pushes data to Firebase Realtime Database  

---

### 4. Cloud & Application Layer
- Firebase Realtime Database:
  - Stores sensor data in real time  
- Firebase Studio:
  - Visualizes data on dashboards  
  - Provides an interface for monitoring system status  

---

## Key Features
- Real-time air quality monitoring  
- Multi-sensor data fusion (dust, gas, temperature, humidity)  
- MQTT-based data transmission over 4G  
- Centralized data processing using Node-RED  
- Real-time visualization using Firebase  

---

## Route Evaluation Strategy
Routes are evaluated using a combination of:
- Distance  
- Dust concentration (from GP2Y1010AU0F)  
- Gas index (from MQ-135)  
- Environmental conditions (temperature, humidity)  
- Data coverage along the route  

A weighted scoring mechanism is applied to balance these factors depending on route characteristics and data availability.

---

## Hardware Setup
- ESP32-WROOM connected to:
  - GP2Y1010AU0F (analog input)  
  - MQ-135 (analog input)  
  - AHT10 (I2C interface)  
- SIM module connected via UART for 4G communication  
- Stable power supply required for accurate sensor readings  

---

## Software Components
- Arduino framework for ESP32 firmware  
- TinyGSM for 4G communication  
- MQTT protocol for data transmission  
- Node-RED for data processing and routing  
- Firebase Realtime Database for storage  
- Firebase Studio for data visualization  

---

## Data Flow
1. Sensors collect environmental data on ESP32-WROOM  
2. ESP32 publishes data via MQTT over 4G  
3. Node-RED receives and processes the data  
4. Processed data is pushed to Firebase Realtime Database  
5. Firebase Studio displays real-time data on the dashboard  

---

## Repository Structure
/firmware
├── Final_code_1.ino
├── GP2Y1010AU0F.cpp
├── GP2Y1010AU0F.h

/backend
├── node-red-flows.json

/docs
├── system_design.md
├── architecture.md


---

## Getting Started

### 1. Hardware Setup
- Connect all sensors to ESP32-WROOM  
- Connect SIM module via UART  
- Ensure stable power supply  
<img width="612" height="663" alt="image" src="https://github.com/user-attachments/assets/44df917b-e3a2-407e-b8cc-368f3f385a15" />

*Note: A voltage divider circuit MUST be used to convert the output voltage level of the GP2Y1010AU0F sensor (maximum approximately 5V) to a voltage level suitable for the analog input of the ESP32 microcontroller (maximum 3.3V). The circuit consists of two resistors connected in series, where the output voltage is taken at the midpoint between the two resistors according to the voltage divider principle. Using a voltage divider circuit helps protect the ADC pin of the ESP32 and ensures accurate and safe measurement signals.

GP2Y Vo ──[10k]──┬── GPIO35
                 │
                [20k]
                 │
                GND
  
### 2. Firmware
- Open project in Arduino IDE or PlatformIO  
- Install required libraries:
  - TinyGSM  
  - Adafruit AHTX0  
- Configure:
  - APN settings  
  - MQTT broker settings  
- Upload firmware to ESP32  

### 3. Node-RED
- Set up MQTT broker connection  
- Create flow to receive ESP32 data  
- Process and forward data to Firebase  
<img width="1323" height="71" alt="image" src="https://github.com/user-attachments/assets/ceeb23c0-666d-4723-b244-f15d3e172ad4" />

### 4. Firebase
- Create Realtime Database  
- Configure Node-RED to push data  
- Use Firebase Studio to visualize data  

---

## Limitations
- Low-cost sensors provide relative measurements, not reference-grade accuracy  
- MQ-135 requires calibration for reliable gas index values  
- Data coverage depends on deployment density of IoT nodes  
- ESP32-CAM is not yet integrated into the current system  
---

## Author
- IoT System: Data acquisition, sensor integration, and communication  
- Backend: Data processing with Node-RED and Firebase integration  
- Optimization: Route evaluation logic and scoring system  

---

## License
This project is developed for academic purposes. The license can be updated as needed.
