from paramiko.config import SSHConfig
import os
import warnings
import paramiko

warnings.filterwarnings(action='ignore', module='.*paramiko.*')

def load_ssh_config(host):
    ssh_config = SSHConfig()
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path) as f:
        ssh_config.parse(f)
    host_config = ssh_config.lookup(host)
    return host_config

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

# bpftrace script for detecting login events
login_bpftrace_script = """
tracepoint:syscalls:sys_enter_setsid
{
    printf("User login detected\\n");
}
"""

def run_bpftrace_script(ssh_host,script_content):
    # Setup SSH connection
    host_config = load_ssh_config(ssh_host)
    script_content = script_content.replace("\n", " ")
    
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
        print(command)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout,stderr
    except Exception as e:
        print(f"Error running bpftrace script: {e}")
    finally:
        pass
