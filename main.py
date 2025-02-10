import serial
import serial.tools.list_ports
import threading
import time

# Global flag to control the serial read thread
running = True

# Function to read from the serial port and print received messages
def read_serial(ser):
    while running:
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(f"Received: {response}")
                # Check if the response contains the "enter XXXX to flash or 0 to abort" message
                if "enter" in response and "to flash or 0 to abort" in response:
                    # Extract the number of lines from the response
                    try:
                        lines = response.split()[1]  # Extract the number (e.g., 4552)
                        print(f"Detected request to confirm {lines} lines.")
                        # Prompt the user to input the code
                        user_input = input(f"Enter {lines} to confirm or 0 to abort: ")
                        # Send the user input to the Arduino
                        ser.write((user_input + '\n').encode())
                        print(f"Sent: {user_input}")
                    except IndexError:
                        print("Failed to parse the number of lines from the response.")
        time.sleep(0.1)  # Small delay to avoid busy-waiting

# Function to list all available serial ports
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return None
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    return ports

# Main function
def main():
    global running

    # List all available serial ports
    ports = list_serial_ports()
    if not ports:
        return

    # Let the user select a serial port
    try:
        choice = int(input("Enter the number of the serial port to use: ")) - 1
        if choice < 0 or choice >= len(ports):
            print("Invalid choice.")
            return
        com_port = ports[choice].device
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # Configuration
    baud_rate = 115200

    # Open serial connection
    try:
        ser = serial.Serial(com_port, baud_rate, timeout=1)
        print(f"Connected to {com_port} at {baud_rate} baud.")
    except Exception as e:
        print(f"Failed to connect to {com_port}: {e}")
        return

    # Start the serial read thread
    serial_thread = threading.Thread(target=read_serial, args=(ser,))
    serial_thread.start()

    try:
        # Wait for the Arduino to initialize
        time.sleep(2)  # Give the Arduino time to boot and send its initial messages

        # Wait for the user to input the HEX file name
        hex_file_path = input("Enter the path to the HEX file: ")

        # Send '1' to choose serial upload
        ser.write(b'1\n')
        print("Sent '1' to choose serial upload.")

        # Wait for the Arduino to acknowledge
        time.sleep(1)

        # Send HEX file
        try:
            with open(hex_file_path, 'rb') as hex_file:
                hex_data = hex_file.read()
                ser.write(hex_data)
                print(f"Sent HEX file: {hex_file_path}")
        except FileNotFoundError:
            print(f"File not found: {hex_file_path}")
            running = False
            return

        # Wait for the Arduino to process the HEX file and reboot
        time.sleep(5)  # Adjust this delay based on the size of the HEX file

    except KeyboardInterrupt:
        print("\nUser interrupted the process.")

if __name__ == "__main__":
    main()