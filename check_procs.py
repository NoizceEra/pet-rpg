import psutil
import sys

for proc in psutil.process_iter(['cmdline']):
    try:
        if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0]:
            print(' '.join(proc.info['cmdline']))
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
