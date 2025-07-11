#  Remote Camera Control via Raspberry Pi

This script sends commands from your **Linux or macOS machine → Raspberry Pi → Camera** to remotely capture and store images.

---

##  Prerequisites

### On your **local machine (Linux/macOS)**:
- Install the following Python packages:
  - `paramiko`
  - `time`
  - `numpy`

### On the **Raspberry Pi**:
- Make sure the script `watertank_capture.py` exists.
  - Path: `/Water_Tank_Measurements/rpi_capturing/`

---

## ⚙️ Parameters

The following parameters must be defined:

1. **`gantry_x` & `gantry_y`**  
   - Used in nested for-loops.
   - Type depends on gantry control, but values are passed to the RPi only for naming the files and directory.

2. **`camera_gain`**  
   - Float in the range `0.0 – 72.0`.  
   - Not changed (fixed) during a single run.
   - Passed to the RPi to configure the camera register and construct filenames.

3. **`camera_exposure`**  
   - Integer in the range `33 – 3700`. 
   - Not changed (fixed) during a single run. 
   - Also passed to the RPi for camera register and filename construction.

4. **`gantry_z`**  
   - Fixed per run (no z-motor available).  
   - Used for directory/filename generation only.

5. **`test_name`**  
   - Optional string tag to categorize data (e.g., light source type, gantry origin).  
   - Included in filenames and directory paths.

6. **`camid`**  
   - Not user-defined.  
   - Automatically read by the RPi and sent back to your local machine.  
   - Important for identifying the camera and matching calibration data.

---

## Execution Flow

1. **Establish SSH connection** to the Raspberry Pi.
2. **Set fixed parameters** for the run: `gantry_z`, `camera_gain`, `camera_exposure`, `test_name`.
3. **Read the camera ID** (`camid`) from the RPi.
4. **Create a directory** on the RPi (not on your local machine) to store captured images.
   - Directory name includes the fixed parameters.
   - Ensure enough storage space on the RPi.
5. **Loop over `gantry_x` and `gantry_y`**:
   - For each pair, send a capture command to the RPi.
   - The RPi script should:
     1. Capture the image
     2. Save the image with a meaningful filename
     3. Validate that the image was stored successfully
   - Note: The SSH connection remains open throughout the loop.
6. **Close the SSH connection** once the loop finishes.

---

## Timestamps for Development

- The script records timestamps for each loop iteration.
- A `.npy` file containing the timing info is saved **locally** (on your Linux/macOS machine).
- You can safely delete this file if not needed.

---
