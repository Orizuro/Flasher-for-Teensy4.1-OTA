import threading
import time

class Updater:
    def __init__(self, serial_comm, console):
        self.serial_comm = serial_comm
        self.console = console
        self.is_updating = False

    def start_update(self, hex_file):
        """Start the firmware update in a separate thread."""
        if self.is_updating:
            self.console.log("Update already in progress...")
            return

        if not self.serial_comm.ser or not self.serial_comm.ser.is_open:
            self.console.log("Error: Not connected to serial port")
            return

        if not hex_file:
            self.console.log("Error: Please select a HEX file")
            return

        self.is_updating = True
        update_thread = threading.Thread(target=self.perform_update, args=(hex_file,), daemon=True)
        update_thread.start()

    def perform_update(self, hex_file):
        """Perform the firmware update process."""
        try:
            self.console.log(">>> Starting firmware update...")

            # Send command to start update
            self.serial_comm.send_data(b'1\n')
            self.console.log(">>> Sent update start command")

            # Read HEX file and send data

            with open(hex_file, 'rb') as f:
                hex_data = f.read()
                self.serial_comm.send_data(hex_data)
                self.console.log(f">>> Sent HEX file: {hex_file}")

            time.sleep(1)  # Simulate processing time
            self.console.log(">>> Update complete!")

        except Exception as e:
            self.console.log(f"Error: {str(e)}")

        finally:
            self.is_updating = False
