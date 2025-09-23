#!/usr/bin/env python3
"""
BonicBot Showcase Demo
- Moves forward, backward, left, right
- Speaks intro
- Shows dance (hands + head + wheels)
- Moves in zigzag path
- Ctrl+C safe exit
"""

import time
import signal
import sys
from bonicbot import create_websocket_controller, create_serial_controller

robot = None

# ---------------- Safe Exit ----------------
def safe_exit(sig, frame):
    global robot
    print("\n🛑 Stopping robot safely...")
    if robot:
        try:
            robot.reset_to_home_position()
            time.sleep(1)
            robot.close()
        except Exception as e:
            print(f"⚠️ Error while closing: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, safe_exit)

# ---------------- Movements ----------------
def basic_moves(robot):
    """Forward, backward, left, right demo"""
    print("🚗 Performing basic moves...")

    print("➡️ Forward")
    robot.move_forward(80, duration=2)
    time.sleep(0.5)

    print("⬅️ Backward")
    robot.move_backward(80, duration=2)
    time.sleep(0.5)

    print("↩️ Turn Left")
    robot.turn_left(80, duration=2)
    time.sleep(0.5)

    print("↪️ Turn Right")
    robot.turn_right(80, duration=2)
    time.sleep(0.5)

    robot.stop_movement()
    print("✅ Basic moves complete!")

def dance_demo(robot):
    """Fun dance movement with arms, head and base"""
    print("💃 Starting dance demo...")

    # Arms up
    robot.control_right_shoulder_pitch(90, 150)
    robot.control_left_shoulder_pitch(90, 150)
    time.sleep(1)

    # Head shake
    for _ in range(2):
        robot.control_head_pan(-30, 120)
        time.sleep(0.5)
        robot.control_head_pan(30, 120)
        time.sleep(0.5)
    robot.control_head_pan(0, 120)

    # Arm swings
    for _ in range(2):
        robot.control_right_shoulder_yaw(45, 150)
        robot.control_left_shoulder_yaw(-45, 150)
        time.sleep(0.6)
        robot.control_right_shoulder_yaw(-45, 150)
        robot.control_left_shoulder_yaw(45, 150)
        time.sleep(0.6)

    # Base spin
    robot.turn_left(100, duration=1.5)
    robot.turn_right(100, duration=1.5)

    robot.reset_to_home_position()
    print("✅ Dance finished!")

def zigzag_path(robot, repeats=3, speed=80, duration=1.5):
    """Zigzag movement"""
    print("🌀 Moving in zigzag path...")
    for i in range(repeats):
        print(f"Zig {i+1}")
        robot.turn_left(speed, duration)
        print(f"Zag {i+1}")
        robot.turn_right(speed, duration)
    robot.stop_movement()
    print("✅ Zigzag complete!")

# ---------------- Main ----------------
def main():
    global robot
    print("🤖 BonicBot Showcase Demo")
    print("==========================")

    try:
        # Try WebSocket
        print("🌐 Connecting via WebSocket...")
        robot = create_websocket_controller("192.168.29.24", 8080)
        robot.connect()
        if robot.is_connected():
            print("✅ Connected via WebSocket!")
        else:
            raise ConnectionError("WebSocket failed")
    except Exception as e:
        print(f"⚠️ WebSocket error: {e}")
        print("🔌 Trying Serial...")
        robot = create_serial_controller('/dev/ttyUSB0')
        robot.connect()
        if robot.is_connected():
            print("✅ Connected via Serial")
        else:
            print("❌ Serial connection also failed")
            return

    # Start sequence
    basic_moves(robot)

    # Speak intro
    print("🗣️ Speaking intro...")
    try:
        robot.speak("I am BonicBot. I will show you my dance movement.")
        time.sleep(3)
    except Exception:
        print("⚠️ Speech not supported in serial mode, skipping...")

    # Dance
    dance_demo(robot)

    # Zigzag
    zigzag_path(robot, repeats=3)

    # Reset
    robot.reset_to_home_position()
    time.sleep(1)
    robot.close()
    print("✅ Demo completed successfully!")

if __name__ == "__main__":
    main()
