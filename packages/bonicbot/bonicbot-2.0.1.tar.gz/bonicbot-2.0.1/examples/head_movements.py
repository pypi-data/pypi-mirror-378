#!/usr/bin/env python3
"""
Enhanced BonicBot Head Control with Expressions

Demonstrates advanced head control including:
- Expression modes synchronized with movement
- Interactive behaviors with speech
- Sensor-guided attention behaviors
- Emotional response patterns
- Complex choreographed head movements
"""

import time
import math
import random
from typing import List, Tuple
from bonicbot import (
    create_serial_controller,
    create_websocket_controller,
    HeadModes,
    HeadCommand,
    ServoConstants
)

class ExpressiveHeadController:
    """Advanced head controller with expression and behavior integration"""
    
    def __init__(self, robot):
        self.robot = robot
        self.has_websocket = hasattr(robot, 'set_head_mode')
        self.current_expression = HeadModes.NORMAL if self.has_websocket else None
        self.attention_targets = []
        
        print(f"✅ Head controller initialized ({'WebSocket' if self.has_websocket else 'Serial'} mode)")
    
    def set_expression_with_speech(self, expression: HeadModes, speech_text: str = None):
        if not self.has_websocket:
            return
        print(f"😊 Setting expression: {expression.value}")
        self.robot.set_head_mode(expression)
        self.current_expression = expression
        if speech_text and hasattr(self.robot, 'speak'):
            print(f"🗣️ Speaking: \"{speech_text}\"")
            self.robot.speak(speech_text)
    
    def expressive_scan(self, expression: HeadModes = HeadModes.NORMAL, 
                       speech: str = None, scan_range: int = 60):
        print(f"👀 Expressive scanning (expression: {expression.value if expression else 'None'})")
        if expression and self.has_websocket:
            self.robot.set_head_mode(expression)
        if speech and hasattr(self.robot, 'speak'):
            self.robot.speak(speech)
        positions = [-scan_range, -scan_range//2, 0, scan_range//2, scan_range, 0]
        for pan_angle in positions:
            self.robot.control_head(pan_angle=pan_angle, tilt_angle=5, speed=120)
            time.sleep(0.8)
    
    def emotional_response_sequence(self):
        print("🎭 Emotional response sequence")
        emotions = [
            {
                "name": "Curiosity",
                "expression": HeadModes.NORMAL,
                "speech": "What's that interesting thing over there?",
                "movements": [
                    (45, 15, 100),
                    (60, 20, 80),
                    (45, 10, 100),
                    (0, 0, 120)
                ]
            },
            {
                "name": "Surprise",
                "expression": HeadModes.SURPRISED,
                "speech": "Oh my! That was unexpected!",
                "movements": [
                    (0, 25, 200),
                    (-30, 20, 150),
                    (30, 20, 150),
                    (0, 15, 100)
                ]
            },
            {
                "name": "Happiness",
                "expression": HeadModes.HAPPY,
                "speech": "I'm so happy to see you!",
                "movements": [
                    (20, 10, 120),
                    (-20, 10, 120),
                    (0, 15, 100),
                    (0, 5, 80)
                ]
            },
            {
                "name": "Sadness",
                "expression": HeadModes.SAD,
                "speech": "I'm feeling a bit down today.",
                "movements": [
                    (0, -15, 80),
                    (-20, -10, 60),
                    (0, -20, 60),
                    (0, -5, 80)
                ]
            },
            {
                "name": "Confusion",
                "expression": HeadModes.CONFUSED,
                "speech": "I don't understand what's happening here.",
                "movements": [
                    (30, 8, 100),
                    (-30, 8, 100),
                    (15, -5, 80),
                    (-15, -5, 80),
                    (0, 0, 100)
                ]
            },
            {
                "name": "Anger",
                "expression": HeadModes.ANGRY,
                "speech": "That really makes me upset!",
                "movements": [
                    (0, -10, 150),
                    (25, -5, 120),
                    (-25, -5, 120),
                    (0, 0, 100)
                ]
            }
        ]
        for emotion in emotions:
            print(f"   Emotion: {emotion['name']}")
            if self.has_websocket:
                self.robot.set_head_mode(emotion['expression'])
                time.sleep(0.5)
            if hasattr(self.robot, 'speak'):
                self.robot.speak(emotion['speech'])
                time.sleep(1)
            for pan, tilt, speed in emotion['movements']:
                self.robot.control_head(pan_angle=pan, tilt_angle=tilt, speed=speed)
                time.sleep(1.2)
            time.sleep(2)
            print()
        if self.has_websocket:
            self.robot.set_head_mode(HeadModes.NORMAL)
        self.robot.control_head(pan_angle=0, tilt_angle=0)
    
    def interactive_attention_behavior(self, duration: int = 30):
        print(f"🧠 Interactive attention behavior for {duration} seconds")
        if hasattr(self.robot, 'speak'):
            self.robot.speak("I'm now in interactive mode. I'll respond to various stimuli.")
        start_time = time.time()
        last_action_time = start_time
        stimuli_types = [
            "sound_left", "sound_right", "movement_up", "person_center",
            "noise_behind", "curiosity_trigger", "surprise_event", "recognition"
        ]
        while time.time() - start_time < duration:
            current_time = time.time()
            if current_time - last_action_time > random.uniform(3, 6):
                stimulus = random.choice(stimuli_types)
                self.respond_to_stimulus(stimulus)
                last_action_time = current_time
            time.sleep(0.5)
        print("✅ Interactive behavior completed")
    
    def respond_to_stimulus(self, stimulus_type: str):
        responses = {
            "sound_left": {
                "description": "Sound from left",
                "expression": HeadModes.NORMAL,
                "speech": "I hear something over there",
                "movement": (-60, 10, 180)
            },
            "sound_right": {
                "description": "Sound from right",
                "expression": HeadModes.NORMAL,
                "speech": "What was that sound?",
                "movement": (60, 10, 180)
            },
            "movement_up": {
                "description": "Movement above",
                "expression": HeadModes.SURPRISED,
                "speech": "Something's happening up there!",
                "movement": (0, 35, 200)
            },
            "person_center": {
                "description": "Person detected center",
                "expression": HeadModes.HAPPY,
                "speech": "Hello there! Nice to see you!",
                "movement": (0, 5, 100)
            },
            "noise_behind": {
                "description": "Noise from behind",
                "expression": HeadModes.CONFUSED,
                "speech": "Was that behind me?",
                "movement": (0, 0, 120)
            },
            "curiosity_trigger": {
                "description": "Something interesting",
                "expression": HeadModes.NORMAL,
                "speech": "That's quite interesting",
                "movement": (random.randint(-45, 45), random.randint(0, 20), 120)
            },
            "surprise_event": {
                "description": "Surprising event",
                "expression": HeadModes.SURPRISED,
                "speech": "Whoa! That was unexpected!",
                "movement": (0, 25, 250)
            },
            "recognition": {
                "description": "Recognizing someone",
                "expression": HeadModes.HAPPY,
                "speech": "Oh, I remember you!",
                "movement": (15, 8, 120)
            }
        }
        if stimulus_type in responses:
            response = responses[stimulus_type]
            print(f"   📡 Stimulus: {response['description']}")
            if self.has_websocket and response['expression']:
                self.robot.set_head_mode(response['expression'])
            if hasattr(self.robot, 'speak') and response['speech']:
                self.robot.speak(response['speech'])
            pan, tilt, speed = response['movement']
            self.robot.control_head(pan_angle=pan, tilt_angle=tilt, speed=speed)
            time.sleep(2.5)
            self.robot.control_head(pan_angle=0, tilt_angle=5, speed=100)
    
    def tracking_simulation_advanced(self):
        print("🎯 Advanced tracking simulation")
        if hasattr(self.robot, 'speak'):
            self.robot.speak("I will now track a virtual object moving around")
        if self.has_websocket:
            self.robot.set_head_mode(HeadModes.NORMAL)
        patterns = [
            {"name": "Horizontal sweep","points": [(i * 15 - 60, 10) for i in range(9)],"speed": 150},
            {"name": "Vertical scan","points": [(0, i * 8 - 20) for i in range(9)],"speed": 120},
            {"name": "Circular tracking","points": [(30 * math.cos(i * math.pi / 8), 15 * math.sin(i * math.pi / 8)) for i in range(16)],"speed": 100},
            {"name": "Figure-8 tracking","points": [(40 * math.sin(i * math.pi / 6), 20 * math.sin(i * math.pi / 3)) for i in range(12)],"speed": 130},
            {"name": "Random movement","points": [(random.randint(-50, 50), random.randint(-15, 25)) for _ in range(10)],"speed": 180}
        ]
        for pattern in patterns:
            print(f"   Tracking: {pattern['name']}")
            for pan, tilt in pattern['points']:
                pan = max(ServoConstants.HEAD_PAN_MIN, min(ServoConstants.HEAD_PAN_MAX, pan))
                tilt = max(ServoConstants.HEAD_TILT_MIN, min(ServoConstants.HEAD_TILT_MAX, tilt))
                self.robot.control_head(pan_angle=pan, tilt_angle=tilt, speed=pattern['speed'])
                time.sleep(0.3)
            time.sleep(1)
        self.robot.control_head(pan_angle=0, tilt_angle=0)
        print("✅ Tracking simulation completed")
    
    def social_interaction_demo(self):
        print("👥 Social interaction demonstration")
        if hasattr(self.robot, 'speak'):
            self.robot.speak("Let me show you various social behaviors")
        interactions = [
            {"name": "Greeting","expression": HeadModes.HAPPY,"speech": "Hello! It's wonderful to meet you!","gestures": [(0, 15, 100),(20, 10, 120),(-20, 10, 120),(0, 8, 100)]},
            {"name": "Active Listening","expression": HeadModes.NORMAL,"speech": "I'm listening carefully to what you're saying","gestures": [(0, 5, 80),(10, 3, 60),(0, 5, 80),(-5, 8, 70)]},
            {"name": "Agreement","expression": HeadModes.HAPPY,"speech": "Yes, I completely agree with you!","gestures": [(0, 15, 120),(0, 5, 120),(0, 15, 120),(0, 8, 100)]},
            {"name": "Disagreement","expression": HeadModes.CONFUSED,"speech": "I'm not sure I agree with that point","gestures": [(25, 5, 100),(-25, 5, 100),(25, 5, 100),(0, 0, 100)]},
            {"name": "Thinking","expression": HeadModes.NORMAL,"speech": "Let me think about that for a moment","gestures": [(30, -5, 80),(0, -10, 60),(-20, 5, 80),(0, 5, 100)]},
            {"name": "Farewell","expression": HeadModes.HAPPY,"speech": "It was great talking with you! See you later!","gestures": [(0, 12, 100),(30, 15, 120),(-30, 15, 120),(0, 10, 100)]}
        ]
        for interaction in interactions:
            print(f"   Social behavior: {interaction['name']}")
            if self.has_websocket and interaction['expression']:
                self.robot.set_head_mode(interaction['expression'])
                time.sleep(0.5)
            if hasattr(self.robot, 'speak') and interaction['speech']:
                self.robot.speak(interaction['speech'])
                time.sleep(1)
            for pan, tilt, speed in interaction['gestures']:
                self.robot.control_head(pan_angle=pan, tilt_angle=tilt, speed=speed)
                time.sleep(1.2)
            time.sleep(2)
            print()
        if self.has_websocket:
            self.robot.set_head_mode(HeadModes.NORMAL)
        self.robot.control_head(pan_angle=0, tilt_angle=0)
    
    def composite_head_control_demo(self):
        print("⚙️ Composite head control demonstration")
        if not hasattr(self.robot, 'control_head_composite'):
            print("   Composite control not available in serial mode")
            return
        commands = [
            HeadCommand(pan=45, tilt=20, mode=HeadModes.HAPPY, speed=150, acceleration=30),
            HeadCommand(pan=-60, tilt=15, mode=HeadModes.SURPRISED, speed=200, acceleration=25),
            HeadCommand(pan=30, tilt=-10, mode=HeadModes.CONFUSED, speed=120, acceleration=20),
            HeadCommand(pan=0, tilt=25, mode=HeadModes.NORMAL, speed=180, acceleration=35),
            HeadCommand(pan=-45, tilt=5, mode=HeadModes.SAD, speed=100, acceleration=15),
            HeadCommand(pan=0, tilt=0, mode=HeadModes.NORMAL, speed=150, acceleration=25)
        ]
        for i, cmd in enumerate(commands):
            print(f"   Command {i+1}: Pan={cmd.pan}°, Tilt={cmd.tilt}°, Mode={cmd.mode.value}")
            self.robot.control_head_composite(cmd)
            time.sleep(2.5)
        print("✅ Composite control demo completed")

def main():
    print("🤖 Enhanced BonicBot Head Control with Expressions")
    print("==================================================")
    
    robot = None
    connection_type = "unknown"
    try:
        print("🌐 Attempting WebSocket connection...")
        robot = create_websocket_controller("192.168.29.24", 8080)
        if robot.connect():
            connection_type = "websocket"
            print("✅ WebSocket connected - Full expression features available!")
        else:
            raise ConnectionError("WebSocket failed")
    except:
        print("⚠️ WebSocket failed, trying serial...")
        try:
            robot = create_serial_controller('/dev/ttyUSB0')
            connection_type = "serial"
            print("✅ Serial connected - Basic head movement available")
        except Exception as e:
            print(f"❌ All connections failed: {e}")
            return
    
    try:
        with robot:
            controller = ExpressiveHeadController(robot)
            print(f"\n🚀 Starting head control demonstrations ({connection_type} mode)...")
            
            try:
                if connection_type == "websocket":
                    controller.expressive_scan(
                        HeadModes.HAPPY, 
                        "Let me look around and see what's happening",
                        scan_range=70
                    )
                else:
                    positions = [-70, -35, 0, 35, 70, 0]
                    for pan in positions:
                        robot.control_head(pan_angle=pan, tilt_angle=5)
                        time.sleep(1)
                
                time.sleep(2)
                controller.emotional_response_sequence()
                time.sleep(2)
                controller.tracking_simulation_advanced()
                time.sleep(2)
                
                if connection_type == "websocket":
                    controller.social_interaction_demo()
                    time.sleep(2)
                    controller.interactive_attention_behavior(duration=15)
                    time.sleep(2)
                    controller.composite_head_control_demo()
                
                robot.control_head(pan_angle=0, tilt_angle=0)
                if hasattr(robot, 'speak'):
                    robot.speak("Head control demonstration completed successfully!")
                print("\n✅ All head control demonstrations completed!")
            
            except KeyboardInterrupt:
                print("\n🛑 Demo interrupted by user (Ctrl+C). Resetting head...")
                robot.control_head(pan_angle=0, tilt_angle=0)
    
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        if robot:
            robot.control_head(pan_angle=0, tilt_angle=0)

if __name__ == "__main__":
    main()
