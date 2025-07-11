import cv2
import os
#import matplotlib.pyplot as plt
import numpy as np
import gzip

# Typically, the dimension of the image is 1312 * 979 (Horizontal * Vertical)
H_size = 1312
V_size = 979

# The first thing you have to do is convert the .RAW file (or RAW.gz file if compressed) into a numpy array

def Raw2Npy(raw):
    if raw.endswith(".RAW"):
        np_1d = np.fromfile(raw, dtype=np.uint16, count=H_size*V_size)                  # This will return a single row of size "H_size * V_size", with 16 bit data from all pixels.
    elif raw.endswith(".gz"):
        with gzip.open(raw, 'rb') as f:                                                 # Need "gzip" to open a ".RAW.gz" file
            data = f.read()
        np_1d = np.frombuffer(data, np.uint16, count=H_size*V_size)                     
    np_1d = np_1d >> 4                                                                  # the bit-depth of the image sensor is 12, however stored in 16-bit. You need to bit shift
    np_2d = np.reshape(np_1d, (V_size, H_size), 'C')                                    # Here, you reshape that single row into a 2D array
    return np_2d


# The image sensor has color of RGGB Bayer pattern. And these scripts are to demosaic them, and create 3-channel image
# Numpy array -> BGR channel image
# Check https://docs.opencv.org/3.4/de/d25/imgproc_color_conversions.html for Bayer -> BGR 
def Npy2Bgr(npy):
    npy = npy >> 4                                                          # Yes, you need to bit shift, 
    bgr = cv2.cvtColor(npy.astype(np.uint8), cv2.COLOR_BAYER_BG2BGR)        # Because the cv2.cvtColor reauires all values in uint8
    return bgr

# However, since the Bayer (RGGB) has 2 Green, 1 Red, and 1 Blue pixels, the image will appear greenish after the convert above.
# Therefore, it is typical to suppress Green, and boost up Red and Blue colors
######## the input image should be in BGR format, not in RGB channel format ##########

def BgrCorrection(bgr):
    # Color Correction Weights
    correction_factors = np.array([1.5, 0.8, 1.5])                          # The plan is to multiply different factros for each color channels. here 1.5, 0.8, and 1.5 are selected manually. You can change as you want.
    #bgr=np.clip(bgr,0,255)                                                 # If value exceeds 255 (maximum of 8-bit), Clip it!
    #for i in range(3):
    #    bgr:,:,i] = np.clip(rgb[:,:,i] * correction_factors[i], 0, 255)
    bgr = bgr * correction_factors[None, None, :]                           
    bgr = np.clip(bgr, 0, 255)
    bgr = bgr.astype('uint8')                                                # The dtype of the multiplication above will be float32. change back to uint8.
    return bgr


# If the image is too dark (due to short exposure, low luminous condition, etc..) you can modify the brightness with the script here.
## Two different approaches are given here.

def BrightenBgr(bgr, alpha=1.2, beta=30):
    """
    alpha: contrast (bigger than 1.0)
    beta: brightness shift (0~100)
    """
    bright = cv2.convertScaleAbs(bgr, alpha=alpha, beta=beta)
    return bright

def BrightenHSV(bgr, factor=1.5):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,2] = hsv[:,:,2] * factor
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
    hsv = hsv.astype(np.uint8)
    bright = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bright


# Save image file
def save_image(fname, file):
    cv2.imwrite(fname, file)
    if os.path.isfile(fname):
        print(f"{fname} is successfully saved.")

    else:
        print(f"Failed to save {fname}")


