# BonicBot API Documentation v2.0.1

## Overview

The BonicBot library provides a comprehensive Python interface for controlling BonicBot humanoid robots via **serial communication** or **WebSocket**. The library supports advanced features including sequence control, camera operations, speech synthesis, real-time sensor monitoring, and emotional expressions.

### Main Components

- **Controllers**: `SerialBonicBotController`, `WebSocketBonicBotController`
- **Factory Functions**: `create_serial_controller()`, `create_websocket_controller()`
- **Enumerations**: `ServoID`, `CommunicationType`, `HeadModes`, `SequenceAction`, `CameraAction`
- **Data Classes**: Command and reading classes for structured control
- **GUI**: `BonicBotGUI` (optional, requires tkinter)

---

## Quick Start

### Basic Usage

```python
# Serial Communication (Basic Features)
from bonicbot import create_serial_controller
with create_serial_controller('/dev/ttyUSB0') as robot:
    robot.control_head(pan_angle=45, tilt_angle=20)
    robot.wave_hello()

# WebSocket Communication (Full Features)  
from bonicbot import create_websocket_controller, HeadModes
with create_websocket_controller('192.168.1.100', 8080) as robot:
    robot.speak("Hello, I am BonicBot!")
    robot.set_head_mode(HeadModes.HAPPY)
    robot.play_sequence("greeting_sequence")
```

---

## Factory Functions

### create_serial_controller()

```python
create_serial_controller(port: str, baudrate: int = 115200, timeout: float = 1.0) -> SerialBonicBotController
```

Create a controller for serial communication (basic features only).

**Parameters:**
- `port` (str): Serial port path (e.g., '/dev/ttyUSB0', 'COM3')
- `baudrate` (int): Communication baud rate (default: 115200)
- `timeout` (float): Connection timeout in seconds (default: 1.0)

**Returns:** `SerialBonicBotController` instance

**Example:**
```python
robot = create_serial_controller('/dev/ttyUSB0', baudrate=115200)
```

### create_websocket_controller()

```python
create_websocket_controller(host: str = "localhost", port: int = 8080) -> WebSocketBonicBotController
```

Create a controller for WebSocket communication (full feature set).

**Parameters:**
- `host` (str): Robot IP address or hostname (default: "localhost")
- `port` (int): WebSocket port number (default: 8080)

**Returns:** `WebSocketBonicBotController` instance

**Example:**
```python
robot = create_websocket_controller("192.168.1.100", 8080)
```

---

## Core Controller Interface

Both `SerialBonicBotController` and `WebSocketBonicBotController` inherit from `BonicBotController` and support these common methods:

### Connection Management

#### Context Manager Support
```python
with create_serial_controller('/dev/ttyUSB0') as robot:
    # Robot automatically connects and disconnects
    robot.control_head(pan_angle=45)
```

#### Manual Connection Control
```python
robot = create_websocket_controller("192.168.1.100")
if robot.connect():
    # Use robot
    robot.close()
```

#### Connection Status
```python
is_connected() -> bool
```
Check if robot is currently connected.

---

## Individual Servo Control

### control_servo()

```python
control_servo(servo_id: Union[ServoID, str], angle: float, 
              speed: float = None, acceleration: float = None) -> bool
```

Control individual servo with angle validation.

**Parameters:**
- `servo_id`: Servo identifier (ServoID enum or string)
- `angle`: Target angle in degrees
- `speed`: Movement speed (default: 200.0)
- `acceleration`: Acceleration value (default: 20.0)

**Returns:** `bool` - Success status

**Angle Limits (automatically validated):**
- **Head Pan**: -90° to 90°
- **Head Tilt**: -38° to 45° 
- **Grippers**: -90° to 90°
- **Wrists**: -90° to 90°
- **Elbows**: -90° to 0°
- **Shoulder Pitch**: -45° to 180°
- **Shoulder Yaw**: -90° to 90°
- **Shoulder Roll**: -3° to 144°

**Examples:**
```python
# Using enum
robot.control_servo(ServoID.HEAD_PAN, 45.0, speed=200, acceleration=25)

# Using string
robot.control_servo('rightGripper', -30.0, speed=150)
```

---

## Group Control Methods

### Head Control

#### control_head()
```python
control_head(pan_angle: float = None, tilt_angle: float = None, 
            mode: HeadModes = None, speed: float = None) -> bool
```

Control head position and expression mode.

**Parameters:**
- `pan_angle`: Head pan angle (-90° to 90°)
- `tilt_angle`: Head tilt angle (-38° to 45°) 
- `mode`: Head expression mode (WebSocket only)
- `speed`: Movement speed

**Example:**
```python
robot.control_head(pan_angle=30, tilt_angle=15, mode=HeadModes.HAPPY, speed=150)
```

### Hand Control

#### control_right_hand()
```python
control_right_hand(gripper: float = None, wrist: float = None,
                  elbow: float = None, shoulder_pitch: float = None,
                  shoulder_yaw: float = None, shoulder_roll: float = None,
                  speed: float = None) -> bool
```

#### control_left_hand()
```python
control_left_hand(gripper: float = None, wrist: float = None,
                 elbow: float = None, shoulder_pitch: float = None,
                 shoulder_yaw: float = None, shoulder_roll: float = None,
                 speed: float = None) -> bool
```

Control all servos of one hand. Only specified parameters are moved.

**Examples:**
```python
# Move just the gripper and elbow
robot.control_right_hand(gripper=45, elbow=-30, speed=120)

# Full hand positioning
robot.control_left_hand(
    gripper=-20, wrist=15, elbow=-60,
    shoulder_pitch=90, shoulder_yaw=30, shoulder_roll=45,
    speed=150
)
```

---

## Base Movement

### Basic Movement
```python
move_forward(speed: float = 100.0, duration: float = None)
move_backward(speed: float = 100.0, duration: float = None)  
turn_left(speed: float = 100.0, duration: float = None)
turn_right(speed: float = 100.0, duration: float = None)
stop_movement()
```

**Parameters:**
- `speed`: Motor speed (0-255)
- `duration`: Optional duration in seconds (auto-stop after duration)

**Examples:**
```python
robot.move_forward(speed=80, duration=2.0)  # Move forward for 2 seconds
robot.turn_left(speed=60)  # Turn left indefinitely
robot.stop_movement()  # Stop all movement
```

---

## High-Level Convenience Methods

### Gesture Methods
```python
wave_hello(use_right_hand: bool = True, speed: float = 150.0) -> bool
look_around(speed: float = 100.0) -> bool
reset_to_home_position(speed: float = 100.0) -> bool
```

### Gripper Control
```python
open_gripper(is_right: bool = True, speed: float = None)
close_gripper(is_right: bool = True, speed: float = None)
```

**Examples:**
```python
robot.wave_hello(use_right_hand=True, speed=200)
robot.look_around(speed=120)
robot.reset_to_home_position()
```

---

## WebSocket-Exclusive Features

The following features are only available when using `WebSocketBonicBotController`:

### Head Expression Modes

#### HeadModes Enumeration
```python
class HeadModes(Enum):
    NONE = 'None'
    NORMAL = 'Normal'
    HAPPY = 'Happy'
    SAD = 'Sad'
    ANGRY = 'Angry'
    SURPRISED = 'Surprised'
    CONFUSED = 'Confused'
```

#### set_head_mode()
```python
set_head_mode(mode: HeadModes) -> bool
```

Set robot's facial expression mode.

**Example:**
```python
robot.set_head_mode(HeadModes.HAPPY)
robot.set_head_mode(HeadModes.SURPRISED)
```

### Speech Synthesis

#### speak()
```python
speak(text: str) -> bool
```

Make the robot speak using text-to-speech.

**Parameters:**
- `text`: Text to be spoken

**Example:**
```python
robot.speak("Hello! I am BonicBot, nice to meet you!")
robot.speak("I can express emotions and speak!")
```

### Sequence Control

#### get_sequences()
```python
get_sequences() -> List[SequenceInfo]
```

Get list of available motion sequences.

**Returns:** List of `SequenceInfo` objects containing:
- `id`: Sequence identifier
- `name`: Human-readable name
- `description`: Sequence description
- `step_count`: Number of steps
- `duration`: Duration in seconds
- `is_loop`: Whether sequence loops
- `created_at`: Creation timestamp
- `component_usage`: Which robot parts are used

#### Sequence Playback Control
```python
play_sequence(sequence_name: str = None, sequence_id: str = None) -> bool
stop_sequence() -> bool
pause_sequence() -> bool
resume_sequence() -> bool
jump_to_step(step_index: int) -> bool
```

#### get_sequence_status()
```python
get_sequence_status() -> SequenceStatus
```

Get current sequence playback status.

**Returns:** `SequenceStatus` object with:
- `is_playing`: Whether sequence is playing
- `is_paused`: Whether sequence is paused
- `current_sequence`: Name of current sequence
- `current_step`: Current step index
- `total_steps`: Total number of steps
- `playback_progress`: Progress as fraction (0.0-1.0)

**Examples:**
```python
# List and play sequences
sequences = robot.get_sequences()
for seq in sequences:
    print(f"{seq.name}: {seq.description}")

robot.play_sequence("greeting_wave")
status = robot.get_sequence_status()
print(f"Playing: {status.current_sequence}, Progress: {status.playback_progress:.1%}")
```

### Camera Operations

#### Camera Control
```python
start_camera_stream() -> bool
stop_camera_stream() -> bool
capture_image() -> Optional[CapturedImage]
get_camera_status() -> CameraStatus
```

#### save_captured_image()
```python
save_captured_image(captured_image: CapturedImage, filename: str)
```

Save captured image to file.

**Examples:**
```python
# Check camera and capture image
status = robot.get_camera_status()
if status.is_initialized:
    robot.start_camera_stream()
    
    image = robot.capture_image()
    if image:
        robot.save_captured_image(image, "robot_view.jpg")
        print(f"Image captured at {image.timestamp}")
    
    robot.stop_camera_stream()
```

---

## Real-Time Sensor Monitoring

### Sensor Data Access

#### get_latest_sensor_data()
```python
get_latest_sensor_data(sensor_type: str) -> Optional[Dict[str, Any]]
```

Get latest sensor reading for specified type.

**Sensor Types:**
- `'battery'`: Battery status
- `'left_hand'`: Left hand servo readings
- `'right_hand'`: Right hand servo readings  
- `'head'`: Head servo readings
- `'base'`: Base motor readings
- `'distance'`: Distance sensor reading

#### Parsed Sensor Readings
```python
get_battery_status() -> Optional[BatteryReading]
get_distance_reading() -> Optional[float]
get_hand_servo_readings(is_right: bool = True) -> Dict[str, ServoReading]
get_head_servo_readings() -> Dict[str, ServoReading]
get_base_motor_readings() -> Dict[str, MotorReading]
```

**Examples:**
```python
# Battery monitoring
battery = robot.get_battery_status()
if battery:
    print(f"Battery: {battery.soc:.1f}% ({battery.voltage:.2f}V)")

# Distance sensor
distance = robot.get_distance_reading()
if distance and distance < 200:  # Less than 20cm
    print("Obstacle detected!")

# Servo readings
hand_servos = robot.get_hand_servo_readings(is_right=True)
gripper = hand_servos.get('gripperServo')
if gripper:
    print(f"Gripper: {gripper.feedback_angle:.1f}° (temp: {gripper.temperature:.1f}°C)")
```

### Sensor Streaming

#### Start Sensor Streams
```python
start_battery_stream(interval_ms: int = 1000, callback: Callable = None) -> bool
start_right_hand_stream(interval_ms: int = 100, callback: Callable = None) -> bool
start_left_hand_stream(interval_ms: int = 100, callback: Callable = None) -> bool
start_head_stream(interval_ms: int = 100, callback: Callable = None) -> bool
start_base_stream(interval_ms: int = 100, callback: Callable = None) -> bool
start_distance_stream(interval_ms: int = 200, callback: Callable = None) -> bool
```

**Parameters:**
- `interval_ms`: Update interval in milliseconds
- `callback`: Optional callback function for real-time data

**Examples:**
```python
# Stream with callback
def battery_callback(data):
    soc = data.get('soc', 0)
    print(f"Battery: {soc:.1f}%")

robot.start_battery_stream(interval_ms=2000, callback=battery_callback)

# Stream without callback (access via get_latest_sensor_data)
robot.start_right_hand_stream(interval_ms=500)
```

### Advanced Monitoring

#### register_sensor_listener()
```python
register_sensor_listener(sensor_type: str, listener_id: str, 
                        callback: Callable, data_filter: Callable = None) -> bool
```

Register a listener for specific sensor data with optional filtering.

#### Predefined Monitoring
```python
monitor_servo_temperature(threshold: float = 60.0, callback: Callable = None)
monitor_battery_level(low_threshold: float = 20.0, callback: Callable = None)  
monitor_servo_errors(callback: Callable = None)
start_comprehensive_monitoring(callbacks: Dict[str, Callable] = None)
```

**Examples:**
```python
# Temperature monitoring
def temp_alert(servo_name, temp):
    print(f"WARNING: {servo_name} temperature {temp:.1f}°C")
    robot.speak(f"Warning: {servo_name} overheating")

robot.monitor_servo_temperature(threshold=55.0, callback=temp_alert)

# Comprehensive monitoring
callbacks = {
    'temperature': temp_alert,
    'battery': lambda soc: print(f"Low battery: {soc:.1f}%"),
    'errors': lambda name, data: print(f"Servo error: {name}")
}
robot.start_comprehensive_monitoring(callbacks)
```

---

## Data Classes

### Command Classes

#### HandCommand
```python
@dataclass
class HandCommand:
    shoulder_pitch: float = 0.0
    shoulder_yaw: float = 0.0
    shoulder_roll: float = 0.0
    elbow: float = 0.0
    wrist: float = 0.0
    gripper: float = 0.0
    speed: float = 200.0
    acceleration: float = 20.0
```

#### HeadCommand
```python
@dataclass  
class HeadCommand:
    pan: float = 0.0
    tilt: float = 0.0
    mode: HeadModes = HeadModes.NONE
    speed: float = 200.0
    acceleration: float = 20.0
```

#### BaseCommand
```python
@dataclass
class BaseCommand:
    left_motor_speed: float = 0.0
    right_motor_speed: float = 0.0
    motor_type: MotorType = MotorType.GEAR_MOTOR
```

### Composite Control Methods (WebSocket Only)
```python
control_head_composite(head_cmd: HeadCommand) -> bool
control_left_hand_composite(hand_cmd: HandCommand) -> bool  
control_right_hand_composite(hand_cmd: HandCommand) -> bool
control_base_composite(base_cmd: BaseCommand) -> bool
```

**Examples:**
```python
# Complex head control
head_cmd = HeadCommand(
    pan=30, tilt=15, 
    mode=HeadModes.HAPPY,
    speed=150, acceleration=25
)
robot.control_head_composite(head_cmd)

# Complex hand positioning  
hand_cmd = HandCommand(
    shoulder_pitch=-90, shoulder_yaw=30,
    elbow_angle=45, wrist_angle=20,
    gripper_angle=60, speed=120
)
robot.control_right_hand_composite(hand_cmd)
```

### Reading Classes

#### ServoReading
```python
@dataclass
class ServoReading:
    id: str
    name: str
    feedback_angle: float
    feedback_speed: float
    load: float
    temperature: float
    has_error: bool
```

#### BatteryReading
```python
@dataclass
class BatteryReading:
    voltage: float
    current: float
    soc: float  # State of charge percentage
    temperature: float
    has_error: bool
    error_message: str
```

#### MotorReading
```python
@dataclass
class MotorReading:
    id: str
    feedback_speed: float
    feedback_position: float
    torque: float
    temperature: float
    mode: int
    has_error: bool
```

---

## System Status and Diagnostics

### System Summary
```python
get_sensor_summary() -> Dict[str, Any]
```

Get comprehensive system status including all sensors, sequence status, and camera status.

### Sensor History
```python
get_sensor_history(sensor_type: str, limit: int = 10) -> List[Dict[str, Any]]
```

Get historical sensor data (last N readings).

### Data Age Checking
```python
is_sensor_data_recent(sensor_type: str, max_age_seconds: float = 5.0) -> bool
get_sensor_data_age(sensor_type: str) -> Optional[float]
```

**Examples:**
```python
# System overview
summary = robot.get_sensor_summary()
print(f"Robot online: {summary['robot_connected']}")
print(f"Sequence playing: {summary['sequence_status']['is_playing']}")

# Check data freshness
if robot.is_sensor_data_recent('battery', max_age_seconds=10):
    battery = robot.get_battery_status()
    print(f"Recent battery reading: {battery.soc:.1f}%")
```

---

## Error Handling and Safety

### Exception Types
- `ConnectionError`: Communication failures
- `ValueError`: Invalid parameters or servo IDs
- `RuntimeError`: Command transmission failures

### Safety Features
- **Automatic angle validation** for all servos
- **Temperature monitoring** with alerts
- **Battery level monitoring** 
- **Servo error detection** and reporting
- **Connection state monitoring**

### Best Practices

```python
try:
    with create_websocket_controller("192.168.1.100") as robot:
        if not robot.is_connected():
            raise ConnectionError("Failed to connect")
        
        # Setup safety monitoring
        robot.monitor_servo_temperature(threshold=55.0)
        robot.monitor_battery_level(low_threshold=20.0)
        
        # Perform operations
        robot.speak("Starting operations")
        robot.control_head(pan_angle=45, tilt_angle=20)
        
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Emergency stop if needed
    if 'robot' in locals():
        robot.stop_movement()
        robot.reset_to_home_position()
```

---

## Advanced Features

### Listener Management
```python
register_sensor_listener(sensor_type: str, listener_id: str, callback: Callable, data_filter: Callable = None) -> bool
unregister_sensor_listener(sensor_type: str, listener_id: str) -> bool
clear_all_listeners()
```

### Robot Status Checking
```python
is_robot_online() -> bool
get_robot_status() -> Dict[str, Any]
```

### Utility Methods
```python
get_sensor_data_age(sensor_type: str) -> Optional[float]
is_sensor_data_recent(sensor_type: str, max_age_seconds: float = 5.0) -> bool
```

---

## Communication Protocols

### Serial Protocol
Simple text-based commands for basic robot control.

### WebSocket Protocol  
JSON-based bidirectional communication supporting:
- Real-time sensor streaming
- Sequence control
- Camera operations
- Speech synthesis
- Advanced monitoring

**WebSocket Message Structure:**
```json
{
    "commandType": "command|request",
    "dataType": "servo|head|lefthand|righthand|base|sequence|camera|speak",
    "payload": {
        // Command-specific data
    },
    "interval": 0
}
```

---

## Migration from v1.x

### Breaking Changes
- Constructor signature changed
- WebSocket features require separate controller
- Some method names updated for consistency

### Migration Example
```python
# Old v1.x code
bot = BonicBotController('/dev/ttyUSB0')
bot.control_servo('headPan', angle=45.0, speed=200, acc=20)

# New v2.x code  
bot = create_serial_controller('/dev/ttyUSB0')
bot.control_servo('headPan', angle=45.0, speed=200, acceleration=20)
```

---

## Complete Example

```python
from bonicbot import (
    create_websocket_controller, 
    HeadModes, 
    HandCommand,
    HeadCommand
)

def main():
    try:
        with create_websocket_controller("192.168.1.100") as robot:
            # Setup monitoring
            robot.start_comprehensive_monitoring({
                'temperature': lambda name, temp: print(f"Temp alert: {name}"),
                'battery': lambda soc: print(f"Battery: {soc:.1f}%")
            })
            
            # Speech and expressions
            robot.speak("Hello! I am BonicBot version 2!")
            robot.set_head_mode(HeadModes.HAPPY)
            
            # Complex movements
            robot.wave_hello(use_right_hand=True, speed=150)
            robot.look_around(speed=120)
            
            # Sequence control
            sequences = robot.get_sequences()
            if sequences:
                robot.play_sequence(sequences[0].name)
            
            # Camera operations
            if robot.get_camera_status().is_initialized:
                image = robot.capture_image()
                if image:
                    robot.save_captured_image(image, "selfie.jpg")
            
            # Composite control
            head_cmd = HeadCommand(pan=30, tilt=15, mode=HeadModes.SURPRISED)
            robot.control_head_composite(head_cmd)
            
            # Final speech
            robot.speak("Demonstration completed successfully!")
            robot.reset_to_home_position()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

This documentation covers the complete BonicBot API v2.0.1 with all advanced features!