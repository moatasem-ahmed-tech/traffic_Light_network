import paho.mqtt.publish as publish
import json

# اختبار إرسال بيانات
print("🧪 اختبار النظام...")

# 1. اختبار إرسال كثافة
publish.single("traffic/intersection1/density",
              json.dumps({"value": 25}),
              hostname="broker.emqx.io")
print("✅ أرسلت بيانات كثافة")

# 2. اختبار طلب طوارئ
publish.single("emergency/request",
              json.dumps({"vehicle_id": "test", "from": "A", "to": "B"}),
              hostname="broker.emqx.io")
print("✅ أرسلت طلب طوارئ")

print("📡 تم إرسال بيانات الاختبار")