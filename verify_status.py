import subprocess
import sys

try:
    res = subprocess.run(['git', 'status'], capture_output=True, text=True)
    with open('git_status_out.txt', 'w') as f:
        f.write(res.stdout + "\n" + res.stderr)
    print("Filesystem write success")
except Exception as e:
    print(f"Error: {e}")
