# Water Tank Measurements — final_DAQ.py
Author: Shouvik Mondal(smondal@icecube.wisc.edu)

This README explains how to set up, test, and run `final_DAQ.py` — a Python-based Data Acquisition (DAQ) script that coordinates:
- a Galil XY gantry (motion controller),
- a Raspberry Pi camera system (remote capture via SSH),
- an Arduino-controlled servo (angle adjustments).

Goal: capture images across a 2D grid on the gantry at multiple servo angles for each grid point.

---

## Quick start (if you want to jump in)

1. Mount and power gantry, Raspberry Pi, Arduino, and camera.
2. Install Python 3 and dependencies on the machine that will run `final_DAQ.py`.
   - Recommended: use a virtualenv(otherwise could crash the PC!).
3. Upload/verify `watertank_capture.py` and `check_id` on the Raspberry Pi at `/home/pi/watertank/`.
4. Upload Arduino sketch to the Arduino that controls the servo.
5. Configure the top of `final_DAQ.py` variables (serial ports, IP/hostname, TEST_NAME, X/Y grid, etc.).
6. Run each component test (SSH to Pi, serial to Arduino, connection to Galil).
7. Run `python3 final_DAQ.py` (start with small grid and few servo angles).

---

## What this script does in step-by-step

1. Connects to Raspberry Pi via SSH to run a remote capture script and create data directories.
2. Connects to an Arduino over serial to send servo angle values.
3. Connects to the Galil gantry controller via gclib to home axes and move to positions.
4. Systematically moves the gantry through X and Y position lists.
   - For each (X, Y) position:
     - cycles through configured servo angles,
     - tells the Arduino to set the servo,
     - uses the capture script on the Raspberry Pi (passing X, Y, Z, servo angle, gain, exposure).
5. On errors or at completion, it returns the gantry to home(defined origin), sets servo to a safe angle, and closes connections.

---

## Hardware overview & wiring notes(check which port is connected to which device by listing the devices in ubuntu PC)

- Galil (gantry controller)
  - Connect via RS232-to-USB cable or native USB serial: e.g., `/dev/ttyUSB0`.
  - Ensure power for motors and controller is ON before connecting.
  - Limit switches wired to controller inputs — check polarity (active-high vs active-low).

- Arduino + servo
  - Arduino receives ASCII lines containing a single angle value (e.g., `90\n`).
  - Servo power: use an external 5V supply if high-current servo (do NOT power large servos directly from Arduino 5V regulator).
  - Ground the servo supply and Arduino and Galil common ground together.

- Raspberry Pi + camera
  - Pi should be reachable over network by hostname/IP from the PC running the DAQ.
  - Camera connected to Pi via ribbon or USB depending on camera model.
  - Pi must have `watertank_capture.py` and `check_id` executable script in `/home/pi/watertank/`.

Wiring tips:
- Use short, secure serial cables for Galil.
- Use twisted pair or shielded cables for long signal runs.
- Label cables and ports to avoid confusion.

---

## Software overview & installation

Suggested host machine: Linux (Ubuntu), but Windows may work for serial devices (port names differ: COM3 etc.)

1. Install Python 3.8+ and pip.
2. Create a virtual environment (recommended if using a new PC)/already done on the lab PC:
   ```bash
   python3 -m venv venv
   source venv/bin/activate'''
Future Work: replace the camera script with the DOM capture script and update the gantry coordinate to physical distance!
If you run into a problem, don't forget to email(shouvik.mondal@utah.edu) or message me in slack(Shouvik Mondal).
