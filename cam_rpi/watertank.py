import paramiko
import time
import numpy as np

rpi_ssh = paramiko.SSHClient()
rpi_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
rpi_ssh.connect('ICUpi10.local', username='pi', password='icepingu')

print("SSH to Raspberry Pi established.")

# Define the gantry and camera parameters for a single run
gantry_z = 0.0
camera_gain = 0.0
camera_exposure = 100
test_name = "dev-stage"

# Check Camera ID 
check_id_cmd = 'sudo /home/pi/watertank/check_id'
stdin, stdout, stderr = rpi_ssh.exec_command(check_id_cmd)
stdout.channel.recv_exit_status()
camid = stdout.read().decode('utf-8').strip()
print(f"Camera ID: {camid}\n")

# Create a directory on the Raspberry Pi to store data
data_dir = f'/home/pi/watertank/data/{test_name}_Z_{gantry_z}_CAM_{camid}_G_{camera_gain}_E_{camera_exposure}/'
mkdir_cmd = f'mkdir -p {data_dir}'
print(f"Creating directory: {data_dir}\n")
stdin, stdout, stderr = rpi_ssh.exec_command(mkdir_cmd)
stdout.channel.recv_exit_status() 

# Check if directory exists
mkdir_check_cmd = f'if [ -d "{data_dir}" ]; then echo "Directory exists"; else echo "Directory creation failed"; fi'
stdin, stdout, stderr = rpi_ssh.exec_command(mkdir_check_cmd)
result = stdout.read().decode().strip()
print(result+"\n")



times = []          #for dev-stage
init = time.time()  #for dev-stage
times.append(init)  #for dev-stage
# Loop through gantry_x and gantry_y values and send capturing commands
for gantry_x in range(0, 10, 2):
    for gantry_y in range(0, 10, 2):
        capture_cmd = (
            f'python3 /home/pi/watertank/watertank_capture.py '
            f'-x {gantry_x} -y {gantry_y} -z {gantry_z} -d {data_dir} -a "{test_name}" -g {camera_gain} -e {camera_exposure} -c {camid}'
        )
        print(f"Running: {capture_cmd}")
        stdin, stdout, stderr = rpi_ssh.exec_command(capture_cmd)

        # Wait for the command to finish
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()

        print(output)
        if error:
            print(f"[ERROR] {error}")

        time.sleep(2)
        stamp = time.time() #for dev-stage
        times.append(stamp) #for dev-stage

np.save(f'./times_{test_name}.npy', np.array(times))

# Close connection
rpi_ssh.close()
print("SSH connection closed.")

total_duration = times[-1] - times[0]                                   #for dev-stage
print(f"Total time taken for the run: {total_duration:.2f}")

  #for dev-stage
