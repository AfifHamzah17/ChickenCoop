# IoT Smart Lighting and Monitoring System

This project implements an IoT-based smart lighting and environmental monitoring system using an ESP32 microcontroller. The system integrates various sensors, including a DHT22 for temperature and humidity, a Light Dependent Resistor (LDR) for ambient light sensing, and a current sensor to monitor energy consumption. It dynamically adjusts lighting conditions based on ambient light levels and temperature, optimizing energy usage and providing real-time data visualization via ThingSpeak.

## Features

- **WiFi Connectivity**: Connects to a WiFi network for real-time data transmission.
- **Temperature and Humidity Monitoring**: Utilizes the DHT22 sensor to measure environmental temperature and humidity.
- **Light Intensity Measurement**: Employs an LDR to determine the ambient light level, enabling the control of lighting based on natural light conditions.
- **Energy Monitoring**: Monitors electrical current using an ACS712 sensor, calculating the power consumption of connected devices.
- **Dynamic Lighting Control**: Implements fuzzy logic to adjust lighting intensity based on ambient light and temperature, ensuring optimal lighting conditions during nighttime.
- **Real-Time Data Visualization**: Sends data to ThingSpeak for monitoring and visualization, accessible from any web browser.

## Components Required

- ESP32 Microcontroller
- DHT22 Temperature and Humidity Sensor
- Light Dependent Resistor (LDR)
- ACS712 Current Sensor
- Relay Module for light control
- Additional components (resistors, breadboard, etc.)

## Getting Started

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/yourusername/IoT-Smart-Lighting.git
   ```

2. **Install Required Libraries**:  
   Ensure you have the necessary libraries installed in your Arduino IDE:
   - WiFi
   - HTTPClient
   - ArduinoJson
   - RTClib
   - DHT22
   - Wire

3. **Configure WiFi and ThingSpeak**:  
   Update the `WIFI_SSID` and `WIFI_PASSWORD` constants with your WiFi credentials. Replace the `apiKey` and `channelId` with your ThingSpeak account details.

4. **Upload the Code**:  
   Upload the code to your ESP32 microcontroller using the Arduino IDE.

5. **Monitor the Output**:  
   Use the Serial Monitor to view the status messages and ensure data is being sent to ThingSpeak correctly.

## Code Structure

- **Pin Definitions**: Configuration of GPIO pins for sensors and outputs.
- **Setup Functions**: WiFi connection setup and sensor initialization.
- **Sensor Reading Functions**: Methods to read data from the LDR, DHT22, and current sensor.
- **Data Processing**: Functions to calculate light intensity, solar power, and control logic for lighting.
- **Communication**: Functions for sending collected data to ThingSpeak.
- **Main Loop**: Executes sensor readings, controls lighting, and sends data periodically.

## Contributing

Contributions are welcome! If you have suggestions for improvements or features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

---

Feel free to modify any part of this description to better fit your project specifics or personal preferences!
