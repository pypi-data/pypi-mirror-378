#!/usr/bin/env python3
"""
BonicBot GUI Controller - CustomTkinter Enhanced Version

A modern, visually appealing GUI for controlling BonicBot servos and base motors.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import json

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"

class ServoLimits:
    """Servo angle limits based on the C++ code"""
    LIMITS = {
        "rightGripper": (-90.0, 90.0),
        "rightWrist": (-90.0, 90.0),
        "rightElbow": (-90.0, 0.0),
        "rightSholderPitch": (-45.0, 180.0),
        "rightSholderYaw": (-90.0, 90.0),
        "rightSholderRoll": (-3.0, 144.0),
        "leftGripper": (-90.0, 90.0),
        "leftWrist": (-90.0, 90.0),
        "leftElbow": (-90.0, 0.0),
        "leftSholderPitch": (-45.0, 180.0),
        "leftSholderYaw": (-90.0, 90.0),
        "leftSholderRoll": (-3.0, 144.0),
        "headPan": (-90.0, 90.0),
        "headTilt": (-38.0, 45.0)
    }
    
    @classmethod
    def get_limits(cls, servo_id):
        return cls.LIMITS.get(servo_id, (-90.0, 90.0))

class BonicBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 BonicBot Controller")
        self.root.geometry("1200x800")
        
        # Controller instance
        self.controller = None
        self.connected = False
        
        # Communication variables
        self.comm_type_var = ctk.StringVar(value="serial")
        self.port_var = ctk.StringVar(value="/dev/ttyUSB0")
        self.websocket_uri_var = ctk.StringVar(value="ws://192.168.1.100:8080/control")
        self.baudrate_var = ctk.StringVar(value="115200")
        
        # Create GUI elements
        self.create_widgets()
        
        # Initialize UI state
        self.on_comm_type_change()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create connection frame first
        self.create_connection_frame()
        
        # Main tabview for different controls
        self.tabview = ctk.CTkTabview(self.main_container, height=600)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        
        # Add tabs
        self.tabview.add("🦾 Individual Servos")
        self.tabview.add("👤 Head Control")
        self.tabview.add("👈 Left Hand")
        self.tabview.add("👉 Right Hand")
        self.tabview.add("🚶 Base Control")
        # self.tabview.add("📋 Presets")
        
        # Create tab contents
        self.create_servo_tab()
        self.create_head_tab()
        self.create_left_hand_tab()
        self.create_right_hand_tab()
        self.create_base_tab()
        
    def create_connection_frame(self):
        """Create modern connection control frame"""
        conn_frame = ctk.CTkFrame(self.main_container)
        conn_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title
        title_label = ctk.CTkLabel(conn_frame, text="🔗 Connection Settings", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(10, 5))
        
        # Main connection container
        connection_container = ctk.CTkFrame(conn_frame)
        connection_container.pack(fill="x", padx=20, pady=(5, 15))
        
        # Communication type selection
        comm_frame = ctk.CTkFrame(connection_container)
        comm_frame.pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(comm_frame, text="Communication Type:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        self.comm_radio_frame = ctk.CTkFrame(comm_frame)
        self.comm_radio_frame.pack(pady=5)
        
        self.serial_radio = ctk.CTkRadioButton(self.comm_radio_frame, text="Serial", 
                                              variable=self.comm_type_var, value="serial",
                                              command=self.on_comm_type_change)
        self.serial_radio.pack(side="left", padx=5)
        
        self.websocket_radio = ctk.CTkRadioButton(self.comm_radio_frame, text="WebSocket", 
                                                 variable=self.comm_type_var, value="websocket",
                                                 command=self.on_comm_type_change)
        self.websocket_radio.pack(side="left", padx=5)
        
        # Connection parameters
        params_frame = ctk.CTkFrame(connection_container)
        params_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(params_frame, text="Connection Parameters:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        # Serial parameters
        self.serial_frame = ctk.CTkFrame(params_frame)
        self.serial_frame.pack(fill="x", pady=5)
        
        serial_container = ctk.CTkFrame(self.serial_frame)
        serial_container.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(serial_container, text="Port:").pack(side="left")
        self.port_entry = ctk.CTkEntry(serial_container, textvariable=self.port_var, width=150)
        self.port_entry.pack(side="left", padx=(5, 10))
        
        ctk.CTkLabel(serial_container, text="Baudrate:").pack(side="left")
        self.baudrate_entry = ctk.CTkEntry(serial_container, textvariable=self.baudrate_var, width=100)
        self.baudrate_entry.pack(side="left", padx=5)
        
        # WebSocket parameters
        self.websocket_frame = ctk.CTkFrame(params_frame)
        self.websocket_frame.pack(fill="x", pady=5)
        
        websocket_container = ctk.CTkFrame(self.websocket_frame)
        websocket_container.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(websocket_container, text="WebSocket URI:").pack(side="left")
        self.websocket_entry = ctk.CTkEntry(websocket_container, textvariable=self.websocket_uri_var, width=300)
        self.websocket_entry.pack(side="left", padx=5)
        
        # Connection control
        control_frame = ctk.CTkFrame(connection_container)
        control_frame.pack(side="right", padx=10, pady=10)
        
        self.connect_btn = ctk.CTkButton(control_frame, text="🔌 Connect", 
                                        command=self.toggle_connection,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        height=40, width=120)
        self.connect_btn.pack(pady=5)
        
        self.status_label = ctk.CTkLabel(control_frame, text="⌫ Disconnected", 
                                        font=ctk.CTkFont(size=12, weight="bold"),
                                        text_color="red")
        self.status_label.pack(pady=5)
        
    def on_comm_type_change(self):
        """Handle communication type selection change"""
        comm_type = self.comm_type_var.get()
        
        if comm_type == "serial":
            self.serial_frame.pack(fill="x", pady=5)
            self.websocket_frame.pack_forget()
        else:  # websocket
            self.websocket_frame.pack(fill="x", pady=5)
            self.serial_frame.pack_forget()
    
    def create_servo_tab(self):
        """Create individual servo control tab with improved spacing"""
        servo_frame = self.tabview.tab("🦾 Individual Servos")
        
        # Create scrollable frame
        self.servo_scroll = ctk.CTkScrollableFrame(servo_frame)
        self.servo_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure the scrollable frame to expand properly
        self.servo_scroll.grid_columnconfigure(0, weight=1)
        self.servo_scroll.grid_columnconfigure(1, weight=1)
        
        # Create servo controls in a grid
        self.servo_controls = {}
        servo_list = [
            "rightGripper", "rightWrist", "rightElbow", "rightSholderPitch", 
            "rightSholderYaw", "rightSholderRoll", "leftGripper", "leftWrist", 
            "leftElbow", "leftSholderPitch", "leftSholderYaw", "leftSholderRoll",
            "headPan", "headTilt"
        ]
        
        for i, servo_id in enumerate(servo_list):
            min_angle, max_angle = ServoLimits.get_limits(servo_id)
            
            # Create modern servo control frame
            servo_frame_widget = ctk.CTkFrame(self.servo_scroll)
            servo_frame_widget.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            
            # Configure the servo frame to expand
            self.servo_scroll.grid_rowconfigure(i//2, weight=1)
            
            # Servo name with icon
            name_display = servo_id.replace("Sholder", "Shoulder")
            ctk.CTkLabel(servo_frame_widget, text=f"⚙️ {name_display}", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
            
            # Angle control with modern slider
            angle_var = ctk.DoubleVar(value=0.0)
            
            angle_frame = ctk.CTkFrame(servo_frame_widget)
            angle_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(angle_frame, text="Angle:", font=ctk.CTkFont(size=12)).pack(side="left")
            angle_label = ctk.CTkLabel(angle_frame, text="0.0°", font=ctk.CTkFont(size=12, weight="bold"))
            angle_label.pack(side="right")
            
            angle_slider = ctk.CTkSlider(servo_frame_widget, from_=min_angle, to=max_angle,
                                       variable=angle_var, width=300)
            angle_slider.pack(pady=10, padx=15)
            
            # Update angle label when slider moves
            def update_angle_label(value, label=angle_label):
                label.configure(text=f"{float(value):.1f}°")
            angle_slider.configure(command=update_angle_label)
            
            # Speed and acceleration controls
            controls_frame = ctk.CTkFrame(servo_frame_widget)
            controls_frame.pack(fill="x", padx=15, pady=5)
            controls_frame.grid_columnconfigure(1, weight=1)
            controls_frame.grid_columnconfigure(3, weight=1)
            
            # Speed control
            speed_var = ctk.IntVar(value=200)
            ctk.CTkLabel(controls_frame, text="Speed:", font=ctk.CTkFont(size=10)).grid(row=0, column=0, sticky="w", padx=5)
            speed_slider = ctk.CTkSlider(controls_frame, from_=1, to=1000, variable=speed_var, width=120)
            speed_slider.grid(row=0, column=1, padx=5, sticky="ew")
            
            # Acceleration control
            acc_var = ctk.IntVar(value=20)
            ctk.CTkLabel(controls_frame, text="Acc:", font=ctk.CTkFont(size=10)).grid(row=0, column=2, sticky="w", padx=5)
            acc_slider = ctk.CTkSlider(controls_frame, from_=1, to=100, variable=acc_var, width=120)
            acc_slider.grid(row=0, column=3, padx=5, sticky="ew")
            
            # Move button
            move_btn = ctk.CTkButton(servo_frame_widget, text="▶️ Move", 
                                   command=lambda sid=servo_id, av=angle_var, sv=speed_var, accv=acc_var: 
                                   self.control_individual_servo(sid, av.get(), sv.get(), accv.get()),
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   height=35)
            move_btn.pack(pady=15, padx=15, fill="x")
            
            self.servo_controls[servo_id] = {
                'angle': angle_var,
                'speed': speed_var,
                'acc': acc_var,
                'button': move_btn
            }
    
    def create_head_tab(self):
        """Create modern head control tab"""
        head_frame = self.tabview.tab("👤 Head Control")
        
        main_frame = ctk.CTkFrame(head_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(main_frame, text="👤 Head Movement Control", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Controls container
        controls_container = ctk.CTkFrame(main_frame)
        controls_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pan control
        pan_frame = ctk.CTkFrame(controls_container)
        pan_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(pan_frame, text="↔️ Head Pan", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.head_pan_var = ctk.DoubleVar(value=0.0)
        
        pan_control_frame = ctk.CTkFrame(pan_frame)
        pan_control_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(pan_control_frame, text="Angle:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.pan_angle_label = ctk.CTkLabel(pan_control_frame, text="0.0°", 
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self.pan_angle_label.pack(side="right")
        
        pan_slider = ctk.CTkSlider(pan_frame, from_=-90, to=90, variable=self.head_pan_var,
                                  width=400, command=self.update_pan_label)
        pan_slider.pack(pady=10)
        
        # Pan speed
        self.head_pan_speed_var = ctk.IntVar(value=200)
        pan_speed_frame = ctk.CTkFrame(pan_frame)
        pan_speed_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(pan_speed_frame, text="Speed:", font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkSlider(pan_speed_frame, from_=1, to=1000, variable=self.head_pan_speed_var,
                     width=300).pack(side="right", padx=10)
        
        # Tilt control
        tilt_frame = ctk.CTkFrame(controls_container)
        tilt_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(tilt_frame, text="↕️ Head Tilt", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.head_tilt_var = ctk.DoubleVar(value=0.0)
        
        tilt_control_frame = ctk.CTkFrame(tilt_frame)
        tilt_control_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(tilt_control_frame, text="Angle:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.tilt_angle_label = ctk.CTkLabel(tilt_control_frame, text="0.0°", 
                                            font=ctk.CTkFont(size=12, weight="bold"))
        self.tilt_angle_label.pack(side="right")
        
        tilt_slider = ctk.CTkSlider(tilt_frame, from_=-38, to=45, variable=self.head_tilt_var,
                                   width=400, command=self.update_tilt_label)
        tilt_slider.pack(pady=10)
        
        # Tilt speed
        self.head_tilt_speed_var = ctk.IntVar(value=200)
        tilt_speed_frame = ctk.CTkFrame(tilt_frame)
        tilt_speed_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(tilt_speed_frame, text="Speed:", font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkSlider(tilt_speed_frame, from_=1, to=1000, variable=self.head_tilt_speed_var,
                     width=300).pack(side="right", padx=10)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(controls_container)
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="🎯 Move Head", command=self.control_head,
                     font=ctk.CTkFont(size=16, weight="bold"), height=50, width=150).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="🎯 Center Head", command=self.center_head,
                     font=ctk.CTkFont(size=16, weight="bold"), height=50, width=150).pack(side="left", padx=10)
    
    def update_pan_label(self, value):
        """Update pan angle label"""
        self.pan_angle_label.configure(text=f"{float(value):.1f}°")
    
    def update_tilt_label(self, value):
        """Update tilt angle label"""
        self.tilt_angle_label.configure(text=f"{float(value):.1f}°")
    
    def create_left_hand_tab(self):
        """Create left hand control tab"""
        self.create_hand_tab("👈 Left Hand", "left")
        
    def create_right_hand_tab(self):
        """Create right hand control tab"""
        self.create_hand_tab("👉 Right Hand", "right")
    
    def create_hand_tab(self, tab_name, side):
        """Create modern hand control tab"""
        hand_frame = self.tabview.tab(tab_name)
        
        main_frame = ctk.CTkFrame(hand_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        icon = "👈" if side == "left" else "👉"
        ctk.CTkLabel(main_frame, text=f"{icon} {side.title()} Hand Control", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Create scrollable frame for controls
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Define servo configurations
        prefix = side.lower()
        servo_configs = [
            ("🤏 Gripper", f"{prefix}Gripper", ServoLimits.get_limits(f"{prefix}Gripper")),
            ("🔄 Wrist", f"{prefix}Wrist", ServoLimits.get_limits(f"{prefix}Wrist")),
            ("💪 Elbow", f"{prefix}Elbow", ServoLimits.get_limits(f"{prefix}Elbow")),
            ("🎯 Shoulder Pitch", f"{prefix}SholderPitch", ServoLimits.get_limits(f"{prefix}SholderPitch")),
            ("↔️ Shoulder Yaw", f"{prefix}SholderYaw", ServoLimits.get_limits(f"{prefix}SholderYaw")),
            ("🔄 Shoulder Roll", f"{prefix}SholderRoll", ServoLimits.get_limits(f"{prefix}SholderRoll")),
        ]
        
        # Create controls for each servo
        hand_vars = {}
        for i, (display_name, servo_key, (min_angle, max_angle)) in enumerate(servo_configs):
            servo_frame = ctk.CTkFrame(scroll_frame)
            servo_frame.pack(fill="x", padx=10, pady=10)
            
            # Servo name
            ctk.CTkLabel(servo_frame, text=display_name, 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
            
            # Angle control with label
            angle_var = ctk.DoubleVar(value=0.0)
            
            angle_control_frame = ctk.CTkFrame(servo_frame)
            angle_control_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(angle_control_frame, text="Angle:", font=ctk.CTkFont(size=12)).pack(side="left")
            angle_label = ctk.CTkLabel(angle_control_frame, text="0.0°", 
                                     font=ctk.CTkFont(size=12, weight="bold"))
            angle_label.pack(side="right")
            
            angle_slider = ctk.CTkSlider(servo_frame, from_=min_angle, to=max_angle, 
                                       variable=angle_var, width=350)
            angle_slider.pack(pady=10)
            
            # Update label function
            def update_label(value, label=angle_label):
                label.configure(text=f"{float(value):.1f}°")
            angle_slider.configure(command=update_label)
            
            hand_vars[servo_key] = angle_var
        
        # Store variables for later use
        if side == "left":
            self.left_hand_vars = hand_vars
        else:
            self.right_hand_vars = hand_vars
        
        # Control buttons
        btn_frame = ctk.CTkFrame(scroll_frame)
        btn_frame.pack(pady=30)
        
        move_cmd = self.control_left_hand if side == "left" else self.control_right_hand
        reset_cmd = self.reset_left_hand if side == "left" else self.reset_right_hand
        
        ctk.CTkButton(btn_frame, text=f"▶️ Move {side.title()} Hand", command=move_cmd,
                     font=ctk.CTkFont(size=16, weight="bold"), height=50, width=200).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=f"🔄 Reset {side.title()} Hand", command=reset_cmd,
                     font=ctk.CTkFont(size=16, weight="bold"), height=50, width=200).pack(side="left", padx=10)
    
    def create_base_tab(self):
        """Create modern base motor control tab with scrolling"""
        base_frame = self.tabview.tab("🚶 Base Control")
        
        # Create scrollable frame for all content
        main_scroll = ctk.CTkScrollableFrame(base_frame)
        main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(main_scroll, text="🚶 Robot Base Movement", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Speed control
        speed_frame = ctk.CTkFrame(main_scroll)
        speed_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(speed_frame, text="⚡ Movement Speed", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.base_speed_var = ctk.IntVar(value=100)
        
        speed_control_frame = ctk.CTkFrame(speed_frame)
        speed_control_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(speed_control_frame, text="Speed:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.speed_label = ctk.CTkLabel(speed_control_frame, text="100", 
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.speed_label.pack(side="right")
        
        speed_slider = ctk.CTkSlider(speed_frame, from_=0, to=255, variable=self.base_speed_var,
                                   width=400, command=self.update_speed_label)
        speed_slider.pack(pady=10)
        
        # Movement buttons with clean styling
        movement_frame = ctk.CTkFrame(main_scroll)
        movement_frame.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkLabel(movement_frame, text="🎮 Movement Controls", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        # Button grid
        btn_grid = ctk.CTkFrame(movement_frame)
        btn_grid.pack(pady=20)
        
        # Configure grid
        for i in range(3):
            btn_grid.grid_columnconfigure(i, weight=1)
        for i in range(3):
            btn_grid.grid_rowconfigure(i, weight=1)
        
        # Forward
        ctk.CTkButton(btn_grid, text="⬆️ Forward", command=self.move_forward,
                     font=ctk.CTkFont(size=14, weight="bold"), width=120, height=50
                     ).grid(row=0, column=1, padx=5, pady=5)
        
        # Left, Stop, Right
        ctk.CTkButton(btn_grid, text="⬅️ Left", command=self.turn_left,
                     font=ctk.CTkFont(size=14, weight="bold"), width=120, height=50
                     ).grid(row=1, column=0, padx=5, pady=5)
        
        ctk.CTkButton(btn_grid, text="⏹️ STOP", command=self.stop_base,
                     font=ctk.CTkFont(size=14, weight="bold"), width=120, height=50,
                     fg_color="#dc3545", hover_color="#c82333"
                     ).grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkButton(btn_grid, text="➡️ Right", command=self.turn_right,
                     font=ctk.CTkFont(size=14, weight="bold"), width=120, height=50
                     ).grid(row=1, column=2, padx=5, pady=5)
        
        # Backward
        ctk.CTkButton(btn_grid, text="⬇️ Backward", command=self.move_backward,
                     font=ctk.CTkFont(size=14, weight="bold"), width=120, height=50
                     ).grid(row=2, column=1, padx=5, pady=5)
        
        # Manual motor control
        manual_frame = ctk.CTkFrame(main_scroll)
        manual_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(manual_frame, text="🔧 Manual Motor Control", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        motors_container = ctk.CTkFrame(manual_frame)
        motors_container.pack(fill="x", padx=20, pady=10)
        
        # Left motor
        left_motor_frame = ctk.CTkFrame(motors_container)
        left_motor_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(left_motor_frame, text="Left Motor:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.left_motor_var = ctk.IntVar(value=0)
        ctk.CTkSlider(left_motor_frame, from_=-255, to=255, variable=self.left_motor_var,
                     width=200).pack(pady=5)
        
        # Right motor
        right_motor_frame = ctk.CTkFrame(motors_container)
        right_motor_frame.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_motor_frame, text="Right Motor:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.right_motor_var = ctk.IntVar(value=0)
        ctk.CTkSlider(right_motor_frame, from_=-255, to=255, variable=self.right_motor_var,
                     width=200).pack(pady=5)
        
        # Apply button
        ctk.CTkButton(manual_frame, text="⚡ Apply Manual Control", command=self.apply_manual_motors,
                     font=ctk.CTkFont(size=14, weight="bold"), height=40).pack(pady=15)
    
    def update_speed_label(self, value):
        """Update speed label"""
        self.speed_label.configure(text=f"{int(float(value))}")
    
    # Connection methods (same as original but with modern styling updates)
    def toggle_connection(self):
        """Toggle robot connection with modern UI updates"""
        if not self.connected:
            self.connect_robot()
        else:
            self.disconnect_robot()
    
    def connect_robot(self):
        """Connect to robot with modern status updates"""
        try:
            # Simulate connection logic here
            # Replace with your actual controller connection code
            
            self.connected = True
            self.connect_btn.configure(text="🔌 Disconnect", fg_color="#dc3545", hover_color="#c82333")
            self.status_label.configure(text="✅ Connected", text_color="green")
            
            # Show modern success message
            messagebox.showinfo("Connection Successful", "🤖 Successfully connected to BonicBot!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"⚠️ Failed to connect: {str(e)}")
    
    def disconnect_robot(self):
        """Disconnect from robot with modern status updates"""
        try:
            self.connected = False
            self.connect_btn.configure(text="🔌 Connect", fg_color="#1f538d", hover_color="#14375e")
            self.status_label.configure(text="⌫ Disconnected", text_color="red")
            
            messagebox.showinfo("Disconnected", "🔌 Disconnected from BonicBot")
            
        except Exception as e:
            messagebox.showerror("Disconnection Error", f"⚠️ Error during disconnect: {str(e)}")
    
    # Add placeholder methods for all the control functions
    def control_individual_servo(self, servo_id, angle, speed, acc):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Moving {servo_id} to {angle}° at speed {speed} with acc {acc}")
    
    def control_head(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Moving head: pan={self.head_pan_var.get()}°, tilt={self.head_tilt_var.get()}°")
    
    def center_head(self):
        self.head_pan_var.set(0.0)
        self.head_tilt_var.set(0.0)
        self.update_pan_label(0.0)
        self.update_tilt_label(0.0)
        self.control_head()
    
    def control_left_hand(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print("Moving left hand")
    
    def control_right_hand(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print("Moving right hand")
    
    def reset_left_hand(self):
        for var in self.left_hand_vars.values():
            var.set(0.0)
        self.control_left_hand()
    
    def reset_right_hand(self):
        for var in self.right_hand_vars.values():
            var.set(0.0)
        self.control_right_hand()
    
    # Base movement methods
    def move_forward(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Moving forward at speed {self.base_speed_var.get()}")
    
    def move_backward(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Moving backward at speed {self.base_speed_var.get()}")
    
    def turn_left(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Turning left at speed {self.base_speed_var.get()}")
    
    def turn_right(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Turning right at speed {self.base_speed_var.get()}")
    
    def stop_base(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print("Stopping robot")
    
    def apply_manual_motors(self):
        if not self.connected:
            messagebox.showwarning("Warning", "⚠️ Not connected to robot")
            return
        print(f"Manual motors: left={self.left_motor_var.get()}, right={self.right_motor_var.get()}")
    
    # Preset methods (add your actual implementation)
    def goto_home(self):
        print("Going to home position")
    
    def goto_attention(self):
        print("Going to attention position")
    
    def wave_hello(self):
        print("Waving hello")
    
    def arms_up(self):
        print("Raising arms")
    
    def look_around(self):
        print("Looking around")
    
    def save_position(self):
        print("Saving position")
    
    def load_position(self):
        print("Loading position")

def run():
    """Main function to run the modern GUI"""
    root = ctk.CTk()
    app = BonicBotGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.connected and hasattr(app, 'controller') and app.controller:
            try:
                app.controller.close()
            except:
                pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    run()