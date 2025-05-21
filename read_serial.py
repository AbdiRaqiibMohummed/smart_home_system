import serial
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import random

# Configuration
SERIAL_PORT = '/dev/cu.usbmodem48CA435C852C2'
BAUD_RATE = 9600
USERNAME = "admin"
PASSWORD = "password123"
MOTION_TIMEOUT = 3
ROOMS = ["Living Room", "Kitchen", "Bedroom", "Garage", "Hallway"]

# Sensor state
temperature = "--"
gas_status = "No Gas Detected"
motion_status = "No Motion Detected"
last_motion_time = time.time()
motion_logs = []
serial_outputs = []  # Added to store serial output logs

# Serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    print(f"Serial error: {e}")
    ser = None

class SmartHomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Login")
        self.root.configure(bg="#060d3d")
        
        # Dictionary to store the state of each light
        # Keys will be the room names, values will be True (ON) or False (OFF)
        self.light_states = {
            "Bedroom": False,
            "Living Room": False,
            "Kitchen": False,
            "Garage": False,
            "Hallway": False,
            "Bathroom": False
        }
        # Dictionary to store references to the ON/OFF buttons for each light
        self.light_buttons = {} # Example: {"Bedroom": {"on_btn": btn_obj, "off_btn": btn_obj}}

        self.build_login_screen()

    def build_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.attributes("-fullscreen", True)
        tk.Label(self.root, text="GT NEST LOGIN", font=("Helvetica", 25, "bold"), bg="#060d3d", fg="white").pack(pady=40)
        self.username_entry = tk.Entry(self.root, font=("Helvetica", 20), bg="white", fg="black")
        self.username_entry.pack(pady=10)
        self.username_entry.insert(0, "admin")
        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 20), bg="white", fg="black")
        self.password_entry.pack(pady=10)
        self.password_entry.insert(0, "password123")
        tk.Button(self.root, text="Login", font=("Helvetica", 20), bg="white", fg="black", bd=0, relief="flat", width=18, command=self.authenticate).pack(pady=20)

    def authenticate(self):
        if self.username_entry.get() == USERNAME and self.password_entry.get() == PASSWORD:
            self.build_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def build_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("GT SMART HOME CONTROL SYSTEM")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#060d3d")

        top_frame = tk.Frame(self.root, bg="#060d3d")
        top_frame.pack(fill="x", padx=10, pady=5 )

        tk.Label(top_frame, text="Smart Home Sensor Dashboard", font=("Helvetica", 20, "bold"), bg="#060d3d", fg="white").pack(side="top")
        tk.Button(top_frame, text="Logout", command=self.build_login_screen, font=("Helvetica", 20), bg="white", fg="black", bd=0, relief="flat").pack(side="right", padx=10)
        tk.Button(top_frame, text="Back", command=self.build_login_screen, font=("Helvetica", 20), bg="white", fg="black", bd=0, relief="flat").pack(side="right", padx=10)

        self.content_frame = tk.Frame(self.root, bg="#060d3d")
        self.content_frame.pack(pady=10)

        self.temp_label = self.create_status_box("Temperature: -- °C", 0, 0, "#4db6ac")
        self.gas_label = self.create_status_box("Gas Status: No Gas Detected", 0, 1, "#f57c00")
        self.motion_label = self.create_motion_box(1, 0, "#7986cb")
        
        # Serial Output Box
        self.create_serial_box(1, 1, "#607d8b")
        
        # Lights Control Box - same style as serial box
        self.create_lights_control_box(2, 0, "#9c27b0")
        
        # Add test data for development purposes
        if not ser:
            self.add_test_data()

        self.update_sensor_data()

    def add_test_data(self):
        # Add some sample motion logs for testing
        for i in range(5):
            room = random.choice(ROOMS)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Motion Detected in {room}"
            motion_logs.append(log_entry)
            serial_outputs.append(f"[{timestamp}] Serial: Motion detected in {room}")

    def create_status_box(self, label_text, row, column, bg_color):
        frame = tk.Frame(self.content_frame, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text=label_text, font=("Helvetica", 14), bg=bg_color, fg="white")
        label.pack()
        return label

#this is the section for motion status
    def create_motion_box(self, row, column, bg_color):
        frame = tk.Frame(self.content_frame, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text="Motion Status: No Motion Detected", font=("Helvetica", 14,"bold"), bg=bg_color, fg="white")
        label.pack()
        tk.Button(frame, text="View Serial Logs", command=self.show_logs, font=("Helvetica", 12, "bold"), bg="white", fg="black", width=10).pack(pady=10,fill="both", expand=True)
        return label
    
    def create_serial_box(self, row, column, bg_color):
        frame = tk.Frame(self.content_frame, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text="Serial Output", font=("Helvetica", 14, "bold"), bg=bg_color, fg="white")
        label.pack(pady=(0, 10))
        
        # Create a button that fills the box
        serial_btn = tk.Button(frame, text="View Serial Logs", command=self.show_serial_logs, 
                      bg="white", fg="black", font=("Helvetica", 12, "bold"))
        serial_btn.pack(fill="both", expand=True)
        
        return label
        
    def create_lights_control_box(self, row, column, bg_color):
        frame = tk.Frame(self.content_frame, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text="Lights Control", font=("Helvetica", 14, "bold"), bg=bg_color, fg="white")
        label.pack(pady=(0, 10))
        
        # Create a button that fills the box
        lights_btn = tk.Button(frame, text="Control Lights", command=self.show_lights_control, 
                      bg="white", fg="black", font=("Helvetica", 12, "bold"))
        lights_btn.pack(fill="both", expand=True)
        
        return label

    def show_logs(self):
        global motion_logs
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg="#060d3d")
        self.root.title("Motion Logs")

        top_frame = tk.Frame(self.root, bg="#060d3d")
        top_frame.pack(fill="x")
        tk.Button(top_frame, text="Back to Dashboard", command=self.build_dashboard, font=("Helvetica", 16), bg="white", fg="black").pack(pady=10)

        logs_frame = tk.Frame(self.root, bg="#060d3d")
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)

        log_box = tk.Text(logs_frame, font=("Helvetica", 20), bg="white", fg="black", height=25, width=80)
        log_box.pack()
        
        # Make sure we have logs to display
        if not motion_logs:
            log_box.insert("end", "No motion logs recorded yet.\n")
        else:
            for log in motion_logs:
                log_box.insert("end", f"{log}\n")
        
        log_box.config(state="disabled")
    
    def show_serial_logs(self):
        global serial_outputs
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg="#060d3d")
        self.root.title("Serial Output Logs")

        top_frame = tk.Frame(self.root, bg="#060d3d")
        top_frame.pack(fill="x")
        tk.Button(top_frame, text="Back to Dashboard", command=self.build_dashboard, font=("Helvetica", 16), bg="white", fg="black").pack(pady=10)

        logs_frame = tk.Frame(self.root, bg="#060d3d")
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)

        log_box = tk.Text(logs_frame, font=("Helvetica", 20), bg="white", fg="black", height=25, width=80)
        log_box.pack()
        
        # Make sure we have logs to display
        if not serial_outputs:
            log_box.insert("end", "No serial outputs recorded yet.\n")
        else:
            for log in serial_outputs:
                log_box.insert("end", f"{log}\n")
        
        log_box.config(state="disabled")
        
    def show_lights_control(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg="#060d3d")
        self.root.title("Lights Control Panel")
        tk.Label(self.root, text="LIGHT CONTROL", font=("Helvetica", 25, "bold"), bg="#060d3d", fg="white").pack(pady=40)

        top_frame = tk.Frame(self.root, bg="#060d3d")
        top_frame.pack(fill="x")
        tk.Button(top_frame, text="Back to Dashboard", command=self.build_dashboard, font=("Helvetica", 16), bg="white", fg="black").pack(pady=10)

        # Create a container frame to hold and center all light control panels
        lights_container_frame = tk.Frame(self.root, bg="#060d3d")
        lights_container_frame.pack(fill="both", expand=True, padx=20, pady=20) # Allows it to take up space and expand

        lights_frame = tk.Frame(lights_container_frame, bg="#060d3d")
        lights_frame.pack() # This centers lights_frame within lights_container_frame

        # Create light controls using .pack() for vertical stacking
        self.create_light_control_panel(lights_frame, "Bedroom", "#A0522D", "LIGHT_ON", "LIGHT_OFF")
        self.create_light_control_panel(lights_frame, "Living Room", "#D2691E", "LIVING_ON", "LIVING_OFF")
        self.create_light_control_panel(lights_frame, "Kitchen", "#CD853F", "KITCHEN_ON", "KITCHEN_OFF")
        self.create_light_control_panel(lights_frame, "Garage", "#F4A460", "GARAGE_ON", "GARAGE_OFF")
        # self.create_light_control_panel(lights_frame, "Hallway", "#DAA520", "HALLWAY_ON", "HALLWAY_OFF")
        # self.create_light_control_panel(lights_frame, "Bathroom", "#B8860B", "BATHROOM_ON", "BATHROOM_OFF")
        
        # Initialize button colors based on current light states
        self.update_all_light_button_colors()


    def create_light_control_panel(self, parent, room_name, color, cmd_on, cmd_off):
        frame = tk.Frame(parent, bg=color, bd=2, relief="raised", padx=20, pady=20)
        frame.pack(pady=10) # Add vertical padding between each light control panel
        
        tk.Label(frame, text=room_name, font=("Helvetica", 18, "bold"), bg=color, fg="white").pack(pady=(0, 20))
        
        buttons_frame = tk.Frame(frame, bg=color)
        buttons_frame.pack(fill="both", expand=True)
        
        # Store references to the buttons
        on_btn = tk.Button(buttons_frame, text="ON", 
                           command=lambda: self.toggle_light_state(room_name, True, cmd_on), 
                           bg="#d32f2f", fg="black", font=("Helvetica", 16, "bold"), # Default to red (off)
                           width=8, height=2)
        on_btn.pack(side="left", padx=10, expand=True, fill="both")
                 
        off_btn = tk.Button(buttons_frame, text="OFF", 
                            command=lambda: self.toggle_light_state(room_name, False, cmd_off), 
                            bg="#388e3c", fg="black", font=("Helvetica", 16, "bold"), # Default to green (on)
                            width=8, height=2)
        off_btn.pack(side="right", padx=10, expand=True, fill="both")

        # Store button references for later updates
        self.light_buttons[room_name] = {"on_btn": on_btn, "off_btn": off_btn}

    def toggle_light_state(self, room_name, new_state, command):
        """
        Updates the light state and calls send_command, then updates button colors.
        """
        self.light_states[room_name] = new_state
        self.send_command(command)
        self.update_light_button_colors(room_name)

    def update_light_button_colors(self, room_name):
        """
        Updates the ON/OFF button colors for a specific room based on its state.
        """
        if room_name in self.light_buttons:
            on_btn = self.light_buttons[room_name]["on_btn"]
            off_btn = self.light_buttons[room_name]["off_btn"]
            
            if self.light_states[room_name]: # Light is ON
                on_btn.config(bg="#388e3c") # Green for ON
                off_btn.config(bg="#d32f2f") # Red for OFF
            else: # Light is OFF
                on_btn.config(bg="#d32f2f") # Red for ON
                off_btn.config(bg="#388e3c") # Green for OFF

    def update_all_light_button_colors(self):
        """
        Initializes or updates button colors for all lights.
        Called when the light control panel is first displayed.
        """
        for room_name in self.light_states:
            self.update_light_button_colors(room_name)

    def send_command(self, command):
        try:
            if ser:
                ser.write(f"{command}\n".encode())
                print(f"Command sent: {command}")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                serial_outputs.append(f"[{timestamp}] Command sent: {command}")
            else:
                print(f"Would send command: {command} (Serial not connected)")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                serial_outputs.append(f"[{timestamp}] Would send command: {command} (Serial not connected)")
        except Exception as e:
            print(f"Error sending {command}: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serial_outputs.append(f"[{timestamp}] Error sending {command}: {e}")

    def update_sensor_data(self):
        global temperature, gas_status, motion_status, last_motion_time, motion_logs, serial_outputs
        
        try:
            # If serial connection is available, try to read data
            if ser:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:  # Only log non-empty lines
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        serial_outputs.append(f"[{timestamp}] Received: {line}")
                    self.process_sensor_data(line)
            
            # For testing purposes, simulate data if no serial connection
            elif random.random() < 0.1:  # 10% chance of simulated data
                simulated_data = [
                    f"Temperature: {random.randint(18, 30)}",
                    "Gas Detected!",
                    "No Gas Detected",
                    "Motion Detected!"
                ]
                chosen_data = random.choice(simulated_data)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                serial_outputs.append(f"[{timestamp}] Simulated: {chosen_data}")
                self.process_sensor_data(chosen_data)
            
            # Check if motion timeout has elapsed
            current_time = time.time()
            if current_time - last_motion_time > MOTION_TIMEOUT:
                if motion_status != "No Motion Detected":
                    motion_status = "No Motion Detected"
                    self.motion_label.config(text=f"Motion Status: {motion_status}")
            
        except Exception as e:
            print(f"Error updating sensor data: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serial_outputs.append(f"[{timestamp}] Error: {e}")
        
        # Schedule next update
        self.root.after(100, self.update_sensor_data)  # Faster update rate (every 100ms)
    
    def process_sensor_data(self, line):
        global temperature, gas_status, motion_status, last_motion_time, motion_logs
        
        if not line:
            return
            
        print(f"Received data: {line}")
        lower_line = line.lower()
        
        # Process temperature data
        if "temperature" in lower_line:
            try:
                # Extract temperature value
                temp_parts = line.split(":")
                if len(temp_parts) > 1:
                    temperature = temp_parts[1].strip()
                    self.temp_label.config(text=f"Temperature: {temperature} °C")
                    print(f"Updated temperature: {temperature} °C")
            except Exception as e:
                print(f"Error processing temperature: {e}")
                
        # Process gas data
        elif "gas detected!" in lower_line:
            gas_status = "Gas Detected"
            self.gas_label.config(text=f"Gas Status: {gas_status}")
            print("Gas detected!")
            
        elif "no gas detected" in lower_line:
            gas_status = "No Gas Detected"
            self.gas_label.config(text=f"Gas Status: {gas_status}")
            print("No gas detected")
            
        # Process motion data
        elif "motion detected!" in lower_line:
            motion_status = "Motion Detected"
            last_motion_time = time.time()
            room = random.choice(ROOMS)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Motion Detected in {room}"
            motion_logs.append(log_entry)
            print(f"Motion log added: {log_entry}")
            self.motion_label.config(text=f"Motion Status: {motion_status}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeApp(root)
    root.mainloop()