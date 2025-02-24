import tkinter as tk
from time import sleep
from tkinter import ttk, filedialog, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import queue
import time

opcode_list = {"update": 1, "reboot": 2, "commit update": 3}

class FirmwareUpdaterAppOld(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Firmware Updater")
        self.geometry("800x800")

        # Serial communication variables
        self.ser = None
        self.running = False
        self.queue = queue.Queue()
        self.confirm_lines = None
        self.command_history = []  # Stores sent commands
        self.history_index = -1  # Tracks history position

        # Create UI elements
        self.create_widgets()
        self.refresh_ports()

        # Start queue processing
        self.after(10, self.process_queue)

        # Configure window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
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
        self.input_entry.bind("<Up>", self.show_previous_command)
        self.input_entry.bind("<Down>", self.show_next_command)

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


    def send_serial_input(self, event=None):
        if self.ser and self.ser.is_open:
            text = self.input_entry.get().strip()
            if text:
                self.ser.write((text + '\n').encode())
                self.log(f">>> {text}")
                self.command_history.append(text)  # Store command
                self.history_index = len(self.command_history)  # Reset index
                self.input_entry.delete(0, tk.END)

    def show_previous_command(self, event):
        """Navigate up in command history."""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])

    def show_next_command(self, event):
        """Navigate down in command history."""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)  # Reset index
            self.input_entry.delete(0, tk.END)  # Clear input field

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
                    self.log(msg['message'])
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
                    if response:
                        self.queue.put({'type': 'log', 'message': f"<<< {response}"})
                    if "rebooting..." in response:
                        self.disconnect_serial()
                        sleep(2)
                        self.connect_serial()
            except:
                break

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
    app = FirmwareUpdaterAppOld()
    app.mainloop()
