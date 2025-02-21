import tkinter as tk
from time import sleep
from tkinter import ttk, filedialog, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import struct
import threading
import queue
import time

opcode_list = {"update": 1, "reboot": 2, "commit update": 3}


class FirmwareUpdaterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Firmware Updater")
        self.geometry("800x800")

        # Serial communication variables
        self.ser = None
        self.running = False
        self.queue = queue.Queue()
        self.confirm_lines = None

        # Create UI elements
        self.create_widgets()
        self.refresh_ports()

        # Start queue processing
        self.after(10, self.process_queue)

        # Configure window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # FRAME LATERAL ESQUERDA (Zona de Informações)
        self.info_frame = ttk.Frame(self, width=200, relief=tk.SUNKEN, borderwidth=2)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(self.info_frame, text="Informações", font=("Arial", 12, "bold")).pack(pady=5)

        # Temperatura
        self.temp_label = ttk.Label(self.info_frame, text="Temperatura: -- °C", font=("Arial", 10))
        self.temp_label.pack(pady=5)

        # Serial port selection
        self.port_frame = ttk.Frame(self)
        self.port_frame.pack(pady=5)

        ttk.Label(self.port_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_combo = ttk.Combobox(self.port_frame, width=30)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(self.port_frame, text="Refresh", command=self.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(self.port_frame, text="Connect", command=self.connect_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        # HEX file selection
        self.file_frame = ttk.Frame(self)
        self.file_frame.pack(pady=5)

        ttk.Label(self.file_frame, text="HEX File:").pack(side=tk.LEFT, padx=5)
        self.file_entry = ttk.Entry(self.file_frame, width=40)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_btn = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        # Log display
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # Serial input prompt
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Send:").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(self.input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.send_serial_input)

        self.send_btn = ttk.Button(self.input_frame, text="Send", command=self.send_serial_input)
        self.send_btn.pack(side=tk.LEFT)

        # Control buttons
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.control_frame, text="Start Update", command=self.start_update,
                                    state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.reboot_btn = ttk.Button(self.control_frame, text="Reboot", command=self.send_serial_input("4"))
        self.reboot_btn.pack(side=tk.LEFT, padx=5)

    def refresh_ports(self):
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        ports.reverse()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def process_queue(self):
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                if msg['type'] == 'log':
                    self.log_area.insert(tk.END, msg['message'] + "\n")
                    self.log_area.see(tk.END)
                elif msg['type'] == 'update_ui':
                    self.temp_label.config(text=f"Temperatura: {msg['temp']} °C")
            except queue.Empty:
                pass
        self.after(10, self.process_queue)

    def connect_serial(self):
        '''
        if self.ser and self.ser.is_open:
            self.log("Already connected to serial port.")
            return
        '''

        port = self.port_combo.get().split(' - ')[0]
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return

        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.running = True
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"Connected to {port} at 115200 baud")

            # Start serial read thread
            threading.Thread(target=self.read_serial, daemon=True).start()

        except Exception as e:
            self.log(f"Connection error: {str(e)}")
            self.running = False
            self.connect_btn.config(state=tk.NORMAL)

    def read_serial(self):
        while self.running and self.ser and self.ser.is_open:
            try:

                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode('utf-8', errors='ignore').strip()

                    # Ignore debug messages, but log them
                    if response.startswith("DEBUG:"):
                        debug_message = response[6:].strip()
                        self.queue.put({'type': 'log', 'message': f" Debug: {debug_message}"})  # Send to GUI log
                        print(f" Debug Message: {response[6:].strip()}")
                        continue

                if self.ser.in_waiting >= 16:
                    data = self.ser.read(16)
                    # Ensure we read exactly 16 bytes (full OpCodePacket size)
                    if len(data) != 16:
                        print("⚠ Incomplete packet received, ignoring...")
                        error_count += 1
                        if error_count > 10:  # Too many errors? Reset.
                            print("⚠ Too many errors! Resetting serial connection...")
                            self.ser.close()
                            time.sleep(2)
                            self.connect_serial()
                            error_count = 0  # Reset error counter
                        continue

                    # Unpack header fields
                    sync_word, packet_type, command_code, payload_length = struct.unpack("<H B B B", data[:5])

                    # Validate Sync Word
                    if sync_word != 0xA55A:
                        print("⚠ Invalid packet received (Sync Word mismatch)")
                        continue  # Ignore this packet

                    # Extract temperature
                    payload = data[5:13]
                    temp_celsius = struct.unpack("<f", payload[:4])[0]

                    # Validate checksum
                    checksum_received = data[13]
                    checksum_calculated = self.calculate_checksum(data)

                    if checksum_received != checksum_calculated:
                        print(f"⚠ Checksum mismatch! Received {checksum_received}, Expected {checksum_calculated}")
                        continue  # Ignore corrupted packet

                    # Update UI with valid temperature data
                    self.queue.put({
                        'type': 'update_ui',
                        'temp': round(temp_celsius, 2)
                    })

                    print(f"✅ Received Temp: {temp_celsius:.2f}°C")

            except serial.SerialException as e:
                print(f"⚠ Serial Error: {e}")
                self.ser.close()
                time.sleep(2)
                self.connect_serial()

    def calculate_checksum(self, packet):
        checksum = 0
        for byte in packet[:-3]:  # XOR all bytes except last 3 (checksum + end marker)
            checksum ^= byte
        return checksum

    def send_serial_input(self, text = ""):
        print(text)
        if self.ser and self.ser.is_open:
            if text == "":
                text = self.input_entry.get()
            if text:
                self.ser.write((text + '\n').encode())
                self.log(f">>> {text}")
                self.input_entry.delete(0, tk.END)


    def disconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.running = False
            self.log("Serial port disconnected.")
            self.start_btn.config(state=tk.DISABLED)

    def start_update(self):
        if not self.ser or not self.ser.is_open:
            messagebox.showerror("Error", "Not connected to serial port")
            return

        hex_file = self.file_entry.get()
        if not hex_file:
            messagebox.showerror("Error", "Please select a HEX file")
            return

        # Start update process in separate thread
        threading.Thread(target=self.perform_update, args=(hex_file,), daemon=True).start()

    def perform_update(self, hex_file):
        try:
            # Send upload command
            self.ser.write(b'1\n')
            self.queue.put({'type': 'log', 'message': ">>> Started serial upload"})

            # Read and send HEX file
            with open(hex_file, 'rb') as f:
                hex_data = f.read()
                self.ser.write(hex_data)
                self.queue.put({'type': 'log', 'message': f"Sent HEX file: {hex_file}"})

            time.sleep(1)  # Wait for processing

        except Exception as e:
            self.queue.put({'type': 'log', 'message': f"Error: {str(e)}"})

    def on_closing(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()

    def reconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.queue.put({'type': 'log', 'message': "Serial port closed. Waiting for device..."})

        time.sleep(1)  # Wait for the board to reboot

        try:
            port = self.port_combo.get().split(' - ')[0]
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.queue.put({'type': 'log', 'message': f"Reconnected to {port}."})

            # Restart reading thread
            threading.Thread(target=self.read_serial, daemon=True).start()

        except Exception as e:
            self.queue.put({'type': 'log', 'message': f"Reconnection failed: {str(e)}"})




if __name__ == "__main__":
    app = FirmwareUpdaterApp()
    app.mainloop()