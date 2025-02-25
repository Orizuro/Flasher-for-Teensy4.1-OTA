import tkinter as tk
from tkinter import ttk, messagebox
from serial_comm import SerialCommunication

class SerialUI:        # Serial Port Ta
    def __init__(self, master, serial_comm: SerialCommunication):
        self.master = master
        self.serial_comm = serial_comm

        self.create_widgets()
        self.get_ports()

    def create_widgets(self):
        """Creates UI elements for selecting and connecting to a serial port."""
        self.port_frame = ttk.Frame(self.master)
        self.port_frame.pack(pady=5)

        ttk.Label(self.port_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_combo = ttk.Combobox(self.port_frame, width=30)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(self.port_frame, text="Refresh", command=self.get_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(self.port_frame, text="Connect", command=self.connect_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

    def get_ports(self):
        """Refresh available serial ports."""
        ports = self.serial_comm.refresh_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def connect_serial(self):
        """Connect to the selected serial port."""
        port = self.port_combo.get().split(' - ')[0]
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return
        try:
            self.serial_comm.connect_serial(port)
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    # In SerialUI

    def send_serial_input(self):
        """Send command from input field to Teensy."""
        input_data = self.input_entry.get().strip()
        if input_data:
            self.serial_comm.send_serial_input(input_data)
            self.console.queue.put({"type": "log", "message": f"Sent: {input_data}"})
            self.input_entry.delete(0, tk.END)

    # Add a command history feature
    def show_previous_command(self, event):
        """Navigate through command history."""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
