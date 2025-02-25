import tkinter as tk
from tkinter import ttk
from serial_comm import SerialCommunication
from serial_ui import SerialUI
from consoleUI import ConsoleUI
from console import Console
from opcodeUi import OpcodeUI
from updateUi import UpdaterUI

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
        self.notebook.add(self.tab1, text="Firmware Update")
        self.updater_ui = UpdaterUI(self.tab1, self.serial_comm, self.console)

        # Tab 2 (Mockup)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Tab 2")
        ttk.Label(self.tab2, text="This is another mockup tab").pack(pady=20)

        self.opcodes_tab = OpcodeUI(self.notebook, self.serial_comm)
        self.notebook.add(self.opcodes_tab.get_frame(), text="Opcodes")

if __name__ == "__main__":
    app = FirmwareUpdaterApp()
    app.mainloop()
