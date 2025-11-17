import paho.mqtt.client as mqtt
import time
import json

BROKER = "localhost"
PORT = 1883

DEVICE_ID = "smart_bulb_01"
TOPIC_DATA = f"honeypot/device/{DEVICE_ID}/data"
TOPIC_CONTROL = f"honeypot/device/{DEVICE_ID}/control"

def on_connect(client, userdata, flags, rc):
    print("[DEVICE] Connected to broker with code:", rc)
    client.subscribe(TOPIC_CONTROL)

def on_message(client, userdata, msg):
    print("[DEVICE] Received control message:", msg.payload.decode())

def main():
    client = mqtt.Client(client_id=DEVICE_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while True:
        bulb_status = {
            "device": DEVICE_ID,
            "status": "ON",
            "brightness": 80,
            "temperature": 25.4
        }
        client.publish(TOPIC_DATA, json.dumps(bulb_status))
        print("[DEVICE] Published data:", bulb_status)
        time.sleep(5)

if __name__ == "__main__":
    main()
