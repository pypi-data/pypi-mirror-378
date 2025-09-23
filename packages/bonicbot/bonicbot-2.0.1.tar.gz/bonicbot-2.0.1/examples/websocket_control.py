#!/usr/bin/env python3
"""
BonicBot Full Demo — Hands (sequence), Head, Wheels, Battery Monitor + OpenCV Camera
(Ctrl+C will safely stop everything and close connection)
"""

import time
import cv2
from datetime import datetime
from bonicbot import create_websocket_controller

# === CONFIG ===
ROBOT_IP = "192.168.29.24"
WEBSOCKET_PORT = 8080
MJPEG_PORT = 8081
MJPEG_STREAM = f"http://{ROBOT_IP}:{MJPEG_PORT}/stream"

# Camera orientation settings
ROTATE_ANGLE = 90      # 0, 90, 180, 270
FLIP_HORIZONTAL = True


# ============ HELPERS ============
def wait(sec=2):
    time.sleep(sec)

def rotate_image(frame, angle):
    """Rotate frame according to ROTATE_ANGLE"""
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame


# ============ HAND SEQUENCE ============
def demo_hands(bot):
    print("\n=== HAND SEQUENCE DEMO ===")

    sequence = [
        {"gripper": 45, "wrist": 30, "elbow": -20, "shoulder_pitch": 20, "shoulder_yaw": 10, "shoulder_roll": 30},
        {"gripper": 10, "wrist": 30, "elbow": -40, "shoulder_pitch": 20, "shoulder_yaw": 15, "shoulder_roll": 25},
        {"gripper": 60, "wrist": 0, "elbow": 0, "shoulder_pitch": 45, "shoulder_yaw": 0, "shoulder_roll": 60},
    ]

    for pose in sequence:
        print(f"▶ Executing hand pose: {pose}")
        bot.control_left_hand(**pose)
        bot.control_right_hand(**pose)
        wait(2)

    print("▶ Resetting both hands to neutral")
    bot.reset_to_home_position()
    print("✅ Hand sequence complete")


# ============ HEAD DEMO ============
def demo_head(bot):
    print("\n=== HEAD DEMO ===")
    positions = [(-45, 0, "Look Left"), (0, 0, "Neutral"),
                 (45, 0, "Look Right"), (0, 0, "Neutral"),
                 (0, 30, "Look Up"), (0, 0, "Neutral"),
                 (0, -30, "Look Down"), (0, 0, "Neutral")]

    for pan, tilt, label in positions:
        print(f"▶ {label} (Pan={pan}, Tilt={tilt})")
        bot.control_head(pan_angle=pan, tilt_angle=tilt, speed=200)
        wait(1)
    print("✅ Head demo complete")


# ============ WHEEL DEMO ============
def demo_wheels(bot):
    print("\n=== WHEEL DEMO ===")
    bot.move_forward(80, duration=2); wait(1)
    bot.move_backward(80, duration=2); wait(1)
    bot.turn_left(70, duration=2); wait(1)
    bot.turn_right(70, duration=2); wait(1)
    bot.stop_movement()
    print("✅ Wheel demo complete")


# ============ BATTERY DEMO ============
def battery_callback(data):
    timestamp = datetime.now().strftime("%H:%M:%S")
    voltage = data.get("voltage", "N/A")
    current = data.get("current", "N/A")
    soc = data.get("soc", "N/A")
    temp = data.get("temperature", "N/A")
    print(f"[{timestamp}] 🔋 Voltage={voltage}V | Current={current}A | SOC={soc}% | Temp={temp}°C")

def demo_battery(bot):
    print("\n=== BATTERY DEMO (Streaming for 15 sec) ===")
    bot.start_battery_stream(interval_ms=2000, callback=battery_callback)
    for _ in range(3):
        status = bot.get_battery_status()
        if status:
            print(f"🔋 Latest SOC={status.soc}%  Temp={status.temperature}°C")
        time.sleep(5)


# ============ CAMERA DEMO ============
def demo_camera():
    print("\n=== CAMERA DEMO (with correct angle/flip) ===")
    cap = cv2.VideoCapture(MJPEG_STREAM)
    if not cap.isOpened():
        print("❌ Failed to open camera stream")
        return

    print("📸 Press 's' to save snapshot, 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Apply correct orientation
        if FLIP_HORIZONTAL:
            frame = cv2.flip(frame, 1)
        if ROTATE_ANGLE != 0:
            frame = rotate_image(frame, ROTATE_ANGLE)

        cv2.imshow("BonicBot Camera", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            filename = f"snapshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Saved {filename}")
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Camera demo complete")


# ============ MAIN ============
def main():
    bot = create_websocket_controller(ROBOT_IP, WEBSOCKET_PORT)
    if not bot.connect():
        print("❌ Failed to connect to BonicBot")
        return

    try:
        print("✅ Connected to BonicBot")
        demo_hands(bot)
        demo_head(bot)
        demo_wheels(bot)
        demo_battery(bot)
        demo_camera()
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        bot.stop_movement()
        bot.close()
        print("🔌 Connection closed")


if __name__ == "__main__":
    main()
