import paho.mqtt.client as mqtt
import json

class EnergyMQTTClient:
    """MQTT client to handle live energy data streams."""
    def __init__(self, topic="energy/live/data"):
        self.client = mqtt.Client()
        self.topic = topic
        self.latest_data = None

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            self.latest_data = json.loads(msg.payload.decode())
        except Exception:
            pass

    def start(self):
        """Connect to public broker and start background loop."""
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect("broker.hivemq.com", 1883, 60)
            self.client.loop_start()
        except Exception:
            print("MQTT Connection Failed")

    def get_data(self):
        """Retrieve the last received message."""
        return self.latest_data