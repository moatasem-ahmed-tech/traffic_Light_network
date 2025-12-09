import subprocess
import time
import sys

print("🚀 بدء تشغيل نظام المرور الذكي")
print("=" * 50)

# تشغيل المكونات
processes = []

try:
    # 1. الخادم
    print("1️⃣  تشغيل الخادم المركزي...")
    server = subprocess.Popen([sys.executable, "traffic_server.py"])
    processes.append(server)
    time.sleep(3)

    # 2. الإشارات
    signals = ["intersection1", "intersection2", "intersection3"]
    for i, signal in enumerate(signals, 1):
        print(f"{i + 1}️⃣  تشغيل الإشارة {signal}...")
        proc = subprocess.Popen([sys.executable, "traffic_signal.py", signal])
        processes.append(proc)
        time.sleep(2)

    # 3. تطبيق الطوارئ
    print("5️⃣  تشغيل تطبيق الطوارئ...")
    time.sleep(5)
    emergency = subprocess.Popen([sys.executable, "emergency_app.py"])
    processes.append(emergency)

    print("\n" + "✅" * 20)
    print("   النظام يعمل بنجاح!")
    print("   🔹 الخادم المركزي")
    print("   🔹 3 إشارات مرور")
    print("   🔹 تطبيق الطوارئ")
    print("✅" * 20)

    print("\n📊 المراقبة النشطة... (اضغط Ctrl+C للإيقاف)")

    # البقاء قيد التشغيل
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n⏹️  إيقاف النظام...")
finally:
    # إيقاف جميع العمليات
    for proc in processes:
        proc.terminate()
    print("تم إيقاف جميع المكونات")