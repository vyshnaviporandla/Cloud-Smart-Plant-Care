import sys
import os

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from cloud.database_service import (
    save_sensor_reading,
    save_watering_event,
    save_alert
)


app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plant_care.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class Device(db.Model):
    __tablename__ = "devices"

    device_id = db.Column(db.String(50), primary_key=True)
    plant_name = db.Column(db.String(100), nullable=False)
    plant_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    moisture_threshold = db.Column(db.Float, default=30.0)
    auto_water = db.Column(db.Boolean, default=True)

    pump_status = db.Column(db.Boolean, default=False)
    watering_until = db.Column(db.DateTime, nullable=True)

    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False
    )

    soil_moisture = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    light_level = db.Column(db.Float, nullable=False)

    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class WateringEvent(db.Model):
    __tablename__ = "watering_events"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False
    )

    trigger_type = db.Column(db.String(30), nullable=False)
    moisture_before = db.Column(db.Float, nullable=False)
    moisture_after = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)

    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False
    )

    alert_type = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), default="WARNING")
    message = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="OPEN")

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# HELPERS
# ============================================================

def now_utc():
    return datetime.utcnow()


def device_to_dict(device):
    return {
        "device_id": device.device_id,
        "plant_name": device.plant_name,
        "plant_type": device.plant_type,
        "location": device.location,
        "moisture_threshold": device.moisture_threshold,
        "auto_water": device.auto_water,
        "pump_status": device.pump_status,
        "last_seen": (
            device.last_seen.isoformat()
            if device.last_seen else None
        ),
        "created_at": (
            device.created_at.isoformat()
            if device.created_at else None
        )
    }


def reading_to_dict(reading):
    return {
        "id": reading.id,
        "device_id": reading.device_id,
        "soil_moisture": reading.soil_moisture,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "light_level": reading.light_level,
        "timestamp": reading.timestamp.isoformat()
    }


def watering_to_dict(event):
    return {
        "id": event.id,
        "device_id": event.device_id,
        "trigger_type": event.trigger_type,
        "moisture_before": event.moisture_before,
        "moisture_after": event.moisture_after,
        "duration": event.duration,
        "timestamp": event.timestamp.isoformat()
    }


def alert_to_dict(alert):
    return {
        "id": alert.id,
        "device_id": alert.device_id,
        "alert_type": alert.alert_type,
        "level": alert.level,
        "message": alert.message,
        "status": alert.status,
        "created_at": alert.created_at.isoformat()
    }


# ============================================================
# INITIAL DATABASE SETUP
# ============================================================

with app.app_context():

    db.create_all()

    device = Device.query.filter_by(
        device_id="PLANT-001"
    ).first()

    if not device:
        device = Device(
            device_id="PLANT-001",
            plant_name="Tomato Plant",
            plant_type="TOMATO",
            location="Demo Greenhouse",
            moisture_threshold=30.0,
            auto_water=True,
            pump_status=False
        )

        db.session.add(device)
        db.session.commit()

        print("Demo device PLANT-001 created.")


# ============================================================
# BASIC ROUTES
# ============================================================

@app.route("/")
def home():
    return jsonify({
        "service": "Cloud Smart Plant Care",
        "status": "running"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "service": "cloud-smart-plant-care-backend",
        "status": "healthy"
    })


# ============================================================
# DEVICES
# ============================================================

@app.route("/api/devices", methods=["GET"])
def get_devices():

    devices = Device.query.all()

    return jsonify([
        device_to_dict(device)
        for device in devices
    ])


@app.route("/api/devices/<device_id>", methods=["GET"])
def get_device(device_id):

    device = Device.query.get(device_id)

    if not device:
        return jsonify({
            "error": "Device not found"
        }), 404

    return jsonify(device_to_dict(device))


# ============================================================
# SENSOR DATA + AUTOMATIC WATERING
# ============================================================

@app.route("/api/sensors/data", methods=["POST"])
def receive_sensor_data():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data required"
        }), 400

    device_id = data.get("device_id")

    if not device_id:
        return jsonify({
            "error": "device_id is required"
        }), 400

    device = Device.query.get(device_id)

    if not device:
        return jsonify({
            "error": "Device not found"
        }), 404

    try:
        soil_moisture = float(data.get("soil_moisture"))
        temperature = float(data.get("temperature"))
        humidity = float(data.get("humidity"))
        light_level = float(data.get("light_level"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "Sensor values must be numbers"
        }), 400

    if not 0 <= soil_moisture <= 100:
        return jsonify({
            "error": "soil_moisture must be between 0 and 100"
        }), 400

    if not -20 <= temperature <= 60:
        return jsonify({
            "error": "temperature must be between -20 and 60"
        }), 400

    if not 0 <= humidity <= 100:
        return jsonify({
            "error": "humidity must be between 0 and 100"
        }), 400

    if not 0 <= light_level <= 100:
        return jsonify({
            "error": "light_level must be between 0 and 100"
        }), 400

    current_time = now_utc()

    # --------------------------------------------------------
    # Save sensor reading
    # --------------------------------------------------------

    reading = SensorReading(
        device_id=device_id,
        soil_moisture=soil_moisture,
        temperature=temperature,
        humidity=humidity,
        light_level=light_level,
        timestamp=current_time
    )

    db.session.add(reading)

    device.last_seen = current_time

    save_sensor_reading(
        device_id=device_id,
        soil_moisture=soil_moisture,
        temperature=temperature,
        humidity=humidity,
        light_level=light_level
    )

    # --------------------------------------------------------
    # Check whether existing watering cycle is finished
    # --------------------------------------------------------

    watering_triggered = False

    if device.pump_status:

        if (
            device.watering_until
            and current_time >= device.watering_until
        ):
            device.pump_status = False
            device.watering_until = None

    # --------------------------------------------------------
    # Automatic watering decision
    # --------------------------------------------------------

    if (
        device.auto_water
        and not device.pump_status
        and soil_moisture < device.moisture_threshold
    ):

        device.pump_status = True

        # Virtual watering duration
        device.watering_until = (
            current_time + timedelta(seconds=30)
        )

        watering_triggered = True

        # Create watering event
        event = WateringEvent(
            device_id=device_id,
            trigger_type="AUTOMATIC",
            moisture_before=soil_moisture,
            moisture_after=min(
                soil_moisture + 15,
                100
            ),
            duration=30.0,
            timestamp=current_time
        )

        db.session.add(event)

        # Create alert
        alert = Alert(
            device_id=device_id,
            alert_type="LOW_SOIL_MOISTURE",
            level="WARNING",
            message=(
                f"Low soil moisture detected: "
                f"{soil_moisture:.1f}%. "
                f"Automatic watering started."
            ),
            status="OPEN",
            created_at=current_time
        )

        db.session.add(alert)

        # Save watering event to Firestore
        save_watering_event(
            device_id=device_id,
            trigger_type="AUTOMATIC",
            moisture_before=soil_moisture,
            moisture_after=min(
                soil_moisture + 15,
                100
            ),
            duration=30.0
        )

        # Save alert to Firestore
        save_alert(
            device_id=device_id,
            alert_type="LOW_SOIL_MOISTURE",
            level="WARNING",
            message=(
                f"Low soil moisture detected: "
                f"{soil_moisture:.1f}%. "
                f"Automatic watering started."
            )
        )
    db.session.commit()

    return jsonify({
        "message": "Sensor data received",
        "device_id": device_id,
        "watering_triggered": watering_triggered,
        "watering_active": device.pump_status,
        "pump_status": device.pump_status,
        "soil_moisture": soil_moisture,
        "moisture_threshold": device.moisture_threshold
    }), 201


# ============================================================
# LATEST SENSOR READING
# ============================================================

@app.route("/api/devices/<device_id>/latest", methods=["GET"])
def latest_reading(device_id):

    reading = (
        SensorReading.query
        .filter_by(device_id=device_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if not reading:
        return jsonify({
            "error": "No sensor readings found"
        }), 404

    return jsonify(reading_to_dict(reading))


# ============================================================
# SENSOR HISTORY
# ============================================================

@app.route("/api/devices/<device_id>/history", methods=["GET"])
def sensor_history(device_id):

    readings = (
        SensorReading.query
        .filter_by(device_id=device_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(100)
        .all()
    )

    return jsonify([
        reading_to_dict(reading)
        for reading in reversed(readings)
    ])


# ============================================================
# CHANGE MOISTURE THRESHOLD
# ============================================================

@app.route("/api/devices/<device_id>/threshold", methods=["PUT"])
def update_threshold(device_id):

    device = Device.query.get(device_id)

    if not device:
        return jsonify({
            "error": "Device not found"
        }), 404

    data = request.get_json() or {}

    try:
        threshold = float(data.get("threshold"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "threshold must be a number"
        }), 400

    if not 0 <= threshold <= 100:
        return jsonify({
            "error": "threshold must be between 0 and 100"
        }), 400

    device.moisture_threshold = threshold

    db.session.commit()

    return jsonify({
        "message": "Threshold updated",
        "threshold": threshold
    })


# ============================================================
# AUTO WATERING ON/OFF
# ============================================================

@app.route("/api/devices/<device_id>/auto-water", methods=["PUT"])
def update_auto_water(device_id):

    device = Device.query.get(device_id)

    if not device:
        return jsonify({
            "error": "Device not found"
        }), 404

    data = request.get_json() or {}

    enabled = data.get("enabled")

    if not isinstance(enabled, bool):
        return jsonify({
            "error": "enabled must be true or false"
        }), 400

    device.auto_water = enabled

    db.session.commit()

    return jsonify({
        "message": "Automatic watering updated",
        "auto_water": enabled
    })


# ============================================================
# MANUAL WATERING
# ============================================================

@app.route("/api/devices/<device_id>/water", methods=["POST"])
def manual_water(device_id):
    device = Device.query.get(device_id)

    if not device:
        return jsonify({"message": "Device not found"}), 404

    current_time = now_utc()

    latest_reading = (
        SensorReading.query
        .filter_by(device_id=device_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if latest_reading:
        moisture_before = latest_reading.soil_moisture
        moisture_after = min(moisture_before + 15, 100)
    else:
        moisture_before = 0.0
        moisture_after = 15.0

    device.pump_status = True
    device.watering_until = current_time + timedelta(seconds=30)

    event = WateringEvent(
        device_id=device_id,
        trigger_type="MANUAL",
        moisture_before=moisture_before,
        moisture_after=moisture_after,
        duration=30.0,
        timestamp=current_time
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "Manual watering started",
        "device_id": device_id,
        "pump_status": True,
        "moisture_before": moisture_before,
        "moisture_after": moisture_after,
        "duration": 30
    }), 200


# ============================================================
# WATERING HISTORY
# ============================================================

@app.route("/api/devices/<device_id>/watering-history", methods=["GET"])
def watering_history(device_id):

    events = (
        WateringEvent.query
        .filter_by(device_id=device_id)
        .order_by(WateringEvent.timestamp.desc())
        .limit(50)
        .all()
    )

    return jsonify([
        watering_to_dict(event)
        for event in events
    ])


# ============================================================
# ALERTS
# ============================================================

@app.route("/api/alerts", methods=["GET"])
def get_alerts():

    alerts = (
        Alert.query
        .order_by(Alert.created_at.desc())
        .limit(50)
        .all()
    )

    return jsonify([
        alert_to_dict(alert)
        for alert in alerts
    ])


@app.route("/api/alerts/<int:alert_id>/acknowledge", methods=["PUT"])
def acknowledge_alert(alert_id):

    alert = Alert.query.get(alert_id)

    if not alert:
        return jsonify({
            "error": "Alert not found"
        }), 404

    alert.status = "ACKNOWLEDGED"

    db.session.commit()

    return jsonify({
        "message": "Alert acknowledged"
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )