"""
BonicBot Python Library

A comprehensive Python library for controlling BonicBot humanoid robots 
via serial communication and WebSocket with sequence and camera support.

Main Components:
- BonicBotController: Core controller class for robot communication
- SerialBonicBotController: Serial communication implementation
- WebSocketBonicBotController: WebSocket communication with enhanced monitoring, sequences, and camera
- BonicBotGUI: Graphical user interface for robot control (optional)
- ServoID: Enumeration of available servo identifiers
- HeadModes: Head expression modes
- Command classes: ServoCommand, HeadCommand, HandCommand, BaseCommand
- Reading classes: ServoReading, BatteryReading, MotorReading
- Sequence classes: SequenceInfo, SequenceStatus
- Camera classes: CameraStatus, CapturedImage

Example:
    Basic usage:
    
    >>> from bonicbot import create_serial_controller
    >>> robot = create_serial_controller('/dev/ttyUSB0')
    >>> robot.control_head(pan_angle=45.0)
    >>> robot.close()
    
    WebSocket with enhanced monitoring, sequences, and camera:
    
    >>> from bonicbot import create_websocket_controller, HeadModes
    >>> robot = create_websocket_controller('192.168.1.100', 8080)
    >>> robot.set_head_mode(HeadModes.HAPPY)
    >>> robot.speak("Hello, I am BonicBot!")
    >>> sequences = robot.get_sequences()
    >>> robot.play_sequence("wave_sequence")
    >>> image = robot.capture_image()
    >>> robot.close()
    
    With context manager:
    
    >>> with create_serial_controller('/dev/ttyUSB0') as robot:
    ...     robot.move_forward(speed=100)
"""

__version__ = "2.0.1"
__author__ = "Shahir Abdulla"
__email__ = "shahir@autobonics.com"
__license__ = "MIT"
__description__ = "Python library for controlling BonicBot humanoid robot via serial and WebSocket communication with sequence and camera support"

from .controller import (
    # Core controller classes
    BonicBotController,
    SerialBonicBotController,
    WebSocketBonicBotController,
    
    # Factory functions
    create_serial_controller,
    create_websocket_controller,
    
    # Enums
    ServoID,
    CommunicationType,
    HeadModes,
    VideoStreamMode,
    MotorType,
    SequenceAction,
    CameraAction,
    
    # Command classes
    ServoCommand,
    HeadCommand,
    HandCommand,
    BaseCommand,
    
    # Reading/sensor data classes
    ServoReading,
    BatteryReading,
    MotorReading,
    
    # Sequence classes
    SequenceInfo,
    SequenceStatus,
    
    # Camera classes
    CameraStatus,
    CapturedImage,
    
    # Constants
    ServoConstants,
)

# Try to import GUI components (optional)
try:
    __all__ = [
        # Core controllers
        "BonicBotController",
        "SerialBonicBotController", 
        "WebSocketBonicBotController",
        
        # Factory functions
        "create_serial_controller",
        "create_websocket_controller",
        
        # Enums
        "ServoID",
        "CommunicationType",
        "HeadModes",
        "VideoStreamMode", 
        "MotorType",
        "SequenceAction",
        "CameraAction",
        
        # Command classes
        "ServoCommand",
        "HeadCommand",
        "HandCommand", 
        "BaseCommand",
        
        # Reading classes
        "ServoReading",
        "BatteryReading",
        "MotorReading",
        
        # Sequence classes
        "SequenceInfo",
        "SequenceStatus",
        
        # Camera classes
        "CameraStatus",
        "CapturedImage",
        
        # Constants
        "ServoConstants",
        
        # GUI (available)
        "BonicBotGUI",
        "run_servo_controller",
        "is_gui_available",
    ]
except ImportError as e:
    # GUI not available (likely missing tkinter)
    __all__ = [
        # Core controllers
        "BonicBotController",
        "SerialBonicBotController",
        "WebSocketBonicBotController", 
        
        # Factory functions
        "create_serial_controller",
        "create_websocket_controller",
        
        # Enums
        "ServoID",
        "CommunicationType", 
        "HeadModes",
        "VideoStreamMode",
        "MotorType",
        "SequenceAction",
        "CameraAction",
        
        # Command classes
        "ServoCommand",
        "HeadCommand",
        "HandCommand",
        "BaseCommand",
        
        # Reading classes
        "ServoReading", 
        "BatteryReading",
        "MotorReading",
        
        # Sequence classes
        "SequenceInfo",
        "SequenceStatus",
        
        # Camera classes
        "CameraStatus",
        "CapturedImage",
        
        # Constants
        "ServoConstants",
        
    ]
    
    def run_servo_controller(*args, **kwargs):
        raise ImportError(
            "GUI functionality requires tkinter. Install it with:\n"
            "  Ubuntu/Debian: sudo apt-get install python3-tk\n"
            "  CentOS/RHEL: sudo yum install python3-tkinter\n"
            "  Fedora: sudo dnf install python3-tkinter\n"
            "  macOS: brew install python-tk\n"
            "  Windows: Reinstall Python with tkinter support"
        )


