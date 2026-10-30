import subprocess
import sys
import os
import time

base = os.path.dirname(os.path.abspath(__file__))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000

v1 = subprocess.Popen(
    [sys.executable, "run_port5000.py"],
    cwd=os.path.join(base, "version1"),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
    close_fds=True
)

v2 = subprocess.Popen(
    [sys.executable, "run_port5001.py"],
    cwd=os.path.join(base, "version2"),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
    close_fds=True
)

with open(os.path.join(base, "server_pids.txt"), "w") as f:
    f.write(f"V1 PID: {v1.pid}\n")
    f.write(f"V2 PID: {v2.pid}\n")

time.sleep(4)

v1_alive = v1.poll() is None
v2_alive = v2.poll() is None

with open(os.path.join(base, "server_status.txt"), "w") as f:
    f.write(f"V1 PID {v1.pid} alive: {v1_alive}\n")
    f.write(f"V2 PID {v2.pid} alive: {v2_alive}\n")
    if v1_alive and v2_alive:
        f.write("\nBoth servers running!\n")
        f.write("V1: http://127.0.0.1:5000\n")
        f.write("V2: http://127.0.0.1:5001\n")
