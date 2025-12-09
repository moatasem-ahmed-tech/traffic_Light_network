import paho.mqtt.client as mqtt
import json
import time

print("=" * 50)
print("📱 تطبيق سيارة الطوارئ")
print("=" * 50)


class EmergencyApp:
    def __init__(self):
        self.client = mqtt.Client("EmergencyApp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.route = None

    def on_connect(self, client, userdata, flags, rc):
        print("✅ متصل بنظام المرور!")
        print("   📡 في انتظار المسارات...")
        client.subscribe("emergency/response")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.route = data

            print("\n" + "📍" * 20)
            print("   🚨 مسار طوارئ مستلم!")
            print("   📍 المسار:", " → ".join(data.get('path', [])))
            print("   ⏱️  الوقت المقدر:", data.get('estimated_time', 'غير معروف'))
            print("   🟢 الحالة:", data.get('status', 'غير معروف'))
            print("📍" * 20 + "\n")

        except Exception as e:
            print(f"❌ خطأ في المسار: {e}")

    def send_emergency_request(self):
        # إنشاء طلب طوارئ
        requests = [
            {
                "vehicle_id": "إسعاف-101",
                "from": "المستشفى العام",
                "to": "حادث طريق النصر",
                "priority": "عالية"
            },
            {
                "vehicle_id": "إطفاء-202",
                "from": "محطة الإطفاء",
                "to": "حريق العمارة 5",
                "priority": "حرج"
            }
        ]

        for i, request in enumerate(requests, 1):
            print(f"\n🚑 إرسال طلب الطوارئ #{i}...")
            print(f"   🚗 {request['vehicle_id']}")
            print(f"   📍 من {request['from']} إلى {request['to']}")

            request['timestamp'] = time.time()
            self.client.publish("emergency/request", json.dumps(request))

            time.sleep(5)  # انتظار 5 ثواني بين الطلبات

    def start(self):
        try:
            print("🔌 الاتصال بـ MQTT Broker...")
            self.client.connect("broker.emqx.io", 1883, 60)
            self.client.loop_start()

            # انتظار الاتصال
            time.sleep(2)

            # إرسال طلبات الطوارئ
            self.send_emergency_request()

            # البقاء مفتوحًا
            print("\n⏳ التطبيق يعمل... (اضغط Ctrl+C للإيقاف)")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n⏹️  إيقاف التطبيق")
        except Exception as e:
            print(f"❌ خطأ: {e}")


if __name__ == "__main__":
    app = EmergencyApp()
    app.start()