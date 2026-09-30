import os
import json

import firebase_admin
from firebase_admin import credentials, firestore


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def initialize_firebase():
    """
    Initialize Firebase using:
    1. FIREBASE_SERVICE_ACCOUNT environment variable
    2. Render Secret File
    3. Local service-account JSON file
    """

    if firebase_admin._apps:
        return firestore.client()

    service_account_json = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT"
    )

    if service_account_json:
        service_account_info = json.loads(
            service_account_json
        )

        cred = credentials.Certificate(
            service_account_info
        )

    else:
        render_secret_path = os.path.join(
            "/etc/secrets",
            "firebase-service-account.json"
        )

        if os.path.exists(render_secret_path):
            service_account_path = render_secret_path

        else:
            service_account_path = os.path.join(
                BASE_DIR,
                "backend",
                "firebase-service-account.json"
            )

        cred = credentials.Certificate(
            service_account_path
        )

    firebase_admin.initialize_app(cred)

    return firestore.client()


cloud_db = initialize_firebase()


def save_sensor_reading(
    device_id,
    soil_moisture,
    temperature,
    humidity,
    light_level
):
    data = {
        "device_id": device_id,
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity,
        "light_level": light_level,
        "timestamp": firestore.SERVER_TIMESTAMP
    }

    cloud_db.collection(
        "sensor_readings"
    ).add(data)


def save_watering_event(
    device_id,
    trigger_type,
    moisture_before,
    moisture_after,
    duration
):
    data = {
        "device_id": device_id,
        "trigger_type": trigger_type,
        "moisture_before": moisture_before,
        "moisture_after": moisture_after,
        "duration": duration,
        "timestamp": firestore.SERVER_TIMESTAMP
    }

    cloud_db.collection(
        "watering_events"
    ).add(data)


def save_alert(
    device_id,
    alert_type,
    level,
    message
):
    data = {
        "device_id": device_id,
        "alert_type": alert_type,
        "level": level,
        "message": message,
        "status": "ACTIVE",
        "created_at": firestore.SERVER_TIMESTAMP
    }

    cloud_db.collection(
        "alerts"
    ).add(data)


def save_device(device_id, device_data):
    cloud_db.collection(
        "devices"
    ).document(device_id).set(
        device_data,
        merge=True
    )