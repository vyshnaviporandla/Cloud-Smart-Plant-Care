# Cloud Smart Plant Care

### Cloud-Connected Plant Monitoring & Automatic Watering System

A cloud-based IoT application that monitors plant conditions using a virtual sensor, sends real-time data to a cloud backend, stores data in Firebase Firestore, and automatically triggers watering when soil moisture falls below a configured threshold.

This project demonstrates the integration of **IoT, Cloud Computing, REST APIs, Cloud Databases, Authentication, Automation, and Web Technologies** without requiring physical hardware.

---

## Project Overview

Traditional plant watering requires regular manual monitoring and can result in overwatering or underwatering.

**Cloud Smart Plant Care** provides an automated solution that:

* Monitors soil moisture
* Monitors temperature
* Monitors humidity
* Monitors light intensity
* Sends sensor data to a cloud backend
* Stores sensor and watering data in the cloud
* Automatically starts watering when soil moisture is low
* Provides a web dashboard for monitoring
* Generates alerts for low soil moisture
* Maintains watering history
* Supports manual watering
* Provides authenticated user access

A Python-based virtual IoT sensor is used instead of physical hardware, making the system easy to demonstrate and test.

---

## Objectives

1. Build an IoT-based plant monitoring system.
2. Connect a virtual sensor to a cloud backend.
3. Store plant sensor data in a cloud database.
4. Implement automatic watering based on soil moisture.
5. Provide a real-time monitoring dashboard.
6. Implement authentication using Firebase Authentication.
7. Demonstrate REST API communication.
8. Demonstrate cloud deployment using Firebase and Render.
9. Demonstrate cloud computing concepts such as scalability, availability, authentication, cloud storage, and automation.

---

##  Key Features

###  Sensor Monitoring

The system monitors:

* Soil Moisture
* Temperature
* Humidity
* Light Level

###  Automatic Watering

When:

```text
Soil Moisture < Moisture Threshold
```

the backend automatically starts the virtual pump.

Example:

```text
Threshold = 35%
    |
Moisture = 29%
    |  
Automatic watering starts
    |
Virtual pump ON
    |   
Moisture increases
    |
Pump OFF
```

###  Manual Watering

Users can manually start watering from the dashboard.

###  Dashboard

The dashboard displays:

* Current sensor values
* Moisture history chart
* Device status
* Pump status
* Automation settings
* Watering history
* Alerts

###  Alerts

The system generates alerts when low soil moisture is detected.

###  Authentication

Firebase Authentication provides email/password login for users.

### Cloud Storage

Sensor readings, device information, watering events, and alerts are stored using Firebase Firestore.

---

#  System Architecture

```text
                  VIRTUAL IoT SENSOR
                         ¦
                         ¦ HTTPS / REST
                         |
                +------------------+
                ¦  FLASK BACKEND   ¦
                ¦     RENDER       ¦
                +------------------+
                         ¦
              +---------------------+
              ¦                     ¦
              |                     |
       AUTOMATION ENGINE       FIRESTORE
              ¦                     ¦
              ¦                     ¦
              |                     ¦
       VIRTUAL WATER PUMP            ¦
                                    ¦
                                    |
                           CLOUD DATA STORAGE
                                    ¦
                                    |
                          REACT WEB DASHBOARD
                                    ¦
                                    |
                         FIREBASE HOSTING
                                    ¦
                                    |
                           AUTHENTICATED USER
```

---

#  Cloud Architecture

```text
User
 ¦
 |
Firebase Hosting
 ¦
 |
React Frontend
 ¦
 ¦ HTTPS REST API
 |
Render
 ¦
 |
Flask Backend
 ¦
 +--------------> Firebase Firestore
 ¦
 +--------------> Automation Engine
                         ¦
                         |
                    Virtual Pump
```

---

#  Technology Stack

| Layer                 | Technology              |
| --------------------- | ----------------------- |
| Frontend              | React.js                |
| Build Tool            | Vite                    |
| Styling               | CSS                     |
| Charts                | Recharts                |
| Backend               | Python Flask            |
| API                   | REST API                |
| Local Database        | SQLite                  |
| Cloud Database        | Firebase Firestore      |
| Authentication        | Firebase Authentication |
| Cloud Frontend        | Firebase Hosting        |
| Cloud Backend         | Render                  |
| IoT Sensor            | Python Simulator        |
| Programming Languages | Python, JavaScript      |
| Version Control       | Git & GitHub            |

---

#  Cloud Services Used

## Firebase

### Firebase Authentication

Used for:

* User login
* User authentication
* Access control

### Firebase Firestore

Used for cloud data storage.

Collections include:

```text
devices
sensor_readings
watering_events
alerts
```

### Firebase Hosting

Hosts the production React frontend.

---

## Render

Render hosts the Flask backend.

Backend URL:

```text
https://cloud-smart-plant-care.onrender.com
```

Health endpoint:

```text
/api/health
```

---

#  IoT Sensor Simulation

A Python program simulates a real IoT device.

The simulator generates:

```text
Soil Moisture
Temperature
Humidity
Light Level
```

The simulated device ID is:

```text
PLANT-001
```

The simulator sends sensor data to the backend using HTTP POST requests.

Example:

```text
Virtual Sensor
      |
HTTP POST
      |
Flask REST API
      |
Automation Engine
      |
Firestore
```

---

#  Automatic Watering Logic

The watering engine continuously evaluates soil moisture.

Example:

```text
Threshold = 35%

If:
    moisture < 35%

Then:
    Start watering

    Record watering event

    Generate alert

    Increase simulated moisture

    Stop watering
```

This demonstrates **event-driven automation**.

---

#  Database Design

## Device

Stores information about connected plants/devices.

```text
device_id
plant_name
plant_type
location
moisture_threshold
auto_water
pump_status
watering_until
last_seen
created_at
```

## Sensor Reading

```text
device_id
soil_moisture
temperature
humidity
light_level
timestamp
```

## Watering Event

```text
device_id
trigger_type
moisture_before
moisture_after
duration
timestamp
```

## Alert

```text
device_id
alert_type
level
message
status
created_at
```

---

#  REST API

| Method | Endpoint                             | Purpose                   |
| ------ | ------------------------------------ | ------------------------- |
| GET    | `/api/health`                        | Check backend health      |
| GET    | `/api/devices`                       | Get devices               |
| GET    | `/api/devices/<id>`                  | Get device                |
| POST   | `/api/sensors/data`                  | Submit sensor data        |
| GET    | `/api/devices/<id>/latest`           | Get latest sensor reading |
| GET    | `/api/devices/<id>/history`          | Get sensor history        |
| PUT    | `/api/devices/<id>/threshold`        | Update moisture threshold |
| PUT    | `/api/devices/<id>/auto-water`       | Enable/disable automation |
| POST   | `/api/devices/<id>/water`            | Start manual watering     |
| GET    | `/api/devices/<id>/watering-history` | Get watering history      |
| GET    | `/api/alerts`                        | Get alerts                |
| PUT    | `/api/alerts/<id>/acknowledge`       | Acknowledge alert         |

---

#  Project Structure

```text
Cloud-Smart-Plant-Care/
¦
+-- sensor_simulator/
¦   +-- simulator.py
¦   +-- config.py
¦
+-- backend/
¦   +-- app.py
¦   +-- models/
¦   +-- routes/
¦   +-- services/
¦   +-- utils/
¦   +-- firebase-service-account.json
¦
+-- automation/
¦   +-- watering_engine.py
¦   +-- plant_profiles.py
¦
+-- frontend/
¦   +-- src/
¦   +-- public/
¦   +-- package.json
¦   +-- vite.config.js
¦
+-- cloud/
¦   +-- database_service.py
¦   +-- auth_service.py
¦
+-- tests/
+-- sample_data/
+-- screenshots/
+-- docs/
+-- reports/
¦
+-- requirements.txt
+-- .env.example
+-- .gitignore
+-- README.md
```

> Firebase service-account credentials are excluded from GitHub using `.gitignore`.

---

#  Local Setup

## 1. Clone Repository

```bash
git clone https://github.com/vyshnaviporandla/Cloud-Smart-Plant-Care.git
cd Cloud-Smart-Plant-Care
```

## 2. Create Python Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bat
venv\Scripts\activate
```

## 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Backend

```bash
python backend\app.py
```

Backend:

```text
http://127.0.0.1:5000
```

## 5. Start Frontend

Open another Command Prompt:

```bat
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 6. Start Sensor Simulator

```bat
python sensor_simulator\simulator.py
```

---

#  Cloud Deployment

## Frontend

The React frontend is deployed using:

```text
Firebase Hosting
```

Production build:

```bash
npm run build
```

Deployment:

```bash
firebase deploy --only hosting
```

## Backend

The Flask backend is deployed on:

```text
Render
```

Start command:

```text
gunicorn --chdir backend app:app
```

## Database

Cloud data is stored using:

```text
Firebase Firestore
```

---

#  Security

The project follows basic security practices:

* Firebase Authentication for user access
* Firebase service-account credentials excluded from Git
* `.env` files excluded from Git
* API credentials are not stored in frontend source code
* Cloud credentials are managed through deployment configuration
* Firestore access is controlled using security rules

Sensitive files such as:

```text
firebase-service-account.json
.env
```

must never be committed to GitHub.

---

#  Testing

The project was tested using:

### Backend

```text
/api/health
```

### Sensor Communication

Virtual sensor successfully sends readings to the cloud backend.

### Automatic Watering

When moisture falls below the configured threshold:

```text
Automatic watering starts
```

### Dashboard

The dashboard successfully displays:

* Sensor values
* Charts
* Device status
* Pump status
* Alerts
* Watering history

### Authentication

Firebase email/password authentication was tested successfully.

### Cloud Deployment

Frontend:

```text
Firebase Hosting
```

Backend:

```text
Render
```

Database:

```text
Firebase Firestore
```

---

# Cloud Computing Concepts Demonstrated

This project demonstrates the following concepts:

### 1. Cloud Computing

Application components are deployed on cloud platforms instead of running entirely on one local computer.

### 2. SaaS

The plant monitoring dashboard is accessed through a web browser.

### 3. PaaS

Firebase Hosting and Render provide managed application hosting platforms.

### 4. Cloud Database

Firestore stores application data in the cloud.

### 5. IoT-to-Cloud Communication

Sensor data travels from the virtual IoT device to the cloud backend.

### 6. REST API

Frontend and sensor communicate with the backend through HTTP APIs.

### 7. Authentication

Firebase Authentication manages user identity.

### 8. Automation

The backend automatically triggers watering based on sensor conditions.

### 9. Event-Driven Architecture

Low soil moisture generates a watering event and alert.

### 10. Scalability

Additional plants/devices can be added without changing the basic architecture.

### 11. Availability

Cloud-hosted frontend and backend can be accessed remotely.

### 12. Monitoring

Sensor readings and system events are continuously recorded.

### 13. Deployment

The project demonstrates deployment using Firebase Hosting and Render.

### 14. Version Control

Git and GitHub are used for source-code management and proof of work.

---

#  Screenshots

Project screenshots are available in:

```text
screenshots/
```

Important screenshots include:

```text
01-login.png
02-dashboard.png
03-automatic-watering.png
04-watering-history.png
05-alerts.png
06-firestore.png
07-render-api.png
08-github.png
```

---

#  Future Enhancements

The project can be extended with:

* ESP32 physical sensors
* Real soil moisture sensors
* Real water pump and relay
* MQTT communication
* Multiple plant support
* Weather API integration
* Mobile application
* Push notifications
* Email alerts
* AI-based watering prediction
* Time-series database
* Serverless cloud functions
* Advanced analytics
* Role-based access control

---

#  Academic Value

This project demonstrates how IoT systems can be integrated with cloud computing infrastructure.

Instead of relying only on a local application, the system demonstrates:

```text
IoT
 |
Internet
 |
Cloud API
 |
Cloud Database
 |
Automation
 |
Web Application
```

It therefore provides practical exposure to modern cloud application architecture.

---

# Project Information

**Project:** Cloud Smart Plant Care

**Domain:** Cloud Computing + IoT

**Frontend:** React + Vite

**Backend:** Python Flask

**Cloud:** Firebase + Render

**Database:** Firebase Firestore

**Authentication:** Firebase Authentication

**Repository:** GitHub

---

#  License

This project was developed for educational and academic purposes.
