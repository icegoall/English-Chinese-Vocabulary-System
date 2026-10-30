import time
import urllib.request

time.sleep(2)

results = []
for name, port in [("V1", 5000), ("V2", 5001)]:
    url = f"http://127.0.0.1:{port}/"
    try:
        r = urllib.request.urlopen(url, timeout=5)
        results.append(f"{name} (port {port}): HTTP {r.status} - OK")
    except Exception as e:
        results.append(f"{name} (port {port}): FAILED - {e}")

for r in results:
    print(r)
