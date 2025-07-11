import time
import sys

def flash_terminal():
    sys.stdout.write("\033[?5h")  # blink on
    sys.stdout.flush()
    time.sleep(0.2)
    sys.stdout.write("\033[?5l")  # blink off
    sys.stdout.flush()

flash_terminal()
