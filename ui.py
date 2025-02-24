import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class FirmwareUpdaterUI:
    def __init__(self, master, serial_comm):
        self.master = master
        self.serial_comm = serial_comm
        self.create_widgets()

    def create_widgets(self):
        # Serial port selection
        self.port_frame = ttk.Frame(self.master)
        self.port_frame.pack(pady=5)

        ttk.Label(self.port_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_combo = ttk.Combobox(self.port_frame, width=30)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(self.port_frame, text="Refresh", command=self.serial_comm.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(self.port_frame, text="Connect", command=self.serial_comm.connect_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        # HEX file selection
        self.file_frame = ttk.Frame(self.master)
        self.file_frame.pack(pady=5)

        ttk.Label(self.file_frame, text="HEX File:").pack(side=tk.LEFT, padx=5)
        self.file_entry = ttk.Entry(self.file_frame, width=40)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_btn = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        # Log display
        self.log_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.log_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # Serial input prompt
        self.input_frame = ttk.Frame(self.master)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Send:").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(self.input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.serial_comm.send_serial_input)
        self.input_entry.bind("<Up>", self.serial_comm.show_previous_command)
        self.input_entry.bind("<Down>", self.serial_comm.show_next_command)

        self.send_btn = ttk.Button(self.input_frame, text="Send", command=self.serial_comm.send_serial_input)
        self.send_btn.pack(side=tk.LEFT)

        # Control buttons
        self.control_frame = ttk.Frame(self.master)
        self.control_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.control_frame, text="Start Update", command=self.serial_comm.start_update,
                                    state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.reboot_btn = ttk.Button(self.control_frame, text="Reboot", command=lambda: self.serial_comm.send_serial_input("4"))
        self.reboot_btn.pack(side=tk.LEFT, padx=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
