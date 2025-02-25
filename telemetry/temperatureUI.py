import tkinter as tk
from tkinter import ttk

class TemperatureUI:
    def __init__(self, master, temperature_module):
        self.master = master
        self.temperature_module = temperature_module  # Link to temperature processing

        self.create_widgets()

    def create_widgets(self):
        """Creates UI elements for temperature display."""
        self.temp_frame = ttk.Frame(self.master)
        self.temp_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.temp_label = ttk.Label(self.temp_frame, text="Temperatura: -- °C", font=("Arial", 12))
        self.temp_label.pack(pady=5)

    def update_temperature(self, temp_value):
        """Update the displayed temperature."""
        self.temp_label.config(text=f"Temperatura: {temp_value} °C")
