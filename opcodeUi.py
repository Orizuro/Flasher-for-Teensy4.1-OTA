import tkinter as tk
from tkinter import ttk
from opcode import Opcode

class OpcodeUI:
    """Manages the Opcode Tab UI and sending packets."""

    def __init__(self, parent, serial_comm):
        self.serial_comm = serial_comm
        self.opcode_handler = Opcode()

        # UI Elements
        self.frame = ttk.Frame(parent)
        self.opcodes = self.load_opcodes_from_file("opcode.txt")  # Load from file
        self.create_ui()

    def load_opcodes_from_file(self, filename):
        """Reads opcodes from a text file and returns a list of tuples (name, hex_value)."""
        opcodes = []
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(maxsplit=1)  # Ensure only two parts (name + hex)
                    if len(parts) == 2:
                        name, hex_value = parts
                        try:
                            hex_value = int(hex_value, 16)  # Convert hex string to integer
                            opcodes.append((name, hex_value))
                        except ValueError:
                            pass  # Ignore invalid hex values
        except FileNotFoundError:
            with open(filename, "w") as file:
                file.write("GET_TELEMETRY 0x0110\nRESET_SYSTEM 0x0120\nPOWER_OFF 0x0130\nSET_MODE 0x0140\n")
            return self.load_opcodes_from_file(filename)  # Reload after creating

        return opcodes

    def create_ui(self):
        """Creates UI elements to display opcode list."""
        self.tree = ttk.Treeview(self.frame, columns=("Name", "Opcode"), show="headings")
        self.tree.heading("Name", text="Opcode Name")
        self.tree.heading("Opcode", text="Hex Value")
        self.tree.column("Name", anchor="center", width=150)
        self.tree.column("Opcode", anchor="center", width=100)

        # Insert opcodes into table
        for name, hex_value in self.opcodes:
            self.tree.insert("", tk.END, values=(name, f"0x{hex_value:04X}"))

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Send Button
        self.send_button = ttk.Button(self.frame, text="Send Opcode", command=self.send_opcode)
        self.send_button.pack(pady=10)

    def send_opcode(self):
        """Handles sending the selected opcode from the list."""
        selected_item = self.tree.selection()
        if selected_item:
            name, hex_value = self.tree.item(selected_item, "values")
            hex_value = int(hex_value, 16)  # Convert from hex string to int
            packet_type = (hex_value >> 8) & 0xFF  # Extract Packet Type
            command_code = hex_value & 0xFF       # Extract Command Code
            payload = b"\x00\x00\x00\x00\x00\x00\x00\x00"  # 8-byte default payload

            # Build and send the packet
            packet = self.opcode_handler.build_packet(packet_type, command_code, payload)
            self.serial_comm.send_data(packet)
            print(f"Sent Opcode '{name}': {packet.hex()}")  # Debug output
        else:
            print("No opcode selected!")

    def get_frame(self):
        """Returns the UI frame for integration."""
        return self.frame
