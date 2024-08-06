import threading
from stethoscope.bpftrace import *
from stethoscope.supercollider import *

def monitor_cpu_usage():
    stdout, stderr = run_bpftrace_script(ssh_host,cpu_bpftrace_script)
    while True:
        line = stdout.readline()
        print(line)
        if not line:
            break
        if "CPU Usage" in line:
            cpu_usage = int(line.split(":")[1].strip())
            frequency = map_cpu_to_frequency(cpu_usage)
            play_sound(frequency)
        
        line = stderr.readline()
        if not line:
            continue
        else:
            print(line)
            break

def monitor_logins():
    stdout, stderr = run_bpftrace_script(ssh_host,login_bpftrace_script)
    while True:
        line = stdout.readline()
        if not line:
            break
        if "User login detected" in line:
            print(line)
            play_ping()
        
        # line = stderr.readline()
        # if not line:
        #     continue
        # else:
        #     print(line)
        #     break

ssh_host="zestdev"
def main():
    login_thread = threading.Thread(target=monitor_logins)
    cpu_thread = threading.Thread(target=monitor_cpu_usage)
    welcome_thread = threading.Thread(target=play_welcome)

    cpu_thread.start()
    login_thread.start()
    welcome_thread.start()

    welcome_thread.join()
    cpu_thread.join()
    login_thread.join()
    server.quit()

if __name__ == "__main__":
    main()
