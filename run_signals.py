import subprocess
import time
import sys

print("=" * 50)
print("🚦 تشغيل الإشارات الأربع تلقائياً")
print("=" * 50)

# تعريف الإشارات
signals = [
    ("intersection1", "SIGNAL 1 (2 lanes)"),
    ("intersection2", "SIGNAL 2 (3 lanes)"),
    ("intersection3", "SIGNAL 3 (1 lane)"),
    ("intersection4", "SIGNAL 4 (2 lanes)")
]

processes = []

try:
    for i, (signal_id, signal_name) in enumerate(signals, 1):
        print(f"\n🔵 تشغيل {signal_name}...")

        # تشغيل الإشارة في عملية منفصلة
        proc = subprocess.Popen([
            sys.executable,
            "traffic_signal_v2.py",
            signal_id,
            signal_name
        ])

        processes.append(proc)
        print(f"   ✅ تم التشغيل (PID: {proc.pid})")

        # انتظر 3 ثواني بين كل إشارة عشان تبدأ واحدة واحدة
        if i < len(signals):
            print(f"   ⏱️  انتظر 3 ثواني للإشارة التالية...")
            time.sleep(3)

    print("\n" + "=" * 50)
    print("✅ جميع الإشارات الأربع تعمل!")
    print("📊 الإشارات: SIGNAL 1, SIGNAL 2, SIGNAL 3, SIGNAL 4")
    print("⏹️  اضغط Ctrl+C لإيقاف الكل")
    print("=" * 50)

    # خلّي السكربت شغال
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n⏹️  جاري إيقاف جميع الإشارات...")
    for proc in processes:
        proc.terminate()
    print("✅ تم إيقاف جميع الإشارات")