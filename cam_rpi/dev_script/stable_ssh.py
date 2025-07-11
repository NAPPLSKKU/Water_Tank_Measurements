import paramiko
import time

rpi_ssh = paramiko.SSHClient()
rpi_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
rpi_ssh.connect('ICUpi10.local', username='pi', password='icepingu')

channel = rpi_ssh.invoke_shell()
print("SSH to Raspberry pi invoked")
time.sleep(5)

# Define the gantry and camera parameters for a single run
gantry_z = 0.0
camera_gain = 0.0
camera_exposure = 100
test_name = "dev-stage"

### Create a directory on the Raspberry Pi to store data ###
# The directory will be named after the "gantry-z", "camera_gain", "camera_exposure", and "test_name" variables
data_dir = f'/home/pi/watertank/data/z_{gantry_z}_g_{camera_gain}_e_{camera_exposure}_{test_name}/'
mkdir_cmd = f'mkdir -p {data_dir}\n'
print(f"Creating directory: {data_dir}")
channel.send(mkdir_cmd)
time.sleep(1)

# Check if the directory was successfully created
check_dir_cmd = f'if [ -d "{data_dir}" ]; then echo "Directory exists"; else echo "Directory creation failed"; fi\n'
channel.send(check_dir_cmd)
time.sleep(1)

# Read the response from the Pi
output = ""
while channel.recv_ready():
    output += channel.recv(1024).decode('utf-8')
print(output)

# Loop through gantry_x and gantry_y values and send capturing commands to the Raspberry Pi
# Adjust the range as needed for your application or replace with gantry command
for gantry_x in range(0,10,2):
    for gantry_y in range(0,10,2):
        capturing_cmd = f'python3 /home/pi/watertank/hello.py -x {gantry_x} -y {gantry_y} -d {data_dir} -a "{test_name}"\n'
        print(f"Command sent: {capturing_cmd}")
        channel.send(capturing_cmd)
        time.sleep(5)

        if channel.recv_ready():
            output = channel.recv(1024).decode('utf-8')
            print(output)


# Close the SSH channel and connection
channel.close()
print("SSH channel closed") 
rpi_ssh.close()
