import paho.mqtt.client as mqtt
import json
import time

print("=" * 50)
print("🚦 خادم المرور الذكي يعمل...")
print("=" * 50)


class SmartTrafficServer:
    def __init__(self):
        self.client = mqtt.Client("TrafficServer")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.intersections = {
            "intersection1": {"density": 0, "status": "red"},
            "intersection2": {"density": 0, "status": "red"},
            "intersection3": {"density": 0, "status": "red"}
        }

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ الخادم متصل! (كود: {rc})")
        client.subscribe("traffic/+/density")
        client.subscribe("traffic/+/status")
        client.subscribe("emergency/request")
        print("📡 مشترك في جميع المواضيع...")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        print(f"📩 [{time.strftime('%H:%M:%S')}] {topic}")

        if "density" in topic:
            intersection = topic.split("/")[1]
            if intersection in self.intersections:
                try:
                    data = json.loads(payload)
                    density = data.get("value", 0)
                    self.intersections[intersection]["density"] = density
                    print(f"   📊 الكثافة: {density} سيارة")

                    # تحديد وقت الإشارة
                    if density > 20:
                        green_time = 40
                        color = "🔴"
                    elif density > 10:
                        green_time = 30
                        color = "🟡"
                    else:
                        green_time = 20
                        color = "🟢"

                    response = {"command": "adjust", "green_time": green_time}
                    self.client.publish(f"traffic/{intersection}/control", json.dumps(response))
                    print(f"   {color} الوقت الأخضر: {green_time} ثانية")

                except Exception as e:
                    print(f"   ❌ خطأ: {e}")

        elif "emergency/request" in topic:
            print("🚑" * 10)
            print("   طلب طوارئ مستلم!")
            try:
                data = json.loads(payload)
                print(f"   🚗 السيارة: {data.get('vehicle_id', 'غير معروف')}")
                print(f"   📍 من: {data.get('from', 'غير معروف')}")
                print(f"   🎯 إلى: {data.get('to', 'غير معروف')}")
            except:
                print(f"   📋 البيانات: {payload}")

            # إرسال مسار طوارئ
            route = {
                "path": ["intersection1", "intersection2", "intersection3"],
                "estimated_time": "5 دقائق",
                "status": "green_route_activated",
                "timestamp": time.time()
            }
            self.client.publish("emergency/response", json.dumps(route))
            print(f"   📍 تم إرسال المسار: {route['path']}")
            print("🟢" * 10)

    def start(self):
        try:
            print("🔌 محاولة الاتصال بـ MQTT Broker...")
            self.client.connect("broker.emqx.io", 1883, 60)
            print("✅ الاتصال ناجح!")
            self.client.loop_forever()
        except Exception as e:
            print(f"❌ فشل الاتصال: {e}")
            print("\n🔧 حاول تغيير الـ Broker إلى:")
            print("1. broker.emqx.io")
            print("2. test.mosquitto.org")
            print("3. mqtt.eclipseprojects.io")


if __name__ == "__main__":
    server = SmartTrafficServer()
    server.start()