import tkinter as tk
from tkinter import ttk, scrolledtext
from serial_comm import SerialCommunication
from console import Console

class ConsoleUI:
    def __init__(self, master, serial_comm: SerialCommunication, console: Console):
        self.master = master
        self.serial_comm = serial_comm
        self.console = console
        self.command_history = []
        self.history_index = -1

        self.create_widgets()

        # Process console messages from queue
        self.master.after(10, self.process_queue)

    def create_widgets(self):
        """Creates the console log display and input field."""
        self.console_frame = ttk.Frame(self.master)
        self.console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log display area
        self.log_area = scrolledtext.ScrolledText(self.console_frame, wrap=tk.WORD, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Input frame for sending strings in the Console Logs tab
        self.console_input_frame = ttk.Frame(self.console_frame)
        self.console_input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_entry = ttk.Entry(self.console_input_frame, width=30)
        self.input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.send_console_input)
        self.input_entry.bind("<Up>", self.show_previous_command)
        self.input_entry.bind("<Down>", self.show_next_command)

        self.send_btn = ttk.Button(self.console_input_frame, text="Send", command=self.send_console_input)
        self.send_btn.pack(side=tk.LEFT, padx=5)

    def send_console_input(self, event=None):
        """Sends input from console UI to the serial port."""
        text = self.input_entry.get().strip()
        if text:
            try:
                self.serial_comm.send_serial_input(text)
                self.log(f">>> {text}")
                self.command_history.append(text)
                self.history_index = len(self.command_history)
                self.input_entry.delete(0, tk.END)
            except Exception as e:
                self.log(f"Error: {str(e)}")

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
            self.history_index = len(self.command_history)
            self.input_entry.delete(0, tk.END)

    def log(self, message):
        """Adds a log message to the console output."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def process_queue(self):
        """Processes queued messages from SerialCommunication."""
        while not self.console.queue.empty():
            try:
                msg = self.console.queue.get_nowait()
                if msg['type'] == 'log':
                    self.log(msg['message'])
            except self.console.queue.Empty:
                pass
        self.master.after(10, self.process_queue)
