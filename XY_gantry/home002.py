import gclib
import time

# --- Configuration ---
# Connection parameters
SERIAL_PORT = 'COM6' # From your latest output
BAUD_RATE = 19200            # Common default

# Motion parameters
SPEED_XY_COUNTS_PER_SEC = 200000  # Speed for X and Y axes in counts/sec
ACCEL_XY_COUNTS_PER_SEC_SQ = 100000 # Acceleration for X and Y in counts/sec^2
DECEL_XY_COUNTS_PER_SEC_SQ = 100000 # Deceleration for X and Y in counts/sec^2
HOMING_SPEED_COUNTS_PER_SEC = 5000 # Slower speed for homing
MOVE_INTERVAL_SECONDS = 1.0      # Interval between moves
RECOVERY_DISTANCE_FORWARD = 1000    # Positive, for moving off a REVERSE limit
RECOVERY_DISTANCE_REVERSE = -1000   # Negative, for moving off a FORWARD limit


# Axis mapping (common Galil convention)
X_AXIS = 'A'
Y_AXIS = 'B'

# Target positions - MODIFY THESE. Assumes homing to reverse limit (0).
# All positions should now be positive or relative to that home.
# 10 different X positions
X_POSITIONS = [1000, 80000, 150000, 100000, 120000, 150000] 
# 5 different Y positions (same for each X)
Y_POSITIONS = [1000,30000, 40000, 50000, 70000, 90000]      

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CRITICAL SETTING: Adjust CN_SETTING_IS_ACTIVE_HIGH based on your hardware
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# True:  Use for Normally Closed (NC) switches that OPEN upon contact,
#        causing the controller's input pin to go HIGH (active-HIGH, CN=1).
# False: Use for Normally Open (NO) switches that CLOSE upon contact,
#        causing the controller's input pin to go LOW (active-LOW, CN=-1).
#        Also use False for NC switches that are wired such that a NOT-PRESSED
#        switch results in a LOW input to the controller.
CN_SETTING_IS_ACTIVE_HIGH = False # YOU MUST VERIFY AND SET THIS!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def get_limit_status_for_homing(g, axis, cn_is_active_high):
    """
    Returns: (is_fwd_limit_active, is_rev_limit_active, raw_ts_value)
    Interprets TS bits based on cn_is_active_high for homing.
    """
    ts_val_str = g.GCommand(f"TS{axis}").strip()
    if not ts_val_str:
        print(f"Warning: No response from TS{axis} during get_limit_status")
        return False, False, 0 
    try:
        ts_val = int(ts_val_str)
    except ValueError:
        print(f"Warning: Could not parse TS{axis} response '{ts_val_str}' to int.")
        return False, False, 0

    if cn_is_active_high: # CN = 1 (Active HIGH limits)
        fwd_active = bool((ts_val >> 3) & 1)
        rev_active = bool((ts_val >> 2) & 1)
    else: # CN = -1 (Active LOW limits)
        fwd_active = not bool((ts_val >> 3) & 1)
        rev_active = not bool((ts_val >> 2) & 1)
    return fwd_active, rev_active, ts_val

def home_axis_to_reverse_limit(g, axis, axis_name, cn_is_active_high):
    """ Homes the specified axis to its REVERSE limit and defines it as 0. """
    print(f"\n--- Homing {axis_name} ({axis}) to REVERSE limit ---")
    
    fwd_limit_active, rev_limit_active, ts_val = get_limit_status_for_homing(g, axis, cn_is_active_high)
    print(f"Initial {axis_name} TS{axis}: {ts_val:08b}, Fwd Limit Active: {fwd_limit_active}, Rev Limit Active: {rev_limit_active}")

    if rev_limit_active:
        print(f"{axis_name} appears to be already on or past the REVERSE limit.")
        if fwd_limit_active:
            print(f"CRITICAL: {axis_name} FORWARD limit is ALSO active. Cannot attempt to move off REVERSE limit. Homing failed. Please check hardware/wiring.")
            return False
        
        print(f"Attempting to move slightly FORWARD to clear REVERSE switch before defining position...")
        g.GCommand(f"PR{axis}={abs(RECOVERY_DISTANCE_REVERSE // 4)}"); time.sleep(0.1) # RECOVERY_DISTANCE_REVERSE is negative
        g.GCommand(f"BG{axis}"); time.sleep(0.05)
        g.GCommand(f"AM{axis}"); time.sleep(0.1)
        
        fwd_limit_active, rev_limit_active, ts_val = get_limit_status_for_homing(g, axis, cn_is_active_high) # Re-check
        print(f"After attempting to clear, {axis_name} TS{axis}: {ts_val:08b}, Fwd Limit Active: {fwd_limit_active}, Rev Limit Active: {rev_limit_active}")
        if rev_limit_active:
            print(f"CRITICAL: Could not move {axis_name} off REVERSE limit (still active). Homing failed. Please check physical status.")
            return False

    # Set homing speed (negative for reverse direction)
    print(f"Setting homing speed for {axis_name} to -{HOMING_SPEED_COUNTS_PER_SEC} (reverse)...")
    g.GCommand(f"JG{axis}=-{HOMING_SPEED_COUNTS_PER_SEC}"); time.sleep(0.1)
    print(f"Beginning homing motion for {axis_name} (BG{axis})...")
    g.GCommand(f"BG{axis}")

    homing_timeout_seconds = 30 
    start_time = time.time()
    limit_found = False
    while time.time() - start_time < homing_timeout_seconds:
        fwd_limit, rev_limit, ts_val = get_limit_status_for_homing(g, axis, cn_is_active_high)
        if rev_limit:
            print(f"{axis_name} REVERSE limit switch detected! (TS{axis}: {ts_val:08b})")
            limit_found = True
            break
        if fwd_limit: 
            print(f"WARNING: {axis_name} FORWARD limit hit during REVERSE homing! (TS{axis}: {ts_val:08b}) Stopping.")
            g.GCommand(f"ST{axis}"); time.sleep(0.05)
            g.GCommand(f"AM{axis}")
            print(f"Homing for {axis_name} failed due to unexpected FLS.")
            return False
        time.sleep(0.05) 

    if not limit_found:
        print(f"Homing timeout for {axis_name}. Could not find REVERSE limit.")
        g.GCommand(f"ST{axis}"); time.sleep(0.05)
        g.GCommand(f"AM{axis}")
        return False

    print(f"Stopping {axis_name} motion (ST{axis})...")
    g.GCommand(f"ST{axis}"); time.sleep(0.05) 
    g.GCommand(f"AM{axis}"); time.sleep(0.1)   

    print(f"Moving {axis_name} slightly forward off the REVERSE limit...")
    g.GCommand(f"PR{axis}={RECOVERY_DISTANCE_FORWARD}"); time.sleep(0.1) # Use RECOVERY_DISTANCE_FORWARD
    g.GCommand(f"BG{axis}"); time.sleep(0.05)
    g.GCommand(f"AM{axis}"); time.sleep(0.1)

    print(f"Defining current {axis_name} position as 0 (DP{axis}=0)...")
    g.GCommand(f"DP{axis}=0"); time.sleep(0.1)
    
    current_pos_after_home = g.GCommand(f"TP{axis}").strip()
    print(f"{axis_name} homing complete. Current position defined as: {current_pos_after_home}")
    return True


def main():
    g = gclib.py() 
    connection_established = False

    try:
        print(f"Attempting to connect to controller at {SERIAL_PORT} with baud rate {BAUD_RATE}...")
        address_string = f"{SERIAL_PORT} --baud {BAUD_RATE}"
        g.GOpen(address_string)
        connection_established = True
        
        controller_info = g.GInfo()
        print(f"Successfully connected to: {controller_info}")

        print(f"Enabling motors (SH {X_AXIS}{Y_AXIS})...")
        g.GCommand(f"SH{X_AXIS}{Y_AXIS}"); time.sleep(0.2)

        cn_val = 1 if CN_SETTING_IS_ACTIVE_HIGH else -1
        print(f"Setting limit switch configuration for {X_AXIS} & {Y_AXIS} to CN={cn_val} (active {'HIGH' if CN_SETTING_IS_ACTIVE_HIGH else 'LOW'})...")
        g.GCommand(f"CN{X_AXIS}={cn_val}"); time.sleep(0.1)
        g.GCommand(f"CN{Y_AXIS}={cn_val}"); time.sleep(0.1)
        
        tc_after_cn = g.GCommand("TC1").strip()
        print(f"Controller status after setting CN (TC1): {tc_after_cn}")
        if "0" not in tc_after_cn: 
             print(f"WARNING: Controller reported an error after setting CN: {tc_after_cn}")
        time.sleep(0.1)

        print(f"Disabling software limits for axis {X_AXIS} & {Y_AXIS}...")
        g.GCommand(f"FL{X_AXIS}=2147483647"); time.sleep(0.1) 
        g.GCommand(f"BL{X_AXIS}=-2147483648"); time.sleep(0.1) 
        g.GCommand(f"FL{Y_AXIS}=2147483647"); time.sleep(0.1)
        g.GCommand(f"BL{Y_AXIS}=-2147483648"); time.sleep(0.1)

        if not home_axis_to_reverse_limit(g, X_AXIS, "X-axis", CN_SETTING_IS_ACTIVE_HIGH):
            print("CRITICAL: X-axis homing failed. Exiting.")
            return 
        time.sleep(0.5) 
        if not home_axis_to_reverse_limit(g, Y_AXIS, "Y-axis", CN_SETTING_IS_ACTIVE_HIGH):
            print("CRITICAL: Y-axis homing failed. Exiting.")
            return 
        
        current_x_after_home = g.GCommand(f"TP{X_AXIS}").strip()
        current_y_after_home = g.GCommand(f"TP{Y_AXIS}").strip()
        print(f"\nPositions after homing: X={current_x_after_home}, Y={current_y_after_home}")
        
        fwd_x, rev_x, ts_x = get_limit_status_for_homing(g, X_AXIS, CN_SETTING_IS_ACTIVE_HIGH)
        fwd_y, rev_y, ts_y = get_limit_status_for_homing(g, Y_AXIS, CN_SETTING_IS_ACTIVE_HIGH)
        print(f"X-axis status post-homing (TSA:{ts_x:08b}): FLS Active={fwd_x}, RLS Active={rev_x}")
        print(f"Y-axis status post-homing (TSB:{ts_y:08b}): FLS Active={fwd_y}, RLS Active={rev_y}")

        if fwd_x or rev_x or fwd_y or rev_y:
            print("CRITICAL WARNING: A limit switch is still reported active after homing sequence.")
            print("This may indicate a problem with the homing logic, CN setting, or physical switches.")
            # return # Optionally exit if limits are not clear after homing

        print(f"\nSetting motion profile speeds and accelerations...")
        g.GCommand(f"SP {SPEED_XY_COUNTS_PER_SEC},{SPEED_XY_COUNTS_PER_SEC}"); time.sleep(0.1)
        g.GCommand(f"AC {ACCEL_XY_COUNTS_PER_SEC_SQ},{ACCEL_XY_COUNTS_PER_SEC_SQ}"); time.sleep(0.1)
        g.GCommand(f"DC {DECEL_XY_COUNTS_PER_SEC_SQ},{DECEL_XY_COUNTS_PER_SEC_SQ}"); time.sleep(0.1)

        for i, x_target_pos in enumerate(X_POSITIONS):
            num_y_positions = len(Y_POSITIONS) 
            print(f"\n--- Moving to X-position {i+1}/{len(X_POSITIONS)}: {x_target_pos} ---")
            
            current_tp_x_val = 0
            try: current_tp_x_val = int(g.GCommand(f"TP{X_AXIS}").strip())
            except ValueError: print(f"Warning: Could not parse TP{X_AXIS} for pre-move check.")
            
            f_x, r_x, _ = get_limit_status_for_homing(g, X_AXIS, CN_SETTING_IS_ACTIVE_HIGH)
            if (x_target_pos > current_tp_x_val and f_x) or \
               (x_target_pos < current_tp_x_val and r_x):
                print(f"WARNING: X-axis limit active that might conflict with move to {x_target_pos}. Skipping X move.")
                continue 

            print(f"Commanding X-axis ({X_AXIS}) to absolute position: {x_target_pos}")
            g.GCommand(f"PA{X_AXIS}={x_target_pos}"); time.sleep(0.1)
            print(f"Beginning X-axis motion (BG{X_AXIS})...")
            g.GCommand(f"BG{X_AXIS}")
            print(f"Waiting for X-axis motion to complete (AM{X_AXIS})...")
            g.GCommand(f"AM{X_AXIS}")
            current_x = g.GCommand(f"TP{X_AXIS}").strip()
            print(f"X-axis motion complete. Current X: {current_x}")
            print(f"Waiting for {MOVE_INTERVAL_SECONDS} sec...")
            time.sleep(MOVE_INTERVAL_SECONDS)

            for j, y_target_pos in enumerate(Y_POSITIONS):
                print(f"  --- Moving to Y-position {j+1}/{num_y_positions}: {y_target_pos} (at X={current_x}) ---")
                
                current_tp_y_val = 0
                try: current_tp_y_val = int(g.GCommand(f"TP{Y_AXIS}").strip())
                except ValueError: print(f"Warning: Could not parse TP{Y_AXIS} for pre-move check.")

                f_y, r_y, _ = get_limit_status_for_homing(g, Y_AXIS, CN_SETTING_IS_ACTIVE_HIGH)
                if (y_target_pos > current_tp_y_val and f_y) or \
                   (y_target_pos < current_tp_y_val and r_y):
                    print(f"  WARNING: Y-axis limit active that might conflict with move to {y_target_pos}. Skipping Y move.")
                    continue 

                print(f"  Commanding Y-axis ({Y_AXIS}) to absolute position: {y_target_pos}")
                g.GCommand(f"PA{Y_AXIS}={y_target_pos}"); time.sleep(0.1)
                print(f"  Beginning Y-axis motion (BG{Y_AXIS})...")
                g.GCommand(f"BG{Y_AXIS}")
                print(f"  Waiting for Y-axis motion to complete (AM{Y_AXIS})...")
                g.GCommand(f"AM{Y_AXIS}")
                current_y = g.GCommand(f"TP{Y_AXIS}").strip()
                print(f"  Y-axis motion complete. Current Y: {current_y}")
                
                if not (i == len(X_POSITIONS) - 1 and j == len(Y_POSITIONS) - 1):
                    print(f"  Waiting for {MOVE_INTERVAL_SECONDS} sec...")
                    time.sleep(MOVE_INTERVAL_SECONDS)
            
            if i < len(X_POSITIONS) - 1:
                 print(f"Completed all Y moves for X-position {i+1}.")
            else:
                 print(f"Completed all Y moves for the final X-position.")

        print("\nAll movements completed.")

    except gclib.GclibError as e:
        print(f"An error occurred with gclib: {e}")
        if connection_established:
            try:
                error_code_response = g.GCommand("TC1") 
                print(f"Controller error details: {error_code_response.strip()}")
            except gclib.GclibError: 
                print("Could not retrieve TC1 error code from controller.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if connection_established:
            try:
                if g.GInfo() != "No Galil Connection": 
                    print("Closing connection...")
                    g.GClose()
            except gclib.GclibError:
                 print("Error during GInfo/GClose. Connection might have been lost.")
        print("Script finished.")

if __name__ == "__main__":
    main()
