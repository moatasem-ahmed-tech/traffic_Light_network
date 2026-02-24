import paho.mqtt.client as mqtt
import json
import time
import threading
from ai_model import TrafficAIModel

print("=" * 60)
print("SMART TRAFFIC SYSTEM WITH AI - 4 SIGNALS")
print("USING RANDOM FOREST MODEL")
print("SIGNAL SEQUENCE: RED -> YELLOW -> GREEN")
print("=" * 60)


class SmartTrafficSystemWithAI:
    def __init__(self):
        print("LOADING AI MODEL...")
        self.ai_model = TrafficAIModel("traffic_ai_model.pkl")
        print("AI MODEL READY")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "TrafficMasterAI")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # 4 traffic signals with different lane counts
        self.intersections = {
            "intersection1": {
                "id": "intersection1",
                "name": "SIGNAL 1",
                "density": 0,
                "lanes": 2,
                "status": "red",
                "green_time": 30,
                "waiting_time": 0,
                "priority": 0
            },
            "intersection2": {
                "id": "intersection2",
                "name": "SIGNAL 2",
                "density": 0,
                "lanes": 3,
                "status": "red",
                "green_time": 30,
                "waiting_time": 0,
                "priority": 0
            },
            "intersection3": {
                "id": "intersection3",
                "name": "SIGNAL 3",
                "density": 0,
                "lanes": 1,
                "status": "red",
                "green_time": 30,
                "waiting_time": 0,
                "priority": 0
            },
            "intersection4": {
                "id": "intersection4",
                "name": "SIGNAL 4",
                "density": 0,
                "lanes": 2,
                "status": "red",
                "green_time": 30,
                "waiting_time": 0,
                "priority": 0
            }
        }

        self.current_green = None
        self.system_active = True

        # Start automatic control cycle
        self.control_thread = threading.Thread(target=self.traffic_control_cycle)
        self.control_thread.daemon = True
        self.control_thread.start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        _ = userdata, flags, properties
        if rc == 0:
            print("CONNECTED TO MQTT BROKER")
        else:
            print(f"CONNECTION FAILED - CODE: {rc}")

        print("SUBSCRIBING TO ALL SIGNAL CHANNELS...")

        for intersection in self.intersections.values():
            client.subscribe(f"traffic/{intersection['id']}/density")
            client.subscribe(f"traffic/{intersection['id']}/status")

        client.subscribe("emergency/request")
        print("SUBSCRIBED TO 8 SIGNAL CHANNELS + EMERGENCY CHANNEL")

    def on_message(self, client, userdata, msg):
        _ = client, userdata
        topic = msg.topic
        payload = msg.payload.decode()

        if "density" in topic:
            signal_id = topic.split("/")[1]

            for key, intersection in self.intersections.items():
                if intersection["id"] == signal_id:
                    try:
                        data = json.loads(payload)
                        density = data.get("value", 0)
                        old_density = intersection["density"]
                        intersection["density"] = density
                        intersection["waiting_time"] += 3

                        print(f"{intersection['name']}: {old_density} -> {density} cars")

                        # Use AI model to predict green time
                        ai_green_time = self.ai_model.predict_green_time(
                            Q_queue=density,
                            lanes=intersection["lanes"],
                            t_lost=3.0
                        )

                        intersection["green_time"] = ai_green_time

                        # Calculate priority (density + waiting time)
                        priority = (density * 2) + (intersection["waiting_time"] * 0.5)
                        intersection["priority"] = priority

                        print(f"   AI suggests: {ai_green_time} sec")
                        print(f"   Priority: {priority:.1f} | Waiting: {intersection['waiting_time']}s")

                    except Exception as e:
                        print(f"ERROR in {signal_id} data: {e}")
                    break

        elif "emergency/request" in topic:
            print("\n" + "🚑" * 15)
            print("           EMERGENCY REQUEST RECEIVED!")
            print("🚑" * 15)

            try:
                data = json.loads(payload)
                vehicle = data.get("vehicle_id", "Emergency vehicle")
                from_loc = data.get("from", "Unknown")
                to_loc = data.get("to", "Unknown")

                print(f"\n   Vehicle: {vehicle}")
                print(f"   From: {from_loc}")
                print(f"   To: {to_loc}")
                print(f"   Activating green route...")

                self.activate_emergency_route(data)

            except Exception as e:
                print(f"ERROR in emergency request: {e}")

    def activate_emergency_route(self, emergency_data):
        route = ["intersection1", "intersection2", "intersection3", "intersection4"]

        for signal_id in route:
            command = {
                "command": "emergency_green",
                "duration": 10,
                "vehicle": emergency_data.get("vehicle_id", "Emergency"),
                "message": "Emergency priority - Clear route"
            }
            self.client.publish(f"traffic/{signal_id}/control", json.dumps(command))
            print(f"   Activating emergency green for {signal_id}")

        response = {
            "path": route,
            "estimated_time": "3 minutes",
            "status": "emergency_active",
            "all_clear": True,
            "timestamp": time.time()
        }
        self.client.publish("emergency/response", json.dumps(response))
        print(f"   Emergency route sent: {route}")

    def traffic_control_cycle(self):
        print("\nSTARTING AI CONTROL CYCLE...")

        while self.system_active:
            try:
                next_signal = self.select_next_signal()

                if next_signal:
                    if self.current_green:
                        self.close_current_signal()

                    self.open_signal(next_signal)
                    time.sleep(self.intersections[next_signal]["green_time"])

                time.sleep(1)

            except Exception as e:
                print(f"ERROR in control cycle: {e}")
                time.sleep(5)

    def select_next_signal(self):
        candidates = []

        for key, intersection in self.intersections.items():
            if intersection["status"] != "green":
                score = intersection["priority"]
                candidates.append((key, score, intersection))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        selected = candidates[0][0]

        print(f"\nSELECTING NEXT SIGNAL: {self.intersections[selected]['name']}")
        print(f"   Density: {self.intersections[selected]['density']} cars")
        print(f"   AI suggested time: {self.intersections[selected]['green_time']} sec")

        return selected

    def close_current_signal(self):
        if self.current_green:
            intersection = self.intersections[self.current_green]

            print(f"\n{intersection['name']}: Changing to YELLOW (5 seconds)...")
            yellow_command = {
                "command": "yellow",
                "duration": 5,
                "message": "Prepare to stop"
            }
            self.client.publish(f"traffic/{intersection['id']}/control", json.dumps(yellow_command))
            intersection["status"] = "yellow"

            time.sleep(5)

            print(f"{intersection['name']}: Changing to RED")
            red_command = {
                "command": "red",
                "message": "Stop"
            }
            self.client.publish(f"traffic/{intersection['id']}/control", json.dumps(red_command))
            intersection["status"] = "red"
            intersection["waiting_time"] = 0
            self.current_green = None

    def open_signal(self, signal_key):
        intersection = self.intersections[signal_key]

        print(f"\n{intersection['name']}: OPENING SIGNAL")
        print(f"   Green time: {intersection['green_time']} sec (AI calculated)")
        print(f"   Cars waiting: {intersection['density']}")

        green_command = {
            "command": "green",
            "duration": intersection["green_time"],
            "density": intersection["density"],
            "message": "Open - Safe passage (AI)"
        }
        self.client.publish(f"traffic/{intersection['id']}/control", json.dumps(green_command))
        intersection["status"] = "green"
        self.current_green = signal_key

        self.notify_other_signals(signal_key)

    def notify_other_signals(self, current_signal):
        for key, intersection in self.intersections.items():
            if key != current_signal and intersection["status"] != "red":
                stop_command = {
                    "command": "stop",
                    "reason": f"{self.intersections[current_signal]['name']} is active",
                    "duration": self.intersections[current_signal]["green_time"]
                }
                self.client.publish(f"traffic/{intersection['id']}/control", json.dumps(stop_command))
                print(f"   Temporary stop for {intersection['name']}")

    def start(self):
        try:
            print("CONNECTING TO MQTT BROKER...")
            self.client.connect("broker.emqx.io", 1883, 60)
            print("CONNECTION SUCCESSFUL!")

            print("\nSYSTEM INFORMATION:")
            print(f"   • Number of signals: 4")
            print(f"   • Signal names: SIGNAL 1, SIGNAL 2, SIGNAL 3, SIGNAL 4")
            print(f"   • Lane counts: 2,3,1,2 lanes")
            print(f"   • Model: Random Forest Regressor (trained on 5000 samples)")
            print(f"   • Inputs: car count + number of lanes")
            print("\nSTARTING AI CONTROL...")

            self.client.loop_forever()

        except Exception as e:
            print(f"CONNECTION FAILED: {e}")


if __name__ == "__main__":
    system = SmartTrafficSystemWithAI()
    system.start()