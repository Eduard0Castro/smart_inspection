# Smart Inspection System (Edge AI + Crazyflie Drone)

This repository contains an embedded inspection system built on a Raspberry Pi 5 integrating:

- physical sensors (motion, environmental)
- the Crazyflie 2.1+ drone with Flow Deck V2 and Multi-ranger Deck
- a locally executed Small Language Model (SLM) via “llama3.2:3b” using Ollama  
- a modular, object-oriented Python codebase for orchestrating sensing, decision-making and drone inspection

The system monitors an indoor environment, interprets user requests in natural language and performs drone-based inspections when motion is detected or when explicitly triggered by the user.

## 1. Repository Structure

```
project/
│
├── actuators/
│   ├── basic_actuators.py        # LED control (green/red)
│   └── crazyflie.py              # Crazyflie actuator interface
│
├── sensors/
│   └── sensors.py                # PIR, BMP280, DHT22, Button, Multi-ranger
│
├── slm/
│   ├── interactivity_handler.py  # Prompt formatting + structured response parsing
│   └── slm_config.py             # SLM initialization + tools (function-calling)
│
└── smart_inspection.py           # Main application (orchestration)
```

## 2. Overview of System Components

### Sensors
The `sensors/` module defines a hierarchy of sensor classes.  
A base abstract class, "Sensor", standardizes configuration, setup and acquisition. Implemented sensors include PIRMotionDetector, BMP280, DHT22, ButtonSensor and MultirangerSensor.

### Actuators
- "BasicActuators": LED control  
- "CrazyflieActuator": drone communication via cflib  

### SLM Integration
- "SLMConfig": model initialization, system prompt, tools variable  
- "InteractivityHandler": prompt formatting and JSON response handling  

### Main Orchestration
"SmartInspection" coordinates sensors, SLM communication, LED control and drone inspection routines.

## 3. Installation Instructions

### Requirements
- Raspberry Pi 5 (64-bit OS)  
- Python 3.9+  
- Crazyflie 2.1+, Flow Deck V2, Multi-ranger Deck  
- Crazyradio 2.0  
- Ollama installed on the Raspberry Pi  

### Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### requirements.txt

```
Adafruit-Blinka==8.67.0
adafruit-circuitpython-bmp280==3.3.9
adafruit-circuitpython-dht==4.0.10
adafruit-circuitpython-busdevice==5.2.14
adafruit-circuitpython-register==1.11.1
gpiozero==2.0.1
lgpio==0.2.2.0
cflib==0.1.29
ollama==0.6.0
```

## 4. Running the System

```
python3 smart_inspection.py
```

Keywords: "drone", "fly", "crazyflie" trigger inspection.

## 5. Extending the System
The architecture supports adding new sensors, actuators and SLM behaviors with minimal changes.