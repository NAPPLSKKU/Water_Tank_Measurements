import argparse
import json
import os
import subprocess
import time

start_time = time.time() #for dev only

# Eight lines below are to check camera id locally.
# Command from main machine includes this part, so you can erase this if you want
#test_cmd = "sudo /home/pi/watertank/check_id"
#try:
#    output = subprocess.check_output(['sudo','/home/pi/watertank/check_id'],  stderr=subprocess.STDOUT)
#    camera_id = output.decode('utf-8').strip()
#    print(f"CAMID : {camera_id}")
#except subprocess.CalledProcessError as e:
#    print(f"Failed to check ID: {e.output.decode('utf-8')}")
#os.system(test_cmd)

# Variabls parsed from the main machine
# gantry position variables (-x, -y, -z) and additional flag (-d, -a) will be used to make file name or path only
# camera register variables (-g, -e) are used to setup capturing register.
parser = argparse.ArgumentParser()
parser.add_argument("-x", "--x_pos", type=str, help="this defines x-position of the gantry system")
parser.add_argument("-y", "--y_pos", type=str, help="this defines y-position of the gantry system")
parser.add_argument("-z", "--z_pos", type=str, help="this defines z-position of the gnatry system")
parser.add_argument("-d", "--data_dir", type=str, help="this defines directori path to save image")
parser.add_argument("-a", "--add", type=str, help="this is additional parameter to flag the run")
parser.add_argument("-g", "--gain", type=str, help="this is camera gain setting 0.0-72.0")
parser.add_argument("-e", "--exposure", type=str, help="this is camera exposure setting 0.0-3700")
parser.add_argument("-c", "--camid", type=str, help="this is camera ID")
args = parser.parse_args()

data = {}
data["x"] = args.x_pos
data["y"] = args.y_pos
data["d"] = args.data_dir
data["a"] = args.add
data["cam"] = args.camid # delete this line if you deleted the check_id block above

resdir = args.data_dir
if os.path.isdir(resdir): pass
else: os.mkdir(resdir)
#print(f"Pi: {resdir}")
#print(f"Pi: {os.path.isdir(resdir)}")

raw_name = resdir + f"{args.add}_CAM_{args.camid}_Z_{args.z_pos}_X_{args.x_pos}_Y_{args.y_pos}_G_{args.gain}_E_{args.exposure}.RAW"

subprocess.run(["sudo", "/home/pi/watertank/simple_capturing", raw_name, args.gain, args.exposure])

fname = resdir + f"X{args.x_pos}_Y{args.y_pos}.json"

end_time = time.time() # for dev only
dur = end_time - start_time
dur = f"{dur:.2f}"
data["duration"] = dur+" sec"

with open(fname, 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)


