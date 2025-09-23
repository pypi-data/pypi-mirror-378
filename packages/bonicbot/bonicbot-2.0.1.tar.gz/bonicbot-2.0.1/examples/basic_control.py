#!/usr/bin/env python3
"""
Enhanced BonicBot Demo — Hands, Head, Wheels, and Live Battery Monitor
(Ctrl+C will safely stop everything and close connection)
"""

import time
from datetime import datetime
from bonicbot import WebSocketBonicBotController

ROBOT_IP = "192.168.29.24"
ROBOT_PORT = 8080


def wait(sec=2):
    time.sleep(sec)


# ===================== HAND DEMO =====================
def demo_hands(controller):
    print("\n=== HAND DEMO ===")

    print("\n▶ Left Hand Sequence")
    controller.control_left_hand(gripper=45); wait()
    controller.control_left_hand(wrist=45); wait()
    controller.control_left_hand(elbow=-30); wait()
    controller.control_left_hand(shoulder_pitch=45); wait()
    controller.control_left_hand(shoulder_yaw=30); wait()
    controller.control_left_hand(shoulder_roll=60); wait()

    print("\n▶ Right Hand Sequence")
    controller.control_right_hand(gripper=45); wait()
    controller.control_right_hand(wrist=45); wait()
    controller.control_right_hand(elbow=-30); wait()
    controller.control_right_hand(shoulder_pitch=45); wait()
    controller.control_right_hand(shoulder_yaw=30); wait()
    controller.control_right_hand(shoulder_roll=60); wait()

    print("\n▶ Resetting both hands to Neutral (0°)")
    controller.control_left_hand(
        gripper=0, wrist=0, elbow=0,
        shoulder_pitch=0, shoulder_yaw=0, shoulder_roll=0
    )
    controller.control_right_hand(
        gripper=0, wrist=0, elbow=0,
        shoulder_pitch=0, shoulder_yaw=0, shoulder_roll=0
    )
    wait()

    print("✅ Hands demo complete")


# ===================== HEAD DEMO =====================
def demo_head(controller):
    print("\n=== HEAD DEMO ===")

    def move(pan, tilt, label, wait_time=2):
        print(f"▶ {label} (Pan={pan}°, Tilt={tilt}°)")
        controller.control_head(pan_angle=pan, tilt_angle=tilt, speed=200)
        time.sleep(wait_time)

    move(-45, 0, "Look Left"); move(0, 0, "Neutral")
    move(45, 0, "Look Right"); move(0, 0, "Neutral")
    move(0, 30, "Look Up"); move(0, 0, "Neutral")
    move(0, -30, "Look Down"); move(0, 0, "Neutral")

    print("✅ Head demo complete")


# ===================== WHEEL DEMO =====================
def demo_wheels(controller):
    print("\n=== WHEEL DEMO ===")

    print("➡️ Forward 2s")
    controller.move_forward(80)
    time.sleep(2)
    controller.stop_movement()

    print("⬅️ Backward 2s")
    controller.move_backward(80)
    time.sleep(2)
    controller.stop_movement()

    print("↩️ Left Turn 2s")
    controller.turn_left(70)
    time.sleep(2)
    controller.stop_movement()

    print("↪️ Right Turn 2s")
    controller.turn_right(70)
    time.sleep(2)
    controller.stop_movement()

    print("✅ Wheel demo complete")


# ===================== BATTERY MONITOR =====================
def battery_callback(data):
    """Streamed battery data arrives here"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    voltage = data.get("voltage", "N/A")
    current = data.get("current", "N/A")
    soc = data.get("soc", "N/A")
    temp = data.get("temperature", "N/A")
    print(f"[{timestamp}] 📡 Streamed: Voltage={voltage}V | Current={current}A | SOC={soc}% | Temp={temp}°C")


def demo_battery(controller):
    print("\n=== BATTERY DEMO (Live Stream + Periodic Fetch) ===")

    # Start battery streaming every 2 sec
    controller.start_battery_stream(interval_ms=2000, callback=battery_callback)

    print("🧪 Fetching live battery status every 5 seconds... (Press Ctrl+C to stop)")
    while True:
        battery_data = controller.get_battery_status()
        if battery_data:
            print("\n🔋 Latest Battery Status:")
            print(f"Voltage     : {battery_data.voltage} V")
            print(f"Current     : {battery_data.current} A")
            print(f"Charge (SOC): {battery_data.soc} %")
            print(f"Temperature : {battery_data.temperature} °C")
            if battery_data.has_error:
                print(f"⚠️ Battery Error: {battery_data.error_message}")
        else:
            print("⏳ Waiting for battery data...")

        time.sleep(5)


# ===================== MAIN =====================
def main():
    bot = WebSocketBonicBotController(ROBOT_IP, ROBOT_PORT)
    if not bot.connect():
        print("❌ Failed to connect to BonicBot")
        return

    try:
        print("✅ Connected to BonicBot")

        demo_hands(bot)
        demo_head(bot)
        demo_wheels(bot)
        demo_battery(bot)  # runs until Ctrl+C

    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user.")

    finally:
        bot.stop_movement()
        bot.close()
        print("🔌 Connection closed")


if __name__ == "__main__":
    main()
