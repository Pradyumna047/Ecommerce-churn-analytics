import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

# ── Configuration ─────────────────────────────────────────────────────────────
KAFKA_BROKER = "localhost:9092"
TOPIC        = "iot_sensor_readings"
INTERVAL_SEC = 1.0

# ── Sensor definitions ────────────────────────────────────────────────────────
SENSORS = [
    {"sensor_id": "S001", "location": "Warehouse-A",   "type": "Temperature"},
    {"sensor_id": "S002", "location": "Warehouse-B",   "type": "Temperature"},
    {"sensor_id": "S003", "location": "Factory-Floor", "type": "Temperature"},
    {"sensor_id": "S004", "location": "Cold-Storage",  "type": "Temperature"},
    {"sensor_id": "S005", "location": "Office-Block",  "type": "Temperature"},
    {"sensor_id": "P001", "location": "Pipeline-1",    "type": "Pressure"},
    {"sensor_id": "P002", "location": "Pipeline-2",    "type": "Pressure"},
    {"sensor_id": "H001", "location": "Warehouse-A",   "type": "Humidity"},
    {"sensor_id": "H002", "location": "Factory-Floor", "type": "Humidity"},
    {"sensor_id": "V001", "location": "Turbine-1",     "type": "Vibration"},
]

BASELINE = {
    "Temperature": {"min": 15.0, "max": 35.0, "unit": "Celsius",  "anomaly_threshold": 40.0},
    "Pressure":    {"min": 1.0,  "max": 5.0,  "unit": "Bar",      "anomaly_threshold": 6.5},
    "Humidity":    {"min": 30.0, "max": 70.0, "unit": "Percent",  "anomaly_threshold": 85.0},
    "Vibration":   {"min": 0.1,  "max": 2.0,  "unit": "mm/s",     "anomaly_threshold": 3.5},
}

def delivery_report(err, msg):
    """Called once per message to confirm delivery."""
    if err:
        print(f"  ✗ Delivery failed: {err}")

def generate_reading(sensor):
    b          = BASELINE[sensor["type"]]
    is_anomaly = random.random() < 0.05
    if is_anomaly:
        value  = round(b["anomaly_threshold"] + random.uniform(0.5, 3.0), 2)
        status = "ANOMALY"
    else:
        value  = round(random.uniform(b["min"], b["max"]), 2)
        status = "NORMAL"

    return {
        "event_id"       : f"{sensor['sensor_id']}_{int(time.time() * 1000)}",
        "sensor_id"      : sensor["sensor_id"],
        "location"       : sensor["location"],
        "sensor_type"    : sensor["type"],
        "value"          : value,
        "unit"           : b["unit"],
        "status"         : status,
        "is_anomaly"     : is_anomaly,
        "threshold"      : b["anomaly_threshold"],
        "timestamp"      : datetime.utcnow().isoformat() + "Z",
        "ingestion_time" : datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    print(f"Connecting to Kafka broker : {KAFKA_BROKER}")
    print(f"Topic                      : {TOPIC}")
    print(f"Sensors                    : {len(SENSORS)}")
    print(f"Interval                   : {INTERVAL_SEC}s")
    print("-" * 50)

    producer = Producer({
        "bootstrap.servers": KAFKA_BROKER,
        "acks"             : "all",
        "retries"          : 3,
        "linger.ms"        : 5,
    })

    messages_sent = 0

    try:
        while True:
            for sensor in SENSORS:
                reading = generate_reading(sensor)

                producer.produce(
                    topic=TOPIC,
                    key=reading["sensor_id"],
                    value=json.dumps(reading).encode("utf-8"),
                    callback=delivery_report
                )
                messages_sent += 1

                if reading["is_anomaly"]:
                    print(f"  ⚠ ANOMALY: {reading['sensor_id']} "
                          f"({reading['sensor_type']}) = "
                          f"{reading['value']} {reading['unit']}")

            producer.poll(0)
            producer.flush()

            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] "
                  f"Sent {len(SENSORS)} readings | "
                  f"Total: {messages_sent:,}")

            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        print(f"\nProducer stopped. Total sent: {messages_sent:,}")
        producer.flush()

if __name__ == "__main__":
    main()