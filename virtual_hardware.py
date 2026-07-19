import paho.mqtt.client as mqtt
import json

# Broker settings (Same as the Next.js dashboard)
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "edge-traffic/control"

# Define what happens when we connect
def on_connect(client, userdata, flags, rc):
    print(f"🟢 Virtual ESP32 Connected to MQTT Broker!")
    print(f"🎧 Listening for commands on topic: {MQTT_TOPIC}...\n")
    client.subscribe(MQTT_TOPIC)

# Define what happens when a message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"📥 NEW MESSAGE RECEIVED")
    print(f"Raw Payload: {payload}")
    
    try:
        data = json.loads(payload)
        command = data.get("command")
        
        if command == "emergency_stop":
            print("🚨 ACTION: EMERGENCY STOP! (All Lights RED)")
        elif command == "override_phase":
            print("⚠️ ACTION: MANUAL OVERRIDE (Lights YELLOW)")
        elif command == "toggle_leds":
            print("🚦 ACTION: TOGGLED GREEN LIGHT")
        else:
            print(f"❓ Unknown command: {command}")
    except json.JSONDecodeError:
        print("❌ Could not parse JSON command.")
        
    print("-" * 40)

# Setup and run the client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Keep the script running and listening
client.loop_forever()
