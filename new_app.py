import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from serial_comm import SerialCommunication
from serial_ui import SerialUI
from consoleUI import ConsoleUI
from console import Console
from telemetry.temperatureUI import TemperatureUI


class FirmwareUpdaterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Firmware Updater")
        self.geometry("800x600")

        # Create a vertical PanedWindow (splits Serial UI from bottom section)
        self.vertical_pane = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.vertical_pane.pack(fill=tk.BOTH, expand=True)

        # Top - Serial UI
        self.serial_frame = ttk.Frame(self.vertical_pane, height=50)
        self.serial_frame.pack_propagate(False)  # Prevent auto-resizing
        self.vertical_pane.add(self.serial_frame)

        # Create console instance first
        self.console = Console()
        self.serial_comm = SerialCommunication(console=self.console)
        self.serial_ui = SerialUI(self.serial_frame, self.serial_comm)

        # Bottom - Split into two halves (Console and Tabs)
        self.bottom_pane = tk.PanedWindow(self.vertical_pane, orient=tk.HORIZONTAL)
        self.vertical_pane.add(self.bottom_pane)

        # Left - Console UI
        self.console_frame = ttk.Frame(self.bottom_pane, width=500)
        self.console_frame.pack_propagate(False)
        self.bottom_pane.add(self.console_frame)

        ConsoleUI(self.console_frame, self.serial_comm, self.console)

        # Right - Tabs
        self.tabs_frame = ttk.Frame(self.bottom_pane, width=400)
        self.bottom_pane.add(self.tabs_frame)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.tabs_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1 (Mockup)
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Tab 1")
        ttk.Label(self.tab1, text="This is a mockup tab").pack(pady=20)

        # Tab 2 - Temperature Display
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Info")

        # Create TemperatureUI instance
        self.temperature_ui = TemperatureUI(self.tab2, self.serial_comm.temperature)

        # Start processing the serial queue for updates
        self.process_serial_queue()


    def process_serial_queue(self):
        """Process incoming serial messages (like temperature updates)."""
        try:
            while not self.serial_comm.queue.empty():
                msg = self.serial_comm.queue.get_nowait()
                if msg['type'] == 'temperature':
                    self.temperature_ui.update_temperature(msg['value'])
        except Exception as e:
            print(f"Error processing serial queue: {e}")
        self.after(100, self.process_serial_queue)


if __name__ == "__main__":
    app = FirmwareUpdaterApp()
    app.mainloop()
