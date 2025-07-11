import paramiko
import time
import os


# Here, All basic information for each test-set are defined. 
# Once a cycle is started, several parameters below are fixed until the cycle is ended.
# Z: height of the motor system (This can be moved into the loop if we have any device that can adjust the height, however, for now (@27MAY2025) it is fixed.
# Gain & Exposure: For all different positions we will use the same values for gain and exposure
# additional flag: Just in case, when it is necessary to re-run the test with same setup (script jammed, power cut, or simply if we want to duplicate, this flag will enable to distinguish them.

while True:
    z = input("Set Z (height) of the setup: ")
    gain = input("Set gain (e.g. 0.0 - 72.0): ")
    exposure = input("Set exposure (e.g. 33 - 3700): ")
    add = input("Add additional flag to distinguish (Note: always use \"-\" rather than space): ")

    raw_dir = f"./data/Z{z}_E{exposure}_G{gain}_{add}/"

    if not os.path.isdir(raw_dir):
        os.mkdir(raw_dir)
        print(f"{raw_dir} Created")
        break
    else:
        print("{raw_dir} already existing.\nPlease choose different file path. (Tip: try use different flag)")
        

#Here, an SSH parameters to connect Local PC and Raspberry Pi are defined.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('ICUpi10.local', username='pi', password='icepingu')


channel = ssh.invoke_shell()
print("SSH invoked")
time.sleep(5)
for x in range(10):
    for y in range(10):

        print(f"x: {x}, y:{y}")
        
        pi_dir = raw_dir.replace("./", "/home/pi/watertank/")
        channel.send(f"mkdir {pi_dir}\n")

        cmd = f'python3 /home/pi/watertank/hello.py -x {x} -y {y} -z {z} -g {gain} -e {exposure} -a {add} \n'
        #print(f"Command sent: {cmd}")
        channel.send(cmd)
        time.sleep(3)

        if channel.recv_ready():
            output = channel.recv(1024).decode('utf-8')
            print(output)


ssh.close()
