import serial
import time
import tkinter as tk
from tkinter import messagebox

# Configuration
SERIAL_PORT = '/dev/cu.usbmodem48CA435C852C2'
BAUD_RATE = 9600
USERNAME = "admin"
PASSWORD = "password123"
MOTION_TIMEOUT = 3

# Sensor state
temperature = "--"
gas_status = "No Gas Detected"
motion_status = "No Motion Detected"
last_motion_time = time.time()

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
        self.root.geometry("400x300")
        self.root.configure(bg="#e1f5fe")
        self.build_login_screen()

    def build_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="GT NEST LOGIN", font=("Helvetica", 20, "bold"), bg="#e0f7fa", fg="#000").pack(pady=20)

        self.username_entry = tk.Entry(self.root, font=("Helvetica", 14),bg="white",fg="black")
        self.username_entry.pack(pady=10)
        self.username_entry.insert(0, "enter username")

        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 14),bg="white",fg="grey")
        self.password_entry.pack(pady=10)
        self.password_entry.insert(0, "password123")

        tk.Button(self.root, text="Login", font=("Helvetica", 14), command=self.authenticate).pack(pady=20)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == USERNAME and password == PASSWORD:
            self.build_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def build_dashboard(self):
        self.root.title("Smart Home Sensor Dashboard")
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("800x500")
        self.root.configure(bg="#e0f7fa")

        top_frame = tk.Frame(self.root, bg="#e0f7fa")
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            top_frame, text="Smart Home Sensor Dashboard",
            font=("Helvetica", 20, "bold"), bg="#e0f7fa", fg="#00796b"
        ).pack(side="left")

        tk.Button(
            top_frame, text="Logout", command=self.build_login_screen,
            font=("Helvetica", 12), bg="#e0f7fa", fg="#000"
        ).pack(side="right")

        self.content_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.content_frame.pack(pady=10)

        self.temp_label = self.create_status_box("Temperature: -- °C", 0, 0, "#4db6ac")
        self.gas_label = self.create_status_box("Gas Status: No Gas Detected", 0, 1, "#f57c00")
        self.motion_label = self.create_status_box("Motion Status: No Motion Detected", 1, 0, "#7986cb")

        # Bedroom light (uses LIGHT_ON/OFF to match your original Arduino)
        self.create_light_control_box("Bedroom", "#8d6e63", 1, 1, "LIGHT_ON", "LIGHT_OFF")

        # Living Room and Kitchen (custom commands, can be adjusted to use LIGHT_ON/OFF as needed)
        self.create_light_control_box("Living Room", "#6d4c41", 2, 0, "LIVING_ON", "LIVING_OFF")
        self.create_light_control_box("Kitchen", "#5d4037", 2, 1, "KITCHEN_ON", "KITCHEN_OFF")

        self.update_sensor_data()

    def create_status_box(self, label_text, row, column, bg_color):
        frame = tk.Frame(self.content_frame, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text=label_text, font=("Helvetica", 14), bg=bg_color, fg="white")
        label.pack()
        return label

    def create_light_control_box(self, room_name, color, row, column, cmd_on, cmd_off):
        frame = tk.Frame(self.content_frame, bg=color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        tk.Label(frame, text=room_name, font=("Helvetica", 14, "bold"), bg=color, fg="white").pack(pady=(0, 10))

        on_btn = tk.Button(frame, text="ON", command=lambda: self.send_command(cmd_on),
                           bg="#388e3c", fg="black", font=("Helvetica", 12, "bold"), width=8, height=2)
        off_btn = tk.Button(frame, text="OFF", command=lambda: self.send_command(cmd_off),
                            bg="#d32f2f", fg="black", font=("Helvetica", 12, "bold"), width=8, height=2)
        on_btn.pack(side="left", padx=10)
        off_btn.pack(side="left", padx=10)

    def send_command(self, command):
        try:
            if ser:
                ser.write(f"{command}\n".encode())
        except Exception as e:
            print(f"Error sending {command}: {e}")

    def update_sensor_data(self):
        global temperature, gas_status, motion_status, last_motion_time
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip() if ser else ''
            current_time = time.time()

            if line:
                print(f"OUTPUT: Received line: '{line}'")
                lower_line = line.lower()

                if "temperature" in lower_line:
                    temperature = line.split(":")[1].strip()
                    self.temp_label.config(text=f"Temperature: {temperature} °C")
                elif "gas detected!" in lower_line:
                    gas_status = "Gas Detected"
                    self.gas_label.config(text=f"Gas Status: {gas_status}")
                elif "no gas detected" in lower_line:
                    gas_status = "No Gas Detected"
                    self.gas_label.config(text=f"Gas Status: {gas_status}")
                elif "motion detected!" in lower_line:
                    motion_status = "Motion Detected"
                    last_motion_time = current_time
                    self.motion_label.config(text=f"Motion Status: {motion_status}")

            if current_time - last_motion_time > MOTION_TIMEOUT:
                if motion_status != "No Motion Detected":
                    motion_status = "No Motion Detected"
                    self.motion_label.config(text=f"Motion Status: {motion_status}")

        except Exception as e:
            print(f"Error updating sensor data: {e}")

        self.root.after(1000, self.update_sensor_data)

# Run the app
root = tk.Tk()
app = SmartHomeApp(root)
root.mainloop()
