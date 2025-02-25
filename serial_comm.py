from telemetry.temperature import Temperature

import serial
import serial.tools.list_ports
import threading
import queue
import time
import struct

class SerialCommunication:
    def __init__(self, console=None):  # Added optional console argument
        self.ser = None
        self.running = False
        self.queue = queue.Queue()
        self.console = console  # Store console reference if provided

        self.temperature = Temperature(self)


    def refresh_ports(self):
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        ports.reverse()
        return ports

    def connect_serial(self, port):
        if not port:
            raise ValueError("Please select a serial port")
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.running = True
            threading.Thread(target=self.read_serial, daemon=True).start()
            self.log_to_console(f"Connected to {port} at 115200 baud")
        except Exception as e:
            raise ConnectionError(f"Connection error: {str(e)}")

    def disconnect_serial(self):
        """Disconnect from the current serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.running = False
            self.log_to_console("Serial port disconnected.")
            return "Serial port disconnected."
        return "No active connection to disconnect."

    def send_serial_input(self, input_data, encoding='utf-8'):
        """Send data to the serial port."""
        if self.ser and self.ser.is_open:
            if input_data:
                encoded_data = input_data.encode(encoding)
                self.ser.write(encoded_data)
                return f"Sent: {input_data}"
            return "No data to send."
        raise ValueError("Not connected to serial port")


    def read_serial(self):
        """Reads data from serial and sends it to the correct telemetry module or console."""
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode("utf-8", errors="ignore").strip()  # Read full line
                    if data:
                        self.console.log(f"<<< {data}")  # Log response to console
                        self.queue.put({'type': 'log', 'message': f"<<< {data}"})

                    # If the response is related to temperature (16-byte packet)
                    if len(data) == 16:
                        temp_value, error = self.temperature.process_packet(data.encode())
                        if error:
                            self.log_to_console(error)
                            continue
                        self.queue.put({'type': 'temperature', 'value': temp_value})

                    else:
                         #Log any other responses (like firmware version)
                        self.console.log(data)  # Send it to ConsoleUI
                        self.queue.put({'type': 'log', 'message': data})  # Store in queue

            except Exception as e:
                self.log_to_console(f"Error reading from serial: {str(e)}")

    def log_to_console(self, message):
        """Send log messages to the console UI if available."""
        if self.console:
            if self.console.queue:
                self.console.queue.put({"type": "log", "message": message})

    # In serial_comm.py, inside SerialCommunication class

    def _calculate_checksum(self, packet: bytes) -> int:
        """Calculates the XOR checksum over the packet except the last 3 bytes (checksum and end marker)."""
        checksum = 0
        # Assuming packet is 16 bytes; XOR first 13 bytes.
        for b in packet[:-3]:
            checksum ^= b
        return checksum
