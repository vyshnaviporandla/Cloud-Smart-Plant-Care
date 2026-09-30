import time
import random
import logging
from datetime import datetime

import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:5000/api/sensors/data"
DEVICE_ID = "PLANT-001"

SEND_INTERVAL = 5


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# VIRTUAL SENSOR VALUES
# ============================================================

soil_moisture = 55.0
temperature = 29.0
humidity = 61.0
light_level = 70.0

pump_on = False


# ============================================================
# HELPER
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# ============================================================
# TEMPERATURE
# ============================================================

def update_temperature():

    global temperature

    temperature += random.uniform(-0.5, 0.5)

    temperature = clamp(
        temperature,
        20.0,
        38.0
    )


# ============================================================
# HUMIDITY
# ============================================================

def update_humidity():

    global humidity

    humidity += random.uniform(-1.5, 1.5)

    humidity = clamp(
        humidity,
        35.0,
        90.0
    )


# ============================================================
# LIGHT
# ============================================================

def update_light():

    global light_level

    hour = datetime.now().hour

    if 6 <= hour < 18:

        target = random.uniform(
            60.0,
            100.0
        )

    else:

        target = random.uniform(
            0.0,
            20.0
        )

    light_level += (
        target - light_level
    ) * 0.2

    light_level = clamp(
        light_level,
        0.0,
        100.0
    )


# ============================================================
# SOIL MOISTURE
# ============================================================

def update_soil_moisture():

    global soil_moisture

    if pump_on:

        # Virtual pump adds water
        soil_moisture += random.uniform(
            3.0,
            5.0
        )

    else:

        # Plant consumes water
        soil_moisture -= random.uniform(
            0.8,
            1.5
        )

    soil_moisture = clamp(
        soil_moisture,
        0.0,
        100.0
    )


# ============================================================
# CREATE SENSOR DATA
# ============================================================

def create_sensor_data():

    update_temperature()
    update_humidity()
    update_light()
    update_soil_moisture()

    return {
        "device_id": DEVICE_ID,
        "soil_moisture": round(
            soil_moisture,
            2
        ),
        "temperature": round(
            temperature,
            2
        ),
        "humidity": round(
            humidity,
            2
        ),
        "light_level": round(
            light_level,
            2
        ),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================
# SEND DATA TO CLOUD/BACKEND
# ============================================================

def send_sensor_data(data):

    global pump_on

    try:

        response = requests.post(
            API_URL,
            json=data,
            timeout=5
        )

        if response.status_code == 201:

            result = response.json()

            watering_triggered = result.get(
                "watering_triggered",
                False
            )

            watering_active = result.get(
                "watering_active",
                False
            )

            # Backend has started automatic watering
            if watering_triggered:

                pump_on = True

                logger.info(
                    "VIRTUAL PUMP ON - "
                    "Automatic watering started"
                )

            # Backend says watering has finished
            elif not watering_active:

                if pump_on:

                    logger.info(
                        "VIRTUAL PUMP OFF - "
                        "Watering completed"
                    )

                pump_on = False

            logger.info(
                "DATA SENT | "
                f"Soil={soil_moisture:.1f}% | "
                f"Temp={temperature:.1f}C | "
                f"Humidity={humidity:.1f}% | "
                f"Light={light_level:.1f}% | "
                f"Watering={pump_on}"
            )

        else:

            logger.error(
                f"SERVER ERROR | "
                f"Status={response.status_code}"
            )

    except requests.exceptions.ConnectionError:

        logger.error(
            "BACKEND CONNECTION ERROR - "
            "Make sure Flask server is running."
        )

    except requests.exceptions.Timeout:

        logger.error(
            "REQUEST TIMEOUT"
        )

    except requests.exceptions.RequestException as error:

        logger.error(
            f"REQUEST ERROR: {error}"
        )


# ============================================================
# MAIN SIMULATOR
# ============================================================

def main():

    logger.info("=" * 60)
    logger.info(
        "CLOUD SMART PLANT CARE - VIRTUAL SENSOR"
    )
    logger.info(
        f"Device ID: {DEVICE_ID}"
    )
    logger.info(
        f"Sending interval: {SEND_INTERVAL} seconds"
    )
    logger.info("=" * 60)

    while True:

        data = create_sensor_data()

        send_sensor_data(data)

        time.sleep(SEND_INTERVAL)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        logger.info(
            "Sensor simulator stopped by user."
        )