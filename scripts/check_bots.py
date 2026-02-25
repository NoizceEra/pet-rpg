import psutil
import sys

scripts_to_check = ['vulture_v3.py', 'sniper.py']
found = {script: False for script in scripts_to_check}

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline:
            cmdline_str = ' '.join(cmdline)
            for script in scripts_to_check:
                if script in cmdline_str:
                    found[script] = True
                    print(f"Found {script} at PID {proc.info['pid']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

for script, is_running in found.items():
    if not is_running:
        print(f"NOT_RUNNING: {script}")
