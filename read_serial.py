import serial
import time
import tkinter as tk

SERIAL_PORT = '/dev/cu.usbmodem48CA435C852C2'  # Change this to match your Arduino port
BAUD_RATE = 9600

temperature = "--"
gas_status = "No Gas Detected"
motion_status = "No Motion Detected"
last_motion_time = time.time()
MOTION_TIMEOUT = 3  # seconds

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for Arduino to reset

    root = tk.Tk()
    root.title("Smart Home Sensor Dashboard")
    root.geometry("700x400")
    root.configure(bg="#e0f7fa")  # Light teal background

    title_label = tk.Label(
        root,
        text="Smart Home Sensor Dashboard",
        font=("Helvetica", 20, "bold"),
        bg="#e0f7fa",
        fg="#00796b"
    )
    title_label.pack(pady=10)

    content_frame = tk.Frame(root, bg="#e0f7fa")
    content_frame.pack(pady=10)

    def create_status_box(parent, label_text, row, column, bg_color):
        frame = tk.Frame(parent, bg=bg_color, bd=2, relief="raised", padx=20, pady=20)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        label = tk.Label(frame, text=label_text, font=("Helvetica", 14), bg=bg_color, fg="white")
        label.pack()
        return label

    # Grid layout (2x2)
    temp_label = create_status_box(content_frame, "Temperature: -- °C", 0, 0, "#4db6ac")
    gas_label = create_status_box(content_frame, "Gas Status: No Gas Detected", 0, 1, "#f57c00")
    motion_label = create_status_box(content_frame, "Motion Status: No Motion Detected", 1, 0, "#7986cb")

    # Light Control Box
    light_frame = tk.Frame(content_frame, bg="#8d6e63", bd=2, relief="raised", padx=20, pady=20)
    light_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    light_label = tk.Label(light_frame, text="Light Control", font=("Helvetica", 14, "bold"), bg="#8d6e63", fg="white")
    light_label.pack(pady=(0, 10))

    def light_on():
        try:
            ser.write(b'LIGHT_ON\n')
        except Exception as e:
            print(f"Error sending LIGHT_ON: {e}")

    def light_off():
        try:
            ser.write(b'LIGHT_OFF\n')
        except Exception as e:
            print(f"Error sending LIGHT_OFF: {e}")

    on_button = tk.Button(
        light_frame,
        text="ON",
        command=light_on,
        bg="#388e3c",      # Dark green
        fg="black",       
        font=("Helvetica", 12, "bold"),
        width=8,
        height=2,
        relief="raised"
    )
    off_button = tk.Button(
        light_frame,
        text="OFF",
        command=light_off,
        bg="#d32f2f",      # Red
        fg="black",       
        font=("Helvetica", 12, "bold"),
        width=8,
        height=2,
        relief="raised"
    )

    on_button.pack(side="left", padx=10)
    off_button.pack(side="left", padx=10)

    def update_sensor_data():
        global temperature, gas_status, motion_status, last_motion_time
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        current_time = time.time()

        if line:
            print(f"DEBUG: Received line: '{line}'")  # For debugging

            lower_line = line.lower()

            if "temperature" in lower_line:
                temperature = line.split(":")[1].strip()
                temp_label.config(text=f"Temperature: {temperature} °C")
            elif "gas detected!" in lower_line:
                gas_status = "Gas Detected"
                gas_label.config(text=f"Gas Status: {gas_status}")
            elif "no gas detected" in lower_line:
                gas_status = "No Gas Detected"
                gas_label.config(text=f"Gas Status: {gas_status}")
            elif "motion detected!" in lower_line:
                motion_status = "Motion Detected"
                motion_label.config(text=f"Motion Status: {motion_status}")
                last_motion_time = current_time

        # Clear motion status if timeout exceeded
        if current_time - last_motion_time > MOTION_TIMEOUT:
            if motion_status != "No Motion Detected":
                motion_status = "No Motion Detected"
                motion_label.config(text=f"Motion Status: {motion_status}")

        root.after(500, update_sensor_data)

    update_sensor_data()
    root.mainloop()

except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("\nExiting.")
    ser.close()
