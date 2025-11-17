import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("[MONITOR] Connected with result code", rc)
    client.subscribe("door/lock/#")  # Subscribe ONLY to door lock topics

def on_message(client, userdata, msg):
    print(f"[MONITOR] {msg.topic} -> {msg.payload.decode()}")

client = mqtt.Client("monitor_console")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
