import paho.mqtt.client as mqtt
import json
import random
import time
import sys

# Auto-detect signal ID and name
if len(sys.argv) >= 3:
    signal_id = sys.argv[1]
    signal_name = sys.argv[2]
elif len(sys.argv) == 2:
    signal_id = sys.argv[1]
    names = {
        "intersection1": "SIGNAL 1",
        "intersection2": "SIGNAL 2",
        "intersection3": "SIGNAL 3",
        "intersection4": "SIGNAL 4"
    }
    signal_name = names.get(signal_id, f"SIGNAL {signal_id[-1]}")
else:
    signal_id = "intersection1"
    signal_name = "SIGNAL 1"

print("=" * 60)
print(f"{signal_name}")
print(f"ID: {signal_id}")
print("=" * 60)


class AdvancedTrafficSignal:
    def __init__(self, signal_id, signal_name):
        self.signal_id = signal_id
        self.signal_name = signal_name
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, signal_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.status = "red"
        self.density = random.randint(2, 35)
        self.green_time = 30
        self.yellow_time = 5
        self.cars_passed = 0
        self.total_waiting = 0

        self.start_traffic_simulation()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        _ = userdata, flags, properties
        print(f"{self.signal_name}: Connected to central system")
        print(f"   ID: {self.signal_id}")
        print(f"   Initial density: {self.density} cars")

        if rc == 0:
            client.subscribe(f"traffic/{self.signal_id}/control")
            self.send_status_update()
        else:
            print(f"   Connection failed - code: {rc}")

    def on_message(self, client, userdata, msg):
        _ = userdata
        try:
            data = json.loads(msg.payload.decode())
            command = data.get("command")

            print(f"{self.signal_name}: Command '{command}' received")

            if command == "green":
                self.activate_green(data)
            elif command == "yellow":
                self.activate_yellow(data)
            elif command == "red":
                self.activate_red(data)
            elif command == "stop":
                self.handle_stop(data)
            elif command == "emergency_green":
                self.activate_emergency(data)

        except Exception as e:
            print(f"{self.signal_name}: Error in command - {e}")

    def activate_green(self, data):
        if self.status != "green":
            self.status = "green"
            self.green_time = data.get("duration", 30)
            density = data.get("density", self.density)
            message = data.get("message", "Open")

            print(f"\n{'🟢' * 10}")
            print(f"   {self.signal_name}: 🟢 GREEN")
            print(f"   Duration: {self.green_time} sec (AI based)")
            print(f"   Density: {density} cars")
            print(f"   {message}")
            print(f"{'🟢' * 10}\n")

            self.simulate_cars_passing()

    def activate_yellow(self, data):
        if self.status != "yellow":
            self.status = "yellow"
            yellow_duration = data.get("duration", 5)
            message = data.get("message", "Prepare to stop")

            print(f"\n{'🟡' * 8}")
            print(f"   {self.signal_name}: 🟡 YELLOW")
            print(f"   {message}")
            print(f"   Duration: {yellow_duration} sec")
            print(f"{'🟡' * 8}\n")

            self.send_status_update()
            time.sleep(yellow_duration)

    def activate_red(self, data):
        if self.status != "red":
            self.status = "red"
            message = data.get("message", "Stop")

            print(f"\n{'🔴' * 10}")
            print(f"   {self.signal_name}: 🔴 RED")
            print(f"   {message}")
            print(f"{'🔴' * 10}\n")

            self.send_status_update()

    def handle_stop(self, data):
        reason = data.get("reason", "Another signal active")
        duration = data.get("duration", 30)

        print(f"\nSTOP: {self.signal_name} temporarily stopped")
        print(f"   Reason: {reason}")
        print(f"   Duration: {duration} sec")
        print(f"   Waiting...\n")

        self.total_waiting += duration

    def activate_emergency(self, data):
        vehicle = data.get("vehicle", "Emergency")
        duration = data.get("duration", 10)

        print(f"\n{'🚑' * 12}")
        print(f"   {self.signal_name}: 🟢 EMERGENCY MODE")
        print(f"   Vehicle: {vehicle}")
        print(f"   Green for: {duration} sec")
        print(f"   Absolute priority!")
        print(f"{'🚑' * 12}\n")

        self.status = "green"
        self.send_status_update()

    def simulate_cars_passing(self):
        cars_per_second = max(1, self.density // 10)
        total_cars = min(self.density, cars_per_second * (self.green_time - 2))

        print(f"   Cars starting to pass...")

        for i in range(self.green_time - 2):
            cars_now = min(cars_per_second, total_cars - self.cars_passed)
            if cars_now > 0:
                self.cars_passed += cars_now
                print(f"   {cars_now} cars passed ({self.cars_passed}/{total_cars})")

            if self.cars_passed >= total_cars:
                break

            time.sleep(5)

        print(f"   Passage complete: {self.cars_passed} cars")
        self.density = max(0, self.density - self.cars_passed)
        self.cars_passed = 0

    def start_traffic_simulation(self):
        import threading

        def traffic_simulator():
            while True:
                change = random.randint(-8, 12)
                self.density = max(0, min(50, self.density + change))
                self.send_density_update()
                time.sleep(7)

        thread = threading.Thread(target=traffic_simulator)
        thread.daemon = True
        thread.start()

    def send_density_update(self):
        data = {
            "value": self.density,
            "signal": self.signal_id,
            "name": self.signal_name,
            "status": self.status,
            "timestamp": time.time()
        }
        self.client.publish(f"traffic/{self.signal_id}/density", json.dumps(data))

        if self.density > 25:
            print(f"HIGH density: {self.signal_name} - {self.density} cars")
        elif self.density > 15:
            print(f"MEDIUM density: {self.signal_name} - {self.density} cars")

    def send_status_update(self):
        data = {
            "status": self.status,
            "signal": self.signal_id,
            "name": self.signal_name,
            "density": self.density,
            "green_time": self.green_time,
            "yellow_time": self.yellow_time,
            "timestamp": time.time()
        }
        self.client.publish(f"traffic/{self.signal_id}/status", json.dumps(data))

    def start(self):
        try:
            self.client.connect("broker.emqx.io", 1883, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"{self.signal_name}: Connection failed - {e}")


if __name__ == "__main__":
    signal = AdvancedTrafficSignal(signal_id, signal_name)
    signal.start()