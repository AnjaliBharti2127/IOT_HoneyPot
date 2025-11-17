# attacker_simulator.py
"""
Simulate attacks: publish suspicious payloads and floods.
Not malicious — only for testing your honeypot.
"""

import random
import time
from paho.mqtt import client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "AttackerSim"
TOPICS = [
    "home/fakebulb/control/power",
    "home/fakebulb/control/brightness",
    "home/sensor/temperature",
    "admin/login",
    "random/topic/{}".format(random.randint(1,100))
]

SUSPICIOUS_PAYLOADS = [
    "hack attempt",
    "password=12345",
    "admin:admin",
    "exploit code",
    "{\"cmd\":\"reboot\"}"
]

def main():
    client = mqtt.Client(CLIENT_ID)
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
    client.loop_start()
    try:
        while True:
            t = random.choice(TOPICS)
            if random.random() < 0.3:
                payload = random.choice(SUSPICIOUS_PAYLOADS)
            else:
                payload = f"normal_{random.randint(0,999)}"
            client.publish(t, payload)
            print(f"[attacker] published to {t}: {payload}")
            time.sleep(random.uniform(0.2, 2.0))
    except KeyboardInterrupt:
        print("[attacker] stopped")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
