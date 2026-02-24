import paho.mqtt.client as mqtt
import json
import time

print("=" * 50)
print("EMERGENCY VEHICLE APPLICATION")
print("=" * 50)


class EmergencyApp:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "EmergencyApp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.route = None
        self.emergency_active = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        _ = userdata, flags, properties
        print("Connected to smart traffic system!")
        print(f"   Connection code: {rc}")
        if rc == 0:
            client.subscribe("emergency/response")
            print("   Subscribed to emergency/response channel")
        else:
            print(f"   Connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        _ = userdata
        try:
            data = json.loads(msg.payload.decode())
            self.route = data
            self.emergency_active = True

            print("\n" + "📍" * 25)
            print("   EMERGENCY ROUTE RECEIVED FROM CENTRAL SYSTEM!")
            print("   Route:", " → ".join(data.get('path', [])))
            print("   Estimated time:", data.get('estimated_time', 'Unknown'))
            print("   Status:", data.get('status', 'Unknown'))

            if data.get('all_clear', False):
                print("   All signals on route are GREEN")

            print("📍" * 25 + "\n")

            self.simulate_emergency_movement(data.get('path', []))

        except Exception as e:
            print(f"Error receiving route: {e}")

    def simulate_emergency_movement(self, path):
        if not path:
            return

        print("Emergency vehicle movement simulation:")
        for i, intersection in enumerate(path, 1):
            print(f"   {i}. Passing through {intersection}...")
            time.sleep(2)

        print("   Destination reached successfully!")
        self.emergency_active = False

    def send_emergency_request(self, vehicle_type="Ambulance"):
        requests = {
            "Ambulance": {
                "vehicle_id": "AMB-101",
                "from": "Central Hospital",
                "to": "Accident site - SIGNAL 2",
                "priority": "High",
                "type": "Ambulance"
            },
            "Fire": {
                "vehicle_id": "FIR-202",
                "from": "Fire Station",
                "to": "Fire site - SIGNAL 3",
                "priority": "Critical",
                "type": "Fire"
            },
            "Police": {
                "vehicle_id": "POL-303",
                "from": "Police Station",
                "to": "Emergency site - SIGNAL 4",
                "priority": "Medium",
                "type": "Police"
            }
        }

        request = requests.get(vehicle_type, requests["Ambulance"])
        request['timestamp'] = time.time()

        print(f"\nSending emergency request:")
        print(f"   Vehicle: {request['vehicle_id']}")
        print(f"   From: {request['from']}")
        print(f"   To: {request['to']}")
        print(f"   Priority: {request['priority']}")

        self.client.publish("emergency/request", json.dumps(request))
        print("   Request sent to central system")

    def start(self):
        try:
            print("Connecting to MQTT Broker...")
            self.client.connect("broker.emqx.io", 1883, 60)
            self.client.loop_start()

            time.sleep(2)

            vehicles = ["Ambulance", "Fire", "Police"]
            for i, vehicle in enumerate(vehicles, 1):
                print(f"\n{'=' * 40}")
                print(f"Emergency request #{i}: {vehicle}")
                self.send_emergency_request(vehicle)
                time.sleep(10)

            print("\n" + "=" * 50)
            print("Emergency application running...")
            print("Press Ctrl+C to stop")

            while True:
                time.sleep(5)

        except KeyboardInterrupt:
            print("\nStopping emergency application")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    app = EmergencyApp()
    app.start()