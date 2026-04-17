"""
Simple MQTT client using HiveMQ public broker.
Includes simulator for testing.
"""

import random
import time
from typing import Dict

import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"
PORT = 1883

TOPICS = [
    "energy/solar",
    "energy/wind",
    "energy/demand",
]

_latest_data: Dict[str, float] = {
    "solar": 0.0,
    "wind": 0.0,
    "demand": 0.0,
}


def _on_connect(client, userdata, flags, rc):
    for topic in TOPICS:
        client.subscribe(topic)


def _on_message(client, userdata, msg):
    key = msg.topic.split("/")[-1]
    try:
        _latest_data[key] = float(msg.payload.decode())
    except Exception:
        pass


def create_client() -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(BROKER, PORT, 60)
    except Exception:
        pass

    return client


def start_client(client: mqtt.Client):
    try:
        client.loop_start()
    except Exception:
        pass


def simulate_sensor_data(client: mqtt.Client):
    """
    Publish fake sensor values every second.
    """
    while True:
        try:
            client.publish("energy/solar", random.uniform(0, 80))
            client.publish("energy/wind", random.uniform(0, 50))
            client.publish("energy/demand", random.uniform(40, 120))
            time.sleep(1)
        except Exception:
            break


def get_latest_data() -> Dict[str, float]:
    return _latest_data.copy()