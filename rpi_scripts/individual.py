print("""
##############################################
WELCOME TO THE ICECUBE UPGRADE CAMERA

        """)

print("Importing relavant modules...")
import subprocess
import os
import time

#Ask if you want to create png files forevery RAW files
while True:
    convert_png = input("Would you like to convert images to PNG for easy viewing? Each capture will take about 10 extra seconds. (y/n): ").strip()
    if convert_png == "y":
        print("Importing printing module...(usually take 10-20 seconds)")
        from src import PrintingTool as prt
        convert_flag = True
        break
    elif convert_png == "n":
        convert_flag = False
        break
    else:
        continue
print("Modules imported succesfully")

# Directory Selection
while True:
    subdir = input("Enter directory name to store images. Directory will be created as [/home/pi/simple-capture/images/[name_you_put]/: ")
    directory = "/home/pi/simple_capture/images/" + subdir + "/"
    if not os.path.isdir(directory):
        response = input("This directory does not exist. Would you like to create it? (y/n): ").strip().lower()
        if response == "y":
            os.mkdir(directory)
            print(f"Directory {directory} created.")
            break
        else:
            continue
    else:
        response = input("This directory already exists. Would you like to store images here? (y/n): ").strip().lower()
        if response == "y":
            print(f"Images will be saved in {directory}.")
            break
        else:
            continue

# Create Directory for .RAW images
raw_dir = directory + "RAW_files/"
os.makedirs(raw_dir, exist_ok=True)

# Create additional folders for .png images, if conversion is enabled
if convert_flag:
    bgr_dir = os.path.join(directory, "BGR")
    cor_dir = os.path.join(directory, "real_color")
    bri_dir = os.path.join(directory, "brighter")

    os.makedirs(bgr_dir, exist_ok=True)
    os.makedirs(cor_dir, exist_ok=True)
    os.makedirs(bri_dir, exist_ok=True)

# Gain & Exposure settings
gain = input("Set gain (e.g., 0.0 ~ 72.0): ")
exposure = input("Set exposure (e.g., 1 ~ 3800 ms): ")

#Image Capture loop
while True:
    name = input("Enter name (or 'finish' to exit): ")

    if name.lower() == "finish":
        print("Exiting program.")
        break

    raw_name = os.path.join(raw_dir, name+".RAW")

    time.sleep(1)
    print("Capturing starts in 3")
    time.sleep(1)
    print("Capturing starts in 2")
    time.sleep(1)
    print("Capturing starts in 1")

    subprocess.run(["./simple_capturing", raw_name, str(gain), str(exposure)])
    
    if os.path.isfile(raw_name):
        #print(f"Success: RAW image saved as {raw_name}")
        pass
    else:
        print(f"Error: {raw_name} not found!  Please try again")
        continue
    

    if convert_flag:
        print("Generating RGB image...")
        npy = prt.Raw2Npy(raw_name)
        bgr = prt.Npy2Bgr(npy)
        bgr_name = os.path.join(bgr_dir, name+".png")
        prt.save_image(bgr_name, bgr)
        if os.path.isfile(bgr_name): ("Success: bgr image created")

        print("Applying color correction...")
        cor = prt.BgrCorrection(bgr)
        cor_name = os.path.join(cor_dir, name+".png")
        prt.save_image(cor_name, cor)
        if os.path.isfile(cor_name): ("Success: Color corrected image created")

        print("Applying brightness enhancement...")
        bri = prt.BrightenHSV(cor, factor=1.5)
        #bri = prt.BrightenBgr(cor, alpha=1.2, beta=30)
        bri_name = os.path.join(bri_dir, name+".png")
        prt.save_image(bri_name, bri)
        if os.path.isfile(bri_name): ("Success: Brighter image created")
    else:
        pass

print("Program terminated.")

