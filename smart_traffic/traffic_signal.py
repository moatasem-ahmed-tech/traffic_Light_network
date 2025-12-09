import paho.mqtt.client as mqtt
import json
import random
import time
import sys

# تحديد اسم الإشارة
if len(sys.argv) > 1:
    signal_id = sys.argv[1]
else:
    signal_id = "intersection1"

print("=" * 50)
print(f"🚦 إشارة مرور: {signal_id}")
print("=" * 50)


class TrafficSignal:
    def __init__(self, signal_id):
        self.signal_id = signal_id
        self.client = mqtt.Client(signal_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.traffic_density = random.randint(5, 30)
        self.green_time = 30

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ {self.signal_id}: متصل بالخادم!")
        print(f"   📡 Broker: broker.emqx.io")
        print(f"   📊 الكثافة الأولية: {self.traffic_density}")

        # الاشتراك في أوامر التحكم
        client.subscribe(f"traffic/{self.signal_id}/control")

        # بدء إرسال البيانات
        self.send_traffic_data()

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            command = data.get("command")

            if command == "adjust":
                self.green_time = data.get("green_time", 30)
                print(f"🟢 {self.signal_id}: ضبط الوقت الأخضر لـ {self.green_time} ثانية")

        except Exception as e:
            print(f"❌ {self.signal_id}: خطأ في الأمر - {e}")

    def send_traffic_data(self):
        while True:
            # تغيير عشوائي
            change = random.randint(-5, 8)
            self.traffic_density = max(0, min(50, self.traffic_density + change))

            # إرسال البيانات
            data = {"value": self.traffic_density, "signal": self.signal_id}
            self.client.publish(f"traffic/{self.signal_id}/density", json.dumps(data))

            # إرسال حالة الإشارة
            status_data = {
                "state": "green" if self.traffic_density < 15 else "yellow" if self.traffic_density < 25 else "red",
                "density": self.traffic_density
            }
            self.client.publish(f"traffic/{self.signal_id}/status", json.dumps(status_data))

            print(f"📤 {self.signal_id}: الكثافة = {self.traffic_density} | الضوء = {status_data['state']}")

            # الانتقال 3 ثواني
            time.sleep(3)

    def start(self):
        try:
            self.client.connect("broker.emqx.io", 1883, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"❌ {self.signal_id}: فشل الاتصال - {e}")


if __name__ == "__main__":
    signal = TrafficSignal(signal_id)
    signal.start()