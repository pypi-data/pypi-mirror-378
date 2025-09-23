#!/usr/bin/env python3
"""
Comprehensive unit tests for BonicBot Controller v2.0

These tests verify the functionality of both Serial and WebSocket 
implementations of the BonicBot controller without requiring actual hardware.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import time
import asyncio
import threading
from datetime import datetime

# Import all the classes we need to test
from bonicbot.controller import (
    # Core controller classes
    BonicBotController, SerialBonicBotController, WebSocketBonicBotController,
    create_serial_controller, create_websocket_controller,
    
    # Enums
    ServoID, CommunicationType, HeadModes, VideoStreamMode, 
    MotorType, SequenceAction, CameraAction,
    
    # Command classes
    ServoCommand, HeadCommand, HandCommand, BaseCommand,
    
    # Reading classes
    ServoReading, BatteryReading, MotorReading,
    
    # Sequence and camera classes
    SequenceInfo, SequenceStatus, CameraStatus, CapturedImage,
    
    # Constants
    ServoConstants
)


class TestServoCommand(unittest.TestCase):
    """Test ServoCommand data class and validation."""
    
    def test_servo_command_creation(self):
        """Test creating a servo command."""
        cmd = ServoCommand(
            id="headPan",
            angle=45.0,
            speed=200.0,
            acc=20.0
        )
        
        self.assertEqual(cmd.id, "headPan")
        self.assertEqual(cmd.angle, 45.0)
        self.assertEqual(cmd.speed, 200.0)
        self.assertEqual(cmd.acc, 20.0)
    
    def test_servo_command_defaults(self):
        """Test servo command with default values."""
        cmd = ServoCommand(id="headTilt", angle=30.0)
        
        self.assertEqual(cmd.speed, ServoConstants.DEFAULT_SPEED)
        self.assertEqual(cmd.acc, ServoConstants.DEFAULT_ACCELERATION)
    
    def test_angle_validation(self):
        """Test servo angle validation."""
        # Valid angle for head pan
        cmd = ServoCommand(id=ServoID.HEAD_PAN.value, angle=45.0)
        self.assertTrue(cmd.validate_angle())
        
        # Invalid angle for head pan (out of range)
        cmd = ServoCommand(id=ServoID.HEAD_PAN.value, angle=120.0)  # Max is 90
        self.assertFalse(cmd.validate_angle())
        
        # Valid angle for right elbow
        cmd = ServoCommand(id=ServoID.RIGHT_ELBOW.value, angle=-45.0)
        self.assertTrue(cmd.validate_angle())


class TestEnums(unittest.TestCase):
    """Test all enum definitions."""
    
    def test_servo_id_values(self):
        """Test that all servo IDs have correct string values."""
        expected_values = {
            ServoID.HEAD_PAN: "headPan",
            ServoID.HEAD_TILT: "headTilt",
            ServoID.LEFT_GRIPPER: "leftGripper",
            ServoID.RIGHT_GRIPPER: "rightGripper",
            ServoID.LEFT_SHOULDER_PITCH: "leftSholderPitch",
            ServoID.RIGHT_SHOULDER_PITCH: "rightSholderPitch",
        }
        
        for servo_id, expected_value in expected_values.items():
            self.assertEqual(servo_id.value, expected_value)
    
    def test_head_modes(self):
        """Test head mode enum values."""
        self.assertEqual(HeadModes.NONE.value, 'None')
        self.assertEqual(HeadModes.HAPPY.value, 'Happy')
        self.assertEqual(HeadModes.SAD.value, 'Sad')
    
    def test_communication_type(self):
        """Test communication type enum."""
        self.assertEqual(CommunicationType.SERIAL.value, 'serial')
        self.assertEqual(CommunicationType.WEBSOCKET.value, 'websocket')


class TestSerialBonicBotController(unittest.TestCase):
    """Test SerialBonicBotController implementation."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_serial_patcher = patch('bonicbot.controller.serial.Serial')
        self.mock_serial = self.mock_serial_patcher.start()
        
        # Configure mock serial instance
        self.mock_serial_instance = Mock()
        self.mock_serial_instance.is_open = True
        self.mock_serial_instance.write = Mock()
        self.mock_serial_instance.flush = Mock()
        self.mock_serial_instance.close = Mock()
        self.mock_serial_instance.in_waiting = 0
        self.mock_serial.return_value = self.mock_serial_instance
        
        # Create controller instance
        self.controller = SerialBonicBotController('/dev/ttyUSB0')
    
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_serial_patcher.stop()
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.port, '/dev/ttyUSB0')
        self.assertEqual(self.controller.baudrate, 115200)
        self.assertEqual(self.controller.timeout, 1.0)
        self.assertEqual(self.controller.communication_type, CommunicationType.SERIAL)
    
    def test_connection(self):
        """Test connection establishment."""
        result = self.controller.connect()
        
        self.assertTrue(result)
        self.assertTrue(self.controller.is_connected())
        self.mock_serial.assert_called_once_with(
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=1.0
        )
    
    def test_connection_failure(self):
        """Test connection failure handling."""
        self.mock_serial.side_effect = Exception("Connection failed")
        
        result = self.controller.connect()
        
        self.assertFalse(result)
        self.assertFalse(self.controller.is_connected())
    
    def test_servo_control_with_string_id(self):
        """Test individual servo control with string ID."""
        self.controller.connect()
        result = self.controller.control_servo('headPan', 45.0, 200, 20)
        
        self.assertTrue(result)
        self.mock_serial_instance.write.assert_called_once()
        written_data = self.mock_serial_instance.write.call_args[0][0]
        expected_command = "SERVO:headPan:45.0:200:20\n"
        self.assertEqual(written_data.decode('utf-8'), expected_command)
    
    def test_servo_control_with_enum_id(self):
        """Test individual servo control with ServoID enum."""
        self.controller.connect()
        result = self.controller.control_servo(ServoID.HEAD_TILT, -10.0, 150, 30)
        
        self.assertTrue(result)
        written_data = self.mock_serial_instance.write.call_args[0][0]
        expected_command = "SERVO:headTilt:-10.0:150:30\n"
        self.assertEqual(written_data.decode('utf-8'), expected_command)
    
    def test_head_control(self):
        """Test head control method."""
        self.controller.connect()
        result = self.controller.control_head(pan_angle=30.0, tilt_angle=-15.0)
        
        self.assertTrue(result)
        # Should have made two servo calls
        self.assertEqual(self.mock_serial_instance.write.call_count, 2)
    
    def test_hand_control(self):
        """Test hand control methods."""
        self.controller.connect()
        
        # Test right hand control
        result = self.controller.control_right_hand(gripper=90.0, elbow=-45.0)
        self.assertTrue(result)
        
        # Reset mock for left hand test
        self.mock_serial_instance.write.reset_mock()
        
        # Test left hand control
        result = self.controller.control_left_hand(gripper=-30.0)
        self.assertTrue(result)
    
    def test_base_movement(self):
        """Test base movement control."""
        self.controller.connect()
        
        # Test direct base control
        result = self.controller._move_base(100, -50)
        self.assertTrue(result)
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        expected_command = "BASE:100:-50\n"
        self.assertEqual(written_data.decode('utf-8'), expected_command)
    
    def test_movement_methods(self):
        """Test convenience movement methods."""
        self.controller.connect()
        
        # Test forward movement
        result = self.controller.move_forward(150)
        self.assertTrue(result)
        
        # Test turn left
        self.mock_serial_instance.write.reset_mock()
        result = self.controller.turn_left(100)
        self.assertTrue(result)
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        expected_command = "BASE:-100:100\n"
        self.assertEqual(written_data.decode('utf-8'), expected_command)
    
    def test_head_mode_setting(self):
        """Test setting head expression mode."""
        self.controller.connect()
        result = self.controller._set_head_mode(HeadModes.HAPPY)
        
        self.assertTrue(result)
        written_data = self.mock_serial_instance.write.call_args[0][0]
        expected_command = "HEAD_MODE:Happy\n"
        self.assertEqual(written_data.decode('utf-8'), expected_command)
    
    def test_sensor_data_reading(self):
        """Test reading sensor data."""
        self.controller.connect()
        
        # Test with no data
        self.mock_serial_instance.in_waiting = 0
        result = self.controller.read_sensor_data()
        self.assertIsNone(result)
        
        # Test with data available
        self.mock_serial_instance.in_waiting = 10
        self.mock_serial_instance.readline.return_value = b"sensor:data\n"
        result = self.controller.read_sensor_data()
        self.assertEqual(result, "sensor:data")
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with patch('bonicbot.controller.serial.Serial') as mock_serial:
            mock_instance = Mock()
            mock_instance.is_open = True
            mock_serial.return_value = mock_instance
            
            with SerialBonicBotController('/dev/ttyUSB0') as bot:
                bot.connect()
                self.assertIsNotNone(bot)
            
            # Verify close was called
            mock_instance.close.assert_called_once()
    
    def test_unsupported_operations(self):
        """Test operations not supported in serial mode."""
        self.controller.connect()
        
        # These should return False or empty results
        self.assertFalse(self.controller.speak("Hello"))
        self.assertEqual(len(self.controller.get_sequences()), 0)


class TestWebSocketBonicBotController(unittest.TestCase):
    """Test WebSocketBonicBotController implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WebSocketBonicBotController('localhost', 8080)
        
        # Mock websocket
        self.mock_websocket = AsyncMock()
        self.mock_websockets_patcher = patch('bonicbot.controller.websockets.connect')
        self.mock_websockets_connect = self.mock_websockets_patcher.start()
        self.mock_websockets_connect.return_value = self.mock_websocket
    
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_websockets_patcher.stop()
        if self.controller.connected:
            self.controller.close()
    
    def test_controller_initialization(self):
        """Test WebSocket controller initialization."""
        self.assertEqual(self.controller.host, 'localhost')
        self.assertEqual(self.controller.port, 8080)
        self.assertEqual(self.controller.communication_type, CommunicationType.WEBSOCKET)
        self.assertFalse(self.controller.is_connected())
    
    def test_servo_command_creation(self):
        """Test servo command creation for WebSocket."""
        cmd = ServoCommand(id="headPan", angle=45.0, speed=200.0, acc=20.0)
        
        # Simulate connected state for command sending
        self.controller.connected = True
        self.controller._loop = Mock()
        
        # Mock the async command sending
        future_mock = Mock()
        future_mock.result.return_value = True
        self.controller._loop.is_closed.return_value = False
        
        with patch('asyncio.run_coroutine_threadsafe', return_value=future_mock):
            result = self.controller._send_servo_command(cmd)
            self.assertTrue(result)
    
    def test_sequence_status_initialization(self):
        """Test sequence status is properly initialized."""
        status = self.controller.sequence_status
        
        self.assertFalse(status.is_playing)
        self.assertFalse(status.is_paused)
        self.assertFalse(status.is_recording)
        self.assertIsNone(status.current_sequence)
        self.assertEqual(status.current_step, 0)
        self.assertEqual(status.total_steps, 0)
        self.assertEqual(status.playback_progress, 0.0)
    
    def test_camera_status_initialization(self):
        """Test camera status is properly initialized."""
        status = self.controller.camera_status
        
        self.assertFalse(status.is_streaming)
        self.assertFalse(status.is_initialized)
        self.assertEqual(status.connected_clients, 0)
        self.assertIsNone(status.stream_url)
    
    def test_sensor_data_storage(self):
        """Test sensor data storage mechanism."""
        # Test data storage
        test_data = {'voltage': 12.5, 'current': 1.2}
        self.controller._store_sensor_data('battery', test_data)
        
        # Verify data was stored
        stored_data = self.controller.get_latest_sensor_data('battery')
        self.assertIsNotNone(stored_data)
        self.assertEqual(stored_data['data'], test_data)
        self.assertIn('timestamp', stored_data)
    
    def test_sensor_listener_registration(self):
        """Test sensor listener registration."""
        callback = Mock()
        
        result = self.controller.register_sensor_listener(
            'battery', 'test_listener', callback
        )
        
        self.assertTrue(result)
        self.assertIn('battery', self.controller.sensor_listeners)
        self.assertIn('test_listener', self.controller.sensor_listeners['battery'])
    
    def test_battery_reading_parsing(self):
        """Test battery reading parsing."""
        # Store some battery data
        battery_data = {
            'voltage': 12.5,
            'current': 1.2,
            'soc': 85.0,
            'temperature': 25.5,
            'hasError': False,
            'errorMessage': ''
        }
        self.controller._store_sensor_data('battery', battery_data)
        
        # Get parsed battery reading
        reading = self.controller.get_battery_status()
        
        self.assertIsNotNone(reading)
        self.assertEqual(reading.voltage, 12.5)
        self.assertEqual(reading.current, 1.2)
        self.assertEqual(reading.soc, 85.0)
        self.assertEqual(reading.temperature, 25.5)
        self.assertFalse(reading.has_error)
    
    def test_distance_reading(self):
        """Test distance sensor reading."""
        # Store distance data
        distance_data = {'distance': 150.5}
        self.controller._store_sensor_data('distance', distance_data)
        
        # Get distance reading
        distance = self.controller.get_distance_reading()
        
        self.assertEqual(distance, 150.5)
    
    def test_sequence_operations(self):
        """Test sequence control operations."""
        # Mock connected state
        self.controller.connected = True
        self.controller._loop = Mock()
        
        future_mock = Mock()
        future_mock.result.return_value = True
        
        with patch('asyncio.run_coroutine_threadsafe', return_value=future_mock):
            # Test play sequence
            result = self.controller.play_sequence("test_sequence")
            self.assertTrue(result)
            
            # Test stop sequence
            result = self.controller.stop_sequence()
            self.assertTrue(result)
            
            # Test pause sequence
            result = self.controller.pause_sequence()
            self.assertTrue(result)
            
            # Test resume sequence
            result = self.controller.resume_sequence()
            self.assertTrue(result)
    
    def test_camera_operations(self):
        """Test camera control operations."""
        # Mock connected state
        self.controller.connected = True
        self.controller._loop = Mock()
        
        future_mock = Mock()
        future_mock.result.return_value = True
        
        with patch('asyncio.run_coroutine_threadsafe', return_value=future_mock):
            # Test start camera stream
            result = self.controller.start_camera_stream()
            self.assertTrue(result)
            
            # Test stop camera stream
            result = self.controller.stop_camera_stream()
            self.assertTrue(result)
    
    def test_speaking_functionality(self):
        """Test TTS/speaking functionality."""
        # Mock connected state
        self.controller.connected = True
        self.controller._loop = Mock()
        
        future_mock = Mock()
        future_mock.result.return_value = True
        
        with patch('asyncio.run_coroutine_threadsafe', return_value=future_mock):
            # Test speaking
            result = self.controller.speak("Hello, world!")
            self.assertTrue(result)
            
            # Test empty text
            result = self.controller.speak("")
            self.assertFalse(result)
    
    def test_high_level_movements(self):
        """Test high-level movement methods."""
        # Mock connected state and async operations
        self.controller.connected = True
        self.controller._loop = Mock()
        
        future_mock = Mock()
        future_mock.result.return_value = True
        
        with patch('asyncio.run_coroutine_threadsafe', return_value=future_mock):
            with patch('time.sleep'):  # Mock sleep to speed up tests
                # Test wave hello
                result = self.controller.wave_hello(use_right_hand=True)
                self.assertTrue(result)
                
                # Test look around
                result = self.controller.look_around()
                self.assertTrue(result)
                
                # Test reset to home position
                result = self.controller.reset_to_home_position()
                self.assertTrue(result)
    
    def test_sensor_monitoring(self):
        """Test sensor monitoring features."""
        # Test temperature monitoring
        temp_callback = Mock()
        self.controller.monitor_servo_temperature(threshold=50.0, callback=temp_callback)
        
        # Test battery monitoring
        battery_callback = Mock()
        self.controller.monitor_battery_level(low_threshold=20.0, callback=battery_callback)
        
        # Test error monitoring
        error_callback = Mock()
        self.controller.monitor_servo_errors(callback=error_callback)
        
        # Verify listeners were registered
        self.assertIn('left_hand', self.controller.sensor_listeners)
        self.assertIn('right_hand', self.controller.sensor_listeners)
        self.assertIn('battery', self.controller.sensor_listeners)
    
    def test_sensor_summary(self):
        """Test sensor summary generation."""
        # Add some test data
        self.controller._store_sensor_data('battery', {'voltage': 12.0})
        self.controller._store_sensor_data('distance', {'distance': 100})
        
        summary = self.controller.get_sensor_summary()
        
        self.assertIn('timestamp', summary)
        self.assertIn('sensors', summary)
        self.assertIn('battery', summary['sensors'])
        self.assertIn('distance', summary['sensors'])
        self.assertTrue(summary['sensors']['battery']['has_data'])
        self.assertTrue(summary['sensors']['distance']['has_data'])


class TestFactoryFunctions(unittest.TestCase):
    """Test factory functions for creating controllers."""
    
    @patch('bonicbot.controller.serial.Serial')
    def test_create_serial_controller(self, mock_serial):
        """Test creating serial controller via factory."""
        mock_serial.return_value.is_open = True
        
        controller = create_serial_controller('/dev/ttyUSB0', 9600, 2.0)
        
        self.assertIsInstance(controller, SerialBonicBotController)
        self.assertEqual(controller.port, '/dev/ttyUSB0')
        self.assertEqual(controller.baudrate, 9600)
        self.assertEqual(controller.timeout, 2.0)
    
    def test_create_websocket_controller(self):
        """Test creating WebSocket controller via factory."""
        controller = create_websocket_controller('192.168.1.100', 9090)
        
        self.assertIsInstance(controller, WebSocketBonicBotController)
        self.assertEqual(controller.host, '192.168.1.100')
        self.assertEqual(controller.port, 9090)
    
    @patch('bonicbot.controller.serial.Serial')
    def test_legacy_constructor_serial_detection(self, mock_serial):
        """Test legacy constructor auto-detects serial communication."""
        mock_serial.return_value.is_open = True
        
        # Should auto-detect as serial due to path-like port
        controller = BonicBotController('/dev/ttyUSB0', 115200)
        
        self.assertIsInstance(controller, SerialBonicBotController)
    
    def test_legacy_constructor_websocket_detection(self):
        """Test legacy constructor auto-detects WebSocket communication."""
        # Should auto-detect as WebSocket due to port number
        controller = BonicBotController('localhost', 8080)
        
        self.assertIsInstance(controller, WebSocketBonicBotController)


class TestDataClasses(unittest.TestCase):
    """Test data classes for commands and readings."""
    
    def test_head_command(self):
        """Test HeadCommand data class."""
        cmd = HeadCommand(pan=45.0, tilt=-30.0, mode=HeadModes.HAPPY)
        
        self.assertEqual(cmd.pan, 45.0)
        self.assertEqual(cmd.tilt, -30.0)
        self.assertEqual(cmd.mode, HeadModes.HAPPY)
        self.assertEqual(cmd.speed, ServoConstants.DEFAULT_SPEED)
    
    def test_hand_command(self):
        """Test HandCommand data class."""
        cmd = HandCommand(
            shoulder_pitch=90.0,
            elbow=-45.0,
            gripper=30.0,
            speed=150.0
        )
        
        self.assertEqual(cmd.shoulder_pitch, 90.0)
        self.assertEqual(cmd.elbow, -45.0)
        self.assertEqual(cmd.gripper, 30.0)
        self.assertEqual(cmd.speed, 150.0)
    
    def test_base_command(self):
        """Test BaseCommand data class."""
        cmd = BaseCommand(
            left_motor_speed=100.0,
            right_motor_speed=-50.0,
            motor_type=MotorType.DDSM115
        )
        
        self.assertEqual(cmd.left_motor_speed, 100.0)
        self.assertEqual(cmd.right_motor_speed, -50.0)
        self.assertEqual(cmd.motor_type, MotorType.DDSM115)
    
    def test_servo_reading(self):
        """Test ServoReading data class."""
        reading = ServoReading(
            id="headPan",
            name="Head Pan Servo",
            feedback_angle=45.0,
            feedback_speed=0.0,
            load=0.2,
            temperature=35.5,
            has_error=False
        )
        
        self.assertEqual(reading.id, "headPan")
        self.assertEqual(reading.name, "Head Pan Servo")
        self.assertEqual(reading.feedback_angle, 45.0)
        self.assertFalse(reading.has_error)
    
    def test_sequence_info(self):
        """Test SequenceInfo data class."""
        seq_info = SequenceInfo(
            id="seq001",
            name="Wave Sequence",
            description="A friendly wave gesture",
            step_count=10,
            duration=5000,
            is_loop=False,
            created_at="2024-01-01T12:00:00Z",
            component_usage={'head': True, 'rightHand': True}
        )
        
        self.assertEqual(seq_info.id, "seq001")
        self.assertEqual(seq_info.name, "Wave Sequence")
        self.assertEqual(seq_info.step_count, 10)
        self.assertFalse(seq_info.is_loop)
        self.assertTrue(seq_info.component_usage['head'])
    
    def test_captured_image(self):
        """Test CapturedImage data class."""
        image = CapturedImage(
            image_data="base64encodeddata",
            format="jpeg",
            timestamp="2024-01-01T12:00:00Z"
        )
        
        self.assertEqual(image.image_data, "base64encodeddata")
        self.assertEqual(image.format, "jpeg")
        self.assertEqual(image.timestamp, "2024-01-01T12:00:00Z")


class TestConstants(unittest.TestCase):
    """Test servo constants and limits."""
    
    def test_default_values(self):
        """Test default servo values."""
        self.assertEqual(ServoConstants.DEFAULT_ANGLE, 0.0)
        self.assertEqual(ServoConstants.DEFAULT_SPEED, 200.0)
        self.assertEqual(ServoConstants.DEFAULT_ACCELERATION, 20.0)
    
    def test_servo_limits(self):
        """Test servo angle limits."""
        # Head limits
        self.assertEqual(ServoConstants.HEAD_PAN_MIN, -90.0)
        self.assertEqual(ServoConstants.HEAD_PAN_MAX, 90.0)
        self.assertEqual(ServoConstants.HEAD_TILT_MIN, -38.0)
        self.assertEqual(ServoConstants.HEAD_TILT_MAX, 45.0)
        
        # Right hand limits
        self.assertEqual(ServoConstants.RIGHT_GRIPPER_MIN, -90.0)
        self.assertEqual(ServoConstants.RIGHT_GRIPPER_MAX, 90.0)
        self.assertEqual(ServoConstants.RIGHT_ELBOW_MIN, -90.0)
        self.assertEqual(ServoConstants.RIGHT_ELBOW_MAX, 0.0)


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)