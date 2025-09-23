#!/usr/bin/env python3
"""
BonicBot Hand Gestures (Safe & Tuned Version)
- Wave (custom angles)
- Pointing
- Applause
- Thinking Pose (custom)
- Victory Celebration
- Pick and Place
- Expressive Sequence
"""

import time
import signal
import sys
from bonicbot import (
    create_serial_controller,
    create_websocket_controller,
)

# ------------------- Safe Exit -------------------

robot = None

def safe_exit(sig, frame):
    """Handle Ctrl+C safely"""
    global robot
    print("\n🛑 Ctrl+C pressed — stopping and resetting robot...")
    if robot:
        try:
            robot.reset_to_home_position()
            time.sleep(1)
            robot.close()
        except Exception as e:
            print(f"⚠️ Error while closing: {e}")
    sys.exit(0)

# Attach Ctrl+C handler
signal.signal(signal.SIGINT, safe_exit)

# ------------------- Gestures -------------------

def wave_gesture(robot, waves=3, speed=120.0):
    """Wave gesture with specific angles:
       shoulder pitch 60, roll 70, yaw 30,
       elbow swings -80 ↔ -20, repeated 3 times
    """
    print(f"👋 Waving hello ({waves} waves)...")

    # Move to starting position
    robot.control_right_shoulder_pitch(60, speed)
    robot.control_right_shoulder_roll(70, speed)
    robot.control_right_shoulder_yaw(30, speed)
    robot.control_right_elbow(-80, speed)
    time.sleep(1.5)

    # Wave motion by elbow
    for i in range(waves):
        robot.control_right_elbow(-20, speed)   # elbow open
        time.sleep(0.6)
        robot.control_right_elbow(-80, speed)   # elbow close
        time.sleep(0.6)

    # Reset
    robot.reset_to_home_position()
    time.sleep(1.2)


def pointing_gestures(robot, speed=120.0):
    """Point in different directions with right hand"""
    print("👉 Performing pointing gestures...")

    # Forward
    robot.control_right_shoulder_pitch(60, speed)
    robot.control_right_elbow(-20, speed)
    time.sleep(1.5)

    # Left
    robot.control_right_shoulder_pitch(50, speed)
    robot.control_right_shoulder_yaw(60, speed)
    time.sleep(1.5)

    # Right
    robot.control_right_shoulder_pitch(50, speed)
    robot.control_right_shoulder_yaw(-60, speed)
    time.sleep(1.5)

    # Reset
    robot.reset_to_home_position()
    time.sleep(1)


def applause_gesture(robot, claps=4, speed=150.0):
    """Clap hands"""
    print(f"👏 Applauding with {claps} claps...")

    for i in range(claps):
        print(f"   Clap {i+1}/{claps}")
        # Hands together
        robot.control_left_shoulder_pitch(30, speed)
        robot.control_right_shoulder_pitch(30, speed)
        time.sleep(0.3)

        # Hands apart
        robot.control_left_shoulder_pitch(60, speed)
        robot.control_right_shoulder_pitch(0, speed)
        time.sleep(0.3)

    robot.reset_to_home_position()
    time.sleep(1)


def thinking_pose(robot, duration=3.0):
    """Thinking pose with updated angles"""
    print("🤔 Thinking pose...")

    robot.control_right_shoulder_pitch(0, 80)
    robot.control_right_elbow(-60, 100)
    robot.control_head_pan(15, 100)
    robot.control_head_tilt(10, 100)

    time.sleep(duration)

    robot.reset_to_home_position()
    time.sleep(1)


def victory_celebration(robot, speed=150.0):
    """Victory celebration with both arms up"""
    print("🎉 Victory celebration!")

    robot.control_left_shoulder_pitch(150, speed)
    robot.control_right_shoulder_pitch(150, speed)

    robot.control_head_tilt(15, 100)
    time.sleep(2)

    robot.reset_to_home_position()
    time.sleep(1)


def pick_and_place(robot):
    """Simple pick and place demo"""
    print("🤏 Pick and place demo...")

    # Approach
    robot.control_right_shoulder_pitch(45, 100)
    robot.control_right_elbow(-70, 100)
    time.sleep(1.5)

    # Close gripper
    robot.control_right_gripper(-20, 80)
    time.sleep(1)

    # Lift
    robot.control_right_shoulder_pitch(60, 100)
    robot.control_right_elbow(-30, 100)
    time.sleep(1.5)

    # Place
    robot.control_right_gripper(60, 80)
    time.sleep(1)

    robot.reset_to_home_position()
    print("✅ Pick and place complete!")
    time.sleep(1)


def expressive_sequence(robot):
    """Expressive gesture sequence"""
    print("🎭 Expressive sequence...")

    # Shrug (confused)
    robot.control_left_shoulder_pitch(60, 120)
    robot.control_right_shoulder_pitch(60, 120)
    robot.control_head_tilt(15, 100)
    time.sleep(2)

    # Stop gesture
    robot.control_right_shoulder_pitch(90, 150)
    robot.control_right_elbow(-10, 150)
    time.sleep(2)

    # Thumbs up (approximate)
    robot.control_right_shoulder_pitch(60, 120)
    robot.control_right_elbow(-45, 120)
    robot.control_right_gripper(-60, 120)
    time.sleep(2)

    robot.reset_to_home_position()
    time.sleep(1)


# ------------------- Demonstration Runner -------------------

def demonstrate_gestures(robot):
    """Run all gestures sequentially"""
    robot.reset_to_home_position()
    time.sleep(1)

    wave_gesture(robot)
    pointing_gestures(robot)
    applause_gesture(robot)
    thinking_pose(robot)
    victory_celebration(robot)
    pick_and_place(robot)
    expressive_sequence(robot)

    robot.reset_to_home_position()
    print("\n✅ All gesture demonstrations completed!")


# ------------------- Main -------------------

def main():
    global robot
    print("🤖 BonicBot Hand Gestures Demo")
    print("==============================")

    try:
        # Try WebSocket
        print("🌐 Connecting via WebSocket...")
        robot = create_websocket_controller("192.168.29.24", 8080)
        robot.connect()

        if robot.is_connected():
            print("✅ Connected via WebSocket!")
            demonstrate_gestures(robot)
        else:
            raise ConnectionError("WebSocket connection failed")

    except Exception as e:
        print(f"⚠️ WebSocket failed: {e}")
        print("🔌 Trying serial...")
        try:
            robot = create_serial_controller('/dev/ttyUSB0')
            robot.connect()
            print("✅ Connected via Serial")
            demonstrate_gestures(robot)
        except Exception as e:
            print(f"❌ Serial connection also failed: {e}")
    finally:
        if robot:
            robot.reset_to_home_position()
            time.sleep(1)
            robot.close()


if __name__ == "__main__":
    main()
