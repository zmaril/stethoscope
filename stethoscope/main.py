import paramiko
import subprocess
import threading
from paramiko.config import SSHConfig
import os
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

# Define the frequency range for CPU activity
MIN_FREQUENCY = 220  # A3
MAX_FREQUENCY = 880  # A5

# SSH configuration
ssh_host = "zestdev"

# bpftrace script for monitoring CPU usage
cpu_bpftrace_script = """interval:s:1 {
    printf("CPU Usage: %d\\n", @cpu);
}

kprobe:do_idle
{
    @cpu = 0;
}

kprobe:do_fork
{
    @cpu++;
}
"""
# escape the script so it works on bash shell
cpu_bpftrace_script = cpu_bpftrace_script.replace("\n", " ")

# bpftrace script for detecting login events
login_bpftrace_script = """
tracepoint:syscalls:sys_enter_setsid
{
    printf("User login detected\\n");
}
"""
# escape the script so it works on bash shell
login_bpftrace_script = login_bpftrace_script.replace("\n", " ")

def load_ssh_config(host):
    ssh_config = SSHConfig()
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path) as f:
        ssh_config.parse(f)
    host_config = ssh_config.lookup(host)
    return host_config

def map_cpu_to_frequency(cpu_usage):
    # Map the CPU usage percentage to a frequency within the specified range
    return MIN_FREQUENCY + (MAX_FREQUENCY - MIN_FREQUENCY) * (cpu_usage / 100.0)

def run_bpftrace_script(script_content):
    # Setup SSH connection
    host_config = load_ssh_config(ssh_host)
    
    # Setup SSH connection using SSH config
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=host_config['hostname'],
        username=host_config.get('user'),
        key_filename=host_config.get('identityfile')[0] if host_config.get('identityfile') else None,
        port=int(host_config.get('port', 22))
    )

    try:
        # Run the bpftrace script on the remote server via SSH
        command = f"sudo bpftrace -e '{script_content}'"
        print(f"Running command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stderr.read().decode())
        return stdout
    except Exception as e:
        print(f"Error running bpftrace script: {e}")
    finally:
        ssh_client.close()

def play_sound(frequency):
    # Use SuperCollider to play sound at the specified frequency
    subprocess.run(['sclang', '-e', f'{{{{SinOsc.ar({frequency}, 0, 0.1).play;}}}}'])

def play_ping():
    # Use SuperCollider to play a ping sound
    subprocess.run(['sclang', '-e', '{SinOsc.ar(440, 0, 0.5).play;}.defer(0.5);'])

def monitor_cpu_usage():
    cpu_script_output = run_bpftrace_script(cpu_bpftrace_script)
    for line in cpu_script_output:
        if "CPU Usage" in line:
            cpu_usage = int(line.split(":")[1].strip())
            frequency = map_cpu_to_frequency(cpu_usage)
            play_sound(frequency)

def monitor_logins():
    login_script_output = run_bpftrace_script(login_bpftrace_script)
    print("here")
    for line in login_script_output:
        if "User login detected" in line:
            print("User login detected")
            play_ping()

def main():
    # Use threading to run both scripts simultaneously
    #cpu_thread = threading.Thread(target=monitor_cpu_usage)
    login_thread = threading.Thread(target=monitor_logins)

    #cpu_thread.start()
    login_thread.start()

    #cpu_thread.join()
    login_thread.join()

if __name__ == "__main__":
    main()
