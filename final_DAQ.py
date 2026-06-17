import gclib #galil/gantry operation library
import time
import numpy as np
import paramiko #need to connect cameras 
import serial
import sys

# --- Configuration ---

# -- Gantry Controller Configuration --
GANTRY_SERIAL_PORT = '/dev/ttyUSB0' # Serial port for the Galil controller(can change)
GANTRY_BAUD_RATE = 19200      # Baud rate for the serial connection(fixed)

# -- Gantry Motion Parameters(we can change, keep it fixed) --
SPEED_XY_COUNTS_PER_SEC = 200000
ACCEL_XY_COUNTS_PER_SEC_SQ = 100000
DECEL_XY_COUNTS_PER_SEC_SQ = 100000
HOMING_SPEED_COUNTS_PER_SEC = 10000
RECOVERY_DISTANCE_FORWARD = 10000
RECOVERY_DISTANCE_REVERSE = -10000

# -- Gantry Axis Mapping(define x,y plane) --
X_AXIS = 'A'
Y_AXIS = 'B'

# -- Target Positions in step size(change based on your data set) --
X_POSITIONS = list(np.linspace(10000, 90000, 2))
Y_POSITIONS = list(np.linspace(10000, 50000, 2))

# -- Gantry Limit Switch Configuration(if not working try True) --
CN_SETTING_IS_ACTIVE_HIGH = False

# -- Raspberry Pi & Camera Configuration(only for camera not for DOM) --
RPI_HOST = 'ICUpi10.local' #camera id
RPI_USER = 'pi'
RPI_PASS = 'icepingu'   #password
TEST_NAME = "7_May_full_DAQ" #change name accordingly
GANTRY_Z_POS = 0.0  #measure from gantry plane to the laser head(height)
CAMERA_GAIN = 0.0
CAMERA_EXPOSURE = 55

# -- Arduino & Servo Configuration --
# IMPORTANT: Change this to your Arduino's serial port!
# Windows: "COM3", "COM4", etc.
# Linux: "/dev/ttyACM0", "/dev/ttyUSB0", etc.
ARDUINO_SERIAL_PORT = '/dev/ttyACM1'  #can change based on your connection
ARDUINO_BAUD_RATE = 9600  #fixed
SERVO_ANGLES = [20, 50, 60, 91, 120] # List of angles for the servo to cycle through
SERVO_MOVE_DELAY_S = 1.0 # Seconds to wait for the servo to physically move

# -- General Timing --
# Time to wait after gantry move and after each camera shot
POST_MOVE_INTERVAL_S = 0.5 #500 ms pause


# --- Helper Functions ---

def get_limit_status_for_homing(g, axis, cn_is_active_high):
  """Checks and interprets the limit switch status for an axis."""
  try:
    ts_val_str = g.GCommand(f"TS{axis}").strip()
    ts_val = int(ts_val_str)
  except (ValueError, gclib.GclibError) as e:
    print(f"Warning: Could not parse TS{axis} response. Error: {e}")
    return False, False, 0
  if cn_is_active_high:
    fwd_active = bool((ts_val >> 3) & 1)
    rev_active = bool((ts_val >> 2) & 1)
  else:
    fwd_active = not bool((ts_val >> 3) & 1)
    rev_active = not bool((ts_val >> 2) & 1)
  return fwd_active, rev_active, ts_val

def home_axis_to_reverse_limit(g, axis, axis_name, cn_is_active_high):
  """Homes a single axis to its REVERSE limit switch and defines that position as 0."""
  print(f"\n--- Homing {axis_name} ({axis}) to REVERSE limit ---")
  _, rev_limit, _ = get_limit_status_for_homing(g, axis, cn_is_active_high)
  if rev_limit:
    print(f"{axis_name} is on REVERSE limit. Attempting recovery...")
    g.GCommand(f"PR{axis}={abs(RECOVERY_DISTANCE_REVERSE // 4)}"); g.GCommand(f"BG{axis}"); g.GCommand(f"AM{axis}")
    time.sleep(0.5)
    _, rev_limit, _ = get_limit_status_for_homing(g, axis, cn_is_active_high)
    if rev_limit:
      print(f"CRITICAL: Could not move {axis_name} off REVERSE limit. Homing failed.")
      return False
  print(f"Setting homing speed for {axis_name} to -{HOMING_SPEED_COUNTS_PER_SEC} (reverse)...")
  g.GCommand(f"JG{axis}=-{HOMING_SPEED_COUNTS_PER_SEC}"); g.GCommand(f"BG{axis}")
  start_time = time.time()
  while time.time() - start_time < 30:
    _, rev_limit, _ = get_limit_status_for_homing(g, axis, cn_is_active_high)
    if rev_limit:
      print(f"{axis_name} REVERSE limit switch detected!")
      g.GCommand(f"ST{axis}"); g.GCommand(f"AM{axis}"); time.sleep(0.2)
      print(f"Moving {axis_name} slightly forward off the REVERSE limit...")
      g.GCommand(f"PR{axis}={RECOVERY_DISTANCE_FORWARD}"); g.GCommand(f"BG{axis}"); g.GCommand(f"AM{axis}")
      time.sleep(0.5)
      print(f"Defining current {axis_name} position as 0 (DP{axis}=0)...")
      g.GCommand(f"DP{axis}=0"); time.sleep(0.1)
      pos = g.GCommand(f"TP{axis}").strip()
      print(f"{axis_name} homing complete. Current reported position is: {pos}")
      return True
    time.sleep(0.05)
  print(f"Homing timeout for {axis_name}. Could not find REVERSE limit.")
  g.GCommand(f"ST{axis}"); g.GCommand(f"AM{axis}")
  return False

def set_servo_angle(arduino_serial, angle):
  """Sends an angle command to the Arduino and waits for the servo to move."""
  if not arduino_serial or not arduino_serial.is_open:
    print(" [ERROR] Arduino serial port not available.")
    return
  print(f"  Setting servo to angle: {angle}")
  try:
    command = f"{angle}\n"
    arduino_serial.write(command.encode('utf-8'))
    # Wait for the servo to physically move to the new position
    time.sleep(SERVO_MOVE_DELAY_S)
    # Read any response from Arduino to clear the buffer
    while arduino_serial.in_waiting > 0:
      response = arduino_serial.readline().decode('utf-8',errors='ignore').strip()
      if response:
        print(f"  [Arduino Response]: {response}")
  except serial.SerialException as e:
    print(f" [ERROR] Failed to send command to Arduino: {e}")

def trigger_camera_capture(ssh_client, data_dir, cam_id, target_x, target_y, servo_angle):
  """
  Executes the image capture script on the Raspberry Pi via SSH.
  Includes the servo angle in the command for the filename.
  """
  gantry_x_int = int(round(target_x))
  gantry_y_int = int(round(target_y))

  print(f"  Triggering camera for target (X={gantry_x_int}, Y={gantry_y_int}) at Servo Angle={servo_angle}...")

  # NOTE: The 'watertank_capture.py' script on the Pi must be modified
  # to accept a new '-s' argument for the servo angle and include it in the filename.
  capture_cmd = (
    f'python3 /home/pi/watertank/watertank_capture.py '
    f'-x {gantry_x_int} -y {gantry_y_int} -z {GANTRY_Z_POS} -s {servo_angle} '
    f'-d {data_dir} -a "{TEST_NAME}" -g {CAMERA_GAIN} '
    f'-e {CAMERA_EXPOSURE} -c {cam_id}'
  )
  print(f"  Running command on Pi: {capture_cmd}")
  try:
    stdin, stdout, stderr = ssh_client.exec_command(capture_cmd)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output:
      print(f"  [Pi Output]: {output}")
    if error:
      print(f"  [Pi ERROR]: {error}")
    if exit_status == 0:
      print("  Camera capture successful.")
    else:
      print(f"  Camera capture failed with exit status {exit_status}.")
  except Exception as e:
    print(f" [ERROR] An SSH error occurred during camera capture: {e}")


def main():
  """Main function to run the full DAQ sequence."""
  g = gclib.py()
  rpi_ssh = paramiko.SSHClient()
  rpi_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  arduino_ser = None

  gantry_connected = False
  ssh_connected = False
  arduino_connected = False

  try:
    # --- 1. Connect to all hardware ---
    print("--- Connecting to Raspberry Pi ---")
    rpi_ssh.connect(RPI_HOST, username=RPI_USER, password=RPI_PASS, timeout=10)
    ssh_connected = True
    print("SSH to Raspberry Pi established.\n")

    print("--- Connecting to Arduino ---")
    arduino_ser = serial.Serial(ARDUINO_SERIAL_PORT, ARDUINO_BAUD_RATE, timeout=1)
    print(f"Waiting for Arduino on {ARDUINO_SERIAL_PORT} to initialize...")
    time.sleep(2) # Wait for Arduino reset
    arduino_connected = True
    print("Arduino connection established.\n")

    print("--- Connecting to Gantry Controller ---")
    g.GOpen(f"{GANTRY_SERIAL_PORT} --baud {GANTRY_BAUD_RATE}")
    gantry_connected = True
    print(f"Gantry connection established: {g.GInfo()}\n")

    # --- 2. Setup Camera and Data Directory on Pi ---
    print("--- Setting up camera and data directory on Pi ---")
    stdin, stdout, _ = rpi_ssh.exec_command('sudo /home/pi/watertank/check_id')
     stdout.channel.recv_exit_status()
    cam_id = stdout.read().decode('utf-8').strip()
    if not cam_id: raise Exception("Could not retrieve Camera ID from Pi.")
    print(f"Camera ID: {cam_id}")
    data_dir = f'/home/pi/watertank/data/{TEST_NAME}_CAM_{cam_id}/'
    rpi_ssh.exec_command(f'mkdir -p {data_dir}')
    print(f"Data directory on Pi: {data_dir}\n")

    # --- 3. Initialize and Home Gantry(move it to origin) ---
    print("--- Initializing and Homing Gantry ---")
    g.GCommand(f"SH{X_AXIS}{Y_AXIS}")
    cn_val = 1 if CN_SETTING_IS_ACTIVE_HIGH else -1
    g.GCommand(f"CN{X_AXIS}={cn_val}; CN{Y_AXIS}={cn_val}")
    if not home_axis_to_reverse_limit(g, X_AXIS, "X-axis", CN_SETTING_IS_ACTIVE_HIGH):
      raise Exception("X-axis homing failed.")
    if not home_axis_to_reverse_limit(g, Y_AXIS, "Y-axis", CN_SETTING_IS_ACTIVE_HIGH):
      raise Exception("Y-axis homing failed.")
    print("\n--- Homing complete. Gantry at (0, 0). ---\n")

    # --- 4. Set Motion Profile and Start DAQ Loop ---
    print("--- Starting Full Data Acquisition Sequence ---")
    g.GCommand(f"SP {SPEED_XY_COUNTS_PER_SEC},{SPEED_XY_COUNTS_PER_SEC}")
    g.GCommand(f"AC {ACCEL_XY_COUNTS_PER_SEC_SQ},{ACCEL_XY_COUNTS_PER_SEC_SQ}")
    g.GCommand(f"DC {DECEL_XY_COUNTS_PER_SEC_SQ},{DECEL_XY_COUNTS_PER_SEC_SQ}")

    total_points = len(X_POSITIONS) * len(Y_POSITIONS)
    point_count = 0

    for x_pos in X_POSITIONS:
      print(f"\nMoving to X-position: {int(round(x_pos))}")
      g.GCommand(f"PA{X_AXIS}={x_pos}"); g.GCommand(f"BG{X_AXIS}"); g.GCommand(f"AM{X_AXIS}")

      for y_pos in Y_POSITIONS:
        point_count += 1
        print(f"\n--- Processing Gantry Point {point_count}/{total_points} at (X={int(round(x_pos))}, Y={int(round(y_pos))}) ---")
        print(f" Moving to Y-position: {int(round(y_pos))}")
        g.GCommand(f"PA{Y_AXIS}={y_pos}"); g.GCommand(f"BG{Y_AXIS}"); g.GCommand(f"AM{Y_AXIS}")
        print(" Gantry in position. Starting servo and camera sequence.")
        time.sleep(POST_MOVE_INTERVAL_S)

        # Inner loop for servo angles
        for angle in SERVO_ANGLES:
          # 1. Move the servo
          set_servo_angle(arduino_ser, angle)

          # 2. Trigger the camera
          trigger_camera_capture(rpi_ssh, data_dir, cam_id, x_pos, y_pos, angle)

          time.sleep(POST_MOVE_INTERVAL_S)

    print("\n--- All movements and captures completed. ---")

  except Exception as e:
    print(f"\nAN ERROR OCCURRED: {e}", file=sys.stderr)
    if gantry_connected:
      try:
        print(f"Controller error details (TC1): {g.GCommand('TC1').strip()}", file=sys.stderr)
      except gclib.GclibError:
        pass # Ignore errors during error handling
  finally:
    # --- 5. Close All Connections ---
    print("\n--- Cleaning up and closing connections ---")
    if arduino_connected and arduino_ser:
      try:
        print("Setting servo to 90 degrees (rest position)...")
        set_servo_angle(arduino_ser, 90)
        arduino_ser.close()
        print("Arduino serial port closed.")
      except Exception as e:
        print(f"Error during Arduino cleanup: {e}")
    if gantry_connected:
      try:
        print("Returning gantry to home position (0,0)...")
        g.GCommand("PA 0,0"); g.GCommand(f"BG{X_AXIS}{Y_AXIS}"); g.GCommand(f"AM{X_AXIS}{Y_AXIS}")
        print("Disabling gantry motors...")
        g.GCommand(f"MO{X_AXIS}{Y_AXIS}")
        g.GClose()
        print("Gantry connection closed.")
      except Exception as e:
        print(f"Error during gantry cleanup: {e}")
    if ssh_connected:
      rpi_ssh.close()
      print("SSH connection to Raspberry Pi closed.")
    print("Script finished.")

if __name__ == "__main__":
  main()
