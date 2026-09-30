from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = "devices"

    device_id = db.Column(db.String(50), primary_key=True)
    plant_name = db.Column(db.String(100), nullable=False)
    plant_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    moisture_threshold = db.Column(db.Float, default=30.0, nullable=False)

    auto_water = db.Column(db.Boolean, default=True, nullable=False)

    last_seen = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False,
        index=True
    )

    soil_moisture = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    light_level = db.Column(db.Float, nullable=True)

    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class WateringEvent(db.Model):
    __tablename__ = "watering_events"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False,
        index=True
    )

    trigger_type = db.Column(db.String(30), nullable=False)

    moisture_before = db.Column(db.Float, nullable=False)
    moisture_after = db.Column(db.Float, nullable=True)

    duration = db.Column(db.Float, nullable=False)

    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.String(50),
        db.ForeignKey("devices.device_id"),
        nullable=False,
        index=True
    )

    alert_type = db.Column(db.String(50), nullable=False)

    level = db.Column(db.String(20), nullable=False)

    message = db.Column(db.String(500), nullable=False)

    status = db.Column(db.String(20), default="OPEN", nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )