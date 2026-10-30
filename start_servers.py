import subprocess
import sys
import os
import time

base = os.path.dirname(os.path.abspath(__file__))

v1 = subprocess.Popen(
    [sys.executable, "app.py"],
    cwd=os.path.join(base, "version1"),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

v2 = subprocess.Popen(
    [sys.executable, "run_port5001.py"],
    cwd=os.path.join(base, "version2"),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

time.sleep(3)

print(f"V1 PID: {v1.pid}")
print(f"V2 PID: {v2.pid}")

v1_alive = v1.poll() is None
v2_alive = v2.poll() is None
print(f"V1 alive: {v1_alive}")
print(f"V2 alive: {v2_alive}")

if v1_alive and v2_alive:
    print("\nBoth servers running!")
    print("V1: http://127.0.0.1:5000")
    print("V2: http://127.0.0.1:5001")
else:
    if not v1_alive:
        print("V1 FAILED to start")
    if not v2_alive:
        print("V2 FAILED to start")
