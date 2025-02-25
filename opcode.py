import struct

class Opcode:
    """Handles opcode structure and packet building."""

    def __init__(self):
        self.sync_word = 0xA55A  # 2 bytes
        self.end_marker = 0xB77B  # 2 bytes

    def build_packet(self, packet_type, command_code, payload):
        """Builds a packet according to the protocol specification."""
        payload_length = len(payload)  # Payload length is dynamic
        payload_bytes = payload.ljust(8, b"\x00")  # Ensure 8-byte payload

        # Pack fields into binary format
        sync_word = struct.pack(">H", self.sync_word)
        packet_type = struct.pack("B", packet_type)
        command_code = struct.pack("B", command_code)
        payload_length = struct.pack("B", payload_length)
        checksum_data = packet_type + command_code + payload_length + payload_bytes
        checksum = struct.pack("B", self.calculate_checksum(checksum_data))
        end_marker = struct.pack(">H", self.end_marker)

        # Full packet
        packet = sync_word + packet_type + command_code + payload_length + payload_bytes + checksum + end_marker
        return packet

    @staticmethod
    def calculate_checksum(data):
        """Calculates XOR checksum for the given data."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
