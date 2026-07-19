import time
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "edge-traffic/control"

print("Connecting Simulator to MQTT Broker...")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

print("✅ Connected! Starting AI Traffic Simulation...\n")

vehicle_count = 0

try:
    while True:
        # Simulate traffic building up at a red light
        vehicle_count += 1
        print(f"📷 AI detects {vehicle_count} vehicles waiting...")
        
        # The exact automation trigger from our main code
        if vehicle_count >= 3:
            print(f"⚠️ DENSITY THRESHOLD MET! Automatically clearing intersection...")
            
            payload = json.dumps({
                "command": "toggle_leds", 
                "timestamp": int(time.time() * 1000),
                "trigger": "AI_AUTO_SIMULATION"
            })
            
            client.publish(MQTT_TOPIC, payload)
            print("🟢 Command published. Waiting for traffic to clear...")
            
            # Reset traffic after green light
            time.sleep(2)
            vehicle_count = 0
            print("-" * 40)
            
        time.sleep(2) # New frame every 2 seconds
        
except KeyboardInterrupt:
    print("\nSimulation stopped.")
    client.loop_stop()
