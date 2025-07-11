# Simple Capture with IceCube Upgrade Camera System

This code is designed for anyone who wishes to easily capture photos using the **IceCube Upgrade Camera System**.

---

## Getting Started

### 1. Clone and Navigate

After downloading this repository from GitHub, navigate to the `simple_capture` folder:

```bash
cd ./simple_capture
```

---

## File Structure

Inside this directory, you’ll find a `src` folder that contains all the source files needed to build and run the code.

### Key file:
#### `simple_capture.cpp`

- A simplified version of the original camera test code written by **Christoph Tönnis**.
- Only the **essential parts** for capturing images have been kept.

### What’s included:
- Exposure setting → `exp_time_setting()`
- Gain setting → `gain_setting()`
- Capture and save function → `myCAMSaveToSDFile()`

### What’s removed:
- Communication tests
- Log file creation  
> *(These were required for full system tests, but are not necessary for simple photo capture.)*

Additionally:
- The code also includes a section that checks whether the **exposure and gain registers** are being correctly read/written, but all related `cout` statements are commented out.

- `simple_capture.cpp` depends on **ArduCAM.h**, where `myCAM` is an instance of the `ArduCAM` class.

All supporting files needed to build the executable are also located in the `src` folder.  
Most of these files come directly from:
- **ArduCAM** (for the camera module and FPGA board)
- **SONY** (for the image sensor)

---

## Main Logic

The `main()` function is designed to execute the core function `myCAMSaveToSDFile(string raw_filename)`, which captures and saves the image.

For potential future use with **multiple cameras** or to handle **timeout errors**, this execution is wrapped inside a `capture_thread()` function.

> ⚠️ **Note:** Unlike previous test codes, `myCAMSaveToSDFile()` now only takes the `"image file name"` as its input argument.

---

## Build Instructions

After cloning the repository and navigating to the `simple_capture` directory, simply run:

```bash
make
```

This will generate the `simple_capture` executable inside the same directory.

---

## How to Use

This repository is intended to be integrated with **Python scripts** using `subprocess` to execute the `simple_capture` binary.

For example, in your Python code:

```python
subprocess.run(["./simple_capturing", raw_name, str(G), str(E)])
```

- `G`: Gain value (in dB)
- `E`: Exposure time (in ms)
- `raw_name`: Full path and filename for the image

This will set the gain and exposure, capture an image, and save it under `raw_name`.

---

## Example Python Script

### Example 1: `single_capture.py`

This simple Python script demonstrates how to interact with the capture program.

### Run the script:

```bash
sudo python3 single_capture.py
```

### Workflow:

1. After launching, you will be asked to input the **full path and filename** (e.g., `/home/pi/simple_capture/image/testdir/test.RAW`) where the image will be saved.  
   > ⚠️ **Important:** The directory you specify must already exist before running the script.

2. Next, you will be prompted to input:
   - **Gain** (enter a value between `0.0` and `72.0`)
   - **Exposure** (enter a value between `33` and `3700` ms)

3. These values will be passed to the capture program using `subprocess.run()`.

4. Once the image is successfully captured and saved, you will see:  
   ```  
   {raw_name} is properly stored  
   ```

---

You’re now ready to start capturing images with the IceCube Upgrade Camera System!

---


