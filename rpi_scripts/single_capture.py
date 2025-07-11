import subprocess
import os
import time
#from src import PrintingTool as pt

while True:
    raw_name = input("Enter Raw file path (abolute) you'd like to store the image data with .RAW at the end of it: ")
    if not os.path.isfile(raw_path):
        pass
    else:
        print("Already existing. Please choose different file path")

gain = input("Set gain (e.g., 0.0 ~ 72.0): ")
exposure = input("Set exposure (e.g., 1 ~ 3800 ms): ")

time.sleep(1)
print("Capturing starts in 3")
time.sleep(1)
print("Capturing starts in 2")
time.sleep(1)
print("Capturing starts in 1")

subprocess.run(["./simple_capturing", raw_name, str(gain), str(exposure)])

if os.path.isfile(raw_name):
    print(f"{raw_name} is properly stored")
    pass
else:
    print(f"Error: {raw_name} not found!  Please try again")

