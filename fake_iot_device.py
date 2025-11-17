# device_simulator.py
"""
Fake IoT device simulator (ESP32-like behavior).
Publishes status and subscribes to control commands.
"""

import time
import json
import socket
from paho.mqtt import client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "FakeSmartBulb-001"
STATUS_TOPIC = "home/fakebulb/status"
CONTROL_TOPIC = "home/fakebulb/control/#"

def on_connect(client, userdata, flags, rc):
    print(f"[device] connected to broker (rc={rc})")
    client.subscribe(CONTROL_TOPIC)
    print(f"[device] subscribed to {CONTROL_TOPIC}")

def on_message(client, userdata, msg):
    print(f"[device] received on {msg.topic}: {msg.payload.decode(errors='ignore')}")
    # Simulate acting on control command:
    if msg.topic.endswith("/power"):
        payload = msg.payload.decode(errors='ignore').lower()
        if "on" in payload:
            print("[device] turning ON")
        elif "off" in payload:
            print("[device] turning OFF")

def make_status():
    # Example status payload the device periodically publishes
    return {
        "client_id": CLIENT_ID,
        "uptime": int(time.time()),
        "status": "ok",
        "brightness": 75
    }

def main():
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    # If you enabled auth on Mosquitto, set username/password here:
    # client.username_pw_set("user", "pass")

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            payload = json.dumps(make_status())
            client.publish(STATUS_TOPIC, payload, qos=0, retain=False)
            print(f"[device] published status to {STATUS_TOPIC}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("[device] stopping")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
