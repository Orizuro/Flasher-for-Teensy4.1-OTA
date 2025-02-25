import tkinter as tk
from tkinter import ttk

class BatteryUI:
    def __init__(self, master, battery_module):
        self.master = master
        self.battery_module = battery_module  # Link to battery processing

        self.create_widgets()

    def create_widgets(self):
        """Creates UI elements for battery display."""
        self.battery_frame = ttk.Frame(self.master)
        self.battery_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.voltage_label = ttk.Label(self.battery_frame, text="Voltage: -- V", font=("Arial", 12))
        self.voltage_label.pack(pady=5)

        self.percentage_label = ttk.Label(self.battery_frame, text="Battery: --%", font=("Arial", 12))
        self.percentage_label.pack(pady=5)

    def update_battery(self, battery_data):
        """Update the displayed battery information."""
        voltage = battery_data.get("voltage", "--")
        percentage = battery_data.get("percentage", "--")

        self.voltage_label.config(text=f"Voltage: {voltage} V")
        self.percentage_label.config(text=f"Battery: {percentage}%")
