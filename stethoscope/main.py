import threading
from stethoscope.bpftrace import *
from stethoscope.supercollider import *
import sys

def monitor_cpu_usage(host):
    stdout, stderr = run_bpftrace_script(host, cpu_bpftrace_script)
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

def monitor_logins(host):
    stdout, stderr = run_bpftrace_script(host, login_bpftrace_script)
    while True:
        line = stdout.readline()
        if not line:
            break
        if "User login detected" in line:
            print("A user logged in (or at least setsid was called)!")
            play_ping()
        
        # line = stderr.readline()
        # if not line:
        #     continue
        # else:
        #     print(line)
        #     break

def main():
    # get argument from user
    host = sys.argv[1]

    print("Welcome to Stethoscope! You should hear a short test tone here shortly. If you don't, please check your audio settings. Log into a server you gave as the argument to this script to hear a different sound be played.")

    login_thread = threading.Thread(target=monitor_logins,args=(host,))
    #cpu_thread = threading.Thread(target=monitor_cpu_usage,args=(host,))
    welcome_thread = threading.Thread(target=play_welcome)

    #cpu_thread.start()
    login_thread.start()
    welcome_thread.start()

    welcome_thread.join()
    #cpu_thread.join()
    login_thread.join()
    sc.quit()

if __name__ == "__main__":
    main()
