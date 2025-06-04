import serial
import time

# --- Configuration ---
# You may need to change this depending on your system.
# Common port names:
# - Windows: "COM3", "COM4", etc. (e.g., 'COM3')
# - Linux: "/dev/ttyUSB0", "/dev/ttyACM0", etc.
# - macOS: "/dev/cu.usbmodemXXXX", "/dev/cu.wchusbserialXXXX", etc.
SERIAL_PORT = 'COM5'  # <<<< IMPORTANT: CHANGE THIS TO YOUR ARDUINO'S PORT ON WINDOWS
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds to wait for serial data

# --- Main Program ---
def main():
    """
    Main function to connect to Arduino and send servo commands.
    This script is designed to work with an Arduino sketch that expects
    angle inputs from 0 to 180 degrees.
    """
    ser = None  # Initialize ser to None
    print("Python Servo Controller for Arduino (0-180 Range)")
    print("-------------------------------------------------")
    print(f"Attempting to connect to Arduino on port {SERIAL_PORT} at {BAUD_RATE} baud.")

    try:
        # Establish serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"Successfully connected to {ser.name}.")
        # Wait for Arduino to reset and initialize. This is crucial.
        # Arduino Uno resets on serial connection by default.
        print("Waiting for Arduino to initialize (2 seconds)...")
        time.sleep(2)

        # Read and display initial messages from Arduino (e.g., welcome messages from its setup() function)
        print("Reading initial messages from Arduino...")
        while ser.in_waiting > 0:
            try:
                arduino_message = ser.readline().decode('utf-8').strip()
                if arduino_message: # Only print if there's actual content
                    print(f"Arduino: {arduino_message}")
            except UnicodeDecodeError:
                # This can happen if the Arduino sends some non-text data during startup,
                # or if the baud rates don't perfectly match initially.
                print("Arduino: [Received non-UTF-8 data during initialization]")
        print("----------------------------------------------------")


        while True:
            try:
                # Get user input
                user_input = input("Enter angle (0 to 180, or 'exit' to quit): ").strip()

                if user_input.lower() == 'exit':
                    print("Exiting program.")
                    break

                # Validate input
                try:
                    angle = int(user_input)
                    # Check if the angle is within the 0-180 range
                    if 0 <= angle <= 180:
                        # Send the command to Arduino
                        # The Arduino code expects a newline character ('\n') at the end of the command.
                        command = f"{angle}\n"
                        ser.write(command.encode('utf-8')) # Encode string to bytes for serial transmission
                        print(f"Sent to Arduino: {angle}")

                        # Wait a short moment for Arduino to process the command and respond
                        time.sleep(0.1) # Adjust if necessary

                        # Read response lines from Arduino
                        response_lines_read = 0
                        max_expected_response_lines = 3 # Read a few lines to catch multi-line or delayed responses
                        
                        # Give Arduino a bit more time to send its response
                        # This loop attempts to read for a short duration or until data is found
                        read_attempt_duration = 0.5 # seconds
                        start_read_time = time.time()
                        while (time.time() - start_read_time < read_attempt_duration) and response_lines_read < max_expected_response_lines :
                            if ser.in_waiting > 0:
                                try:
                                    arduino_response = ser.readline().decode('utf-8').strip()
                                    if arduino_response: # Only print if there's actual content
                                        print(f"Arduino: {arduino_response}")
                                        response_lines_read += 1
                                except UnicodeDecodeError:
                                    print("Arduino: [Received non-UTF-8 data in response]")
                                    response_lines_read += 1 # Count it as a line read to avoid infinite loops on bad data
                            else:
                                time.sleep(0.05) # Briefly pause if no data, to not hog CPU

                        if response_lines_read == 0:
                            # This might happen if the Arduino sketch doesn't always send a reply
                            # or if the reply is too slow and TIMEOUT is too short.
                            # The Arduino sketch you provided *does* send a reply.
                            # print("Arduino: [No response received within timeframe]")
                            pass

                    else:
                        print("Invalid angle. Please enter a value between 0 and 180.")
                except ValueError:
                    print("Invalid input. Please enter a numeric value (e.g., 90) or 'exit'.")

            except KeyboardInterrupt:
                print("\nExiting program due to user interruption (Ctrl+C).")
                break
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
                print("Lost connection to Arduino or port unavailable. Please check the connection and port settings.")
                break

    except serial.SerialException as e:
        print(f"Error: Could not open serial port '{SERIAL_PORT}'. Details: {e}")
        print("Please ensure:")
        print("  1. Your Arduino is connected to the computer.")
        print("  2. You have selected the correct COM port in the SERIAL_PORT variable.")
        print("     (On Windows, it's usually COM3, COM4, etc. Check Device Manager -> Ports (COM & LPT))")
        print("  3. The Arduino IDE's Serial Monitor is closed (it can't share the port).")
        print("  4. You have the necessary permissions to access the serial port.")
    finally:
        if ser and ser.is_open:
            ser.close()
            print(f"Serial port {SERIAL_PORT} closed.")

if __name__ == "__main__":
    main()
