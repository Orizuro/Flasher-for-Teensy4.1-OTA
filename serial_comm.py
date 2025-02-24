import serial
import serial.tools.list_ports
import threading
import queue
import time

class SerialCommunication:
    def __init__(self, console=None):  # Added optional console argument
        self.ser = None
        self.running = False
        self.queue = queue.Queue()
        self.console = console  # Store console reference if provided

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
        """Read data from the serial port."""
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    self.log_to_console(f"<<< {response}")
            except Exception as e:
                raise IOError(f"Error reading from serial: {str(e)}")

    def log_to_console(self, message):
        """Send log messages to the console UI if available."""
        if self.console:
            self.console.queue.put({"type": "log", "message": message})
