# Simple Capture with IceCube Upgrade Camera System

This code is designed for capturing images for the **Watertank measurement in Utah**
Setup : Desktop (Linux/Mac) - Raspberry Pi - Camera
This directory `rpi scripts` should be downloaded in the Raspberry Pi, not your Local/Desktop
---

## Build Instructions

After cloning the repository and navigating to the `simple_capture` directory, simply run:

```bash
make
```



## `simple_capture.cpp`

- A simplified version of the original camera production test code written by **Christoph Tönnis**.
- Only the **essential parts** for capturing images have been kept.

### What’s included:
- Exposure setting → `exp_time_setting()`
- Gain setting → `gain_setting()`
- Capture and save function → `myCAMSaveToSDFile()`

### What’s removed:
- Communication tests
- Log file creation  
> *(These were required for full system tests, but are not necessary for simple photo capture.)*

- `simple_capture.cpp` depends on **ArduCAM.h**, where `myCAM` is an instance of the `ArduCAM` class.

All supporting files needed to build the executable are also located in the `src` folder.  
Most of these files come directly from:
- **ArduCAM** (for the camera module and FPGA board)
- **SONY** (for the image sensor)


### Main Logic

The `main()` function is designed to execute the core function `myCAMSaveToSDFile(string raw_filename)`, which captures and saves the image.

For potential future use with **multiple cameras** or to handle **timeout errors**, this execution is wrapped inside a `capture_thread()` function.



## `watertank_capture.py`

- The `watertank_capture.py` is running the `simple_capturing` with arguments which are parsed from the main desktop (Linux/MacOS).
You can't use this as a standalone.
- for more details, go check directory `cam_rpi`
