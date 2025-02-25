import struct

class Battery:
    def __init__(self, serial_comm):
        self.serial_comm = serial_comm  # Link to serial communication

    def process_packet(self, data):
        """Extract battery status from incoming binary data."""
        if len(data) != 16:
            return None, "Incomplete packet"

        sync_word, = struct.unpack("<H", data[0:2])
        if sync_word != 0xA55A:
            return None, "Invalid Sync Word"

        # Extract battery voltage (float) and percentage (int)
        voltage, = struct.unpack("<f", data[5:9])
        percentage, = struct.unpack("<B", data[9:10])

        # Validate checksum
        checksum_received = data[13]
        checksum_calculated = self._calculate_checksum(data)
        if checksum_received != checksum_calculated:
            return None, "Checksum mismatch"

        return {"voltage": round(voltage, 2), "percentage": percentage}, None  # Return battery data and no error

    def _calculate_checksum(self, packet):
        """Calculates the XOR checksum over the packet except last 3 bytes."""
        checksum = 0
        for b in packet[:-3]:
            checksum ^= b
        return checksum
