import tkinter as tk
from tkinter import ttk, filedialog
from update import Updater

class UpdaterUI:
    def __init__(self, master, serial_comm, console):
        self.master = master
        self.serial_comm = serial_comm
        self.console = console
        self.updater = Updater(serial_comm, console)

        self.create_widgets()

    def create_widgets(self):
        """Create UI for firmware update process."""
        self.file_frame = ttk.Frame(self.master)
        self.file_frame.pack(pady=5)

        ttk.Label(self.file_frame, text="HEX File:").pack(side=tk.LEFT, padx=5)
        self.file_entry = ttk.Entry(self.file_frame, width=40)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=5)

        self.browse_btn = ttk.Button(self.button_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(self.button_frame, text="Start Update", command=self.start_update, state=tk.NORMAL)
        self.start_btn.pack(side=tk.LEFT, padx=5)

    def browse_file(self):
        """Open file dialog to select HEX file."""
        filename = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def start_update(self):
        """Trigger firmware update."""
        hex_file = self.file_entry.get()
        self.updater.start_update(hex_file)
