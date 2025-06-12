

import subprocess
import sys

# Use default commit message unless one is provided
default_message = "Update trip itinerary and guide links"
commit_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else default_message

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ Command failed.")
        sys.exit(1)

# Step 1: Add changes
run_command("git add .")

# Step 2: Commit
run_command(f'git commit -m "{commit_message}"')

# Step 3: Push
run_command("git push origin")

print("✅ All done.")