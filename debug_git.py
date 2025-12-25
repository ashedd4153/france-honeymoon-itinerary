import subprocess
import os

LOG_FILE = "git_debug_log.txt"

with open(LOG_FILE, "w") as f:
    def log(msg):
        print(msg)
        f.write(msg + "\n")

    def run_git(args):
        log(f"--- Running: git {' '.join(args)} ---")
        try:
            output = subprocess.check_output(["git"] + args, stderr=subprocess.STDOUT, cwd=os.getcwd())
            log(output.decode())
        except subprocess.CalledProcessError as e:
            log(f"Command failed with return code {e.returncode}")
            try:
                log(e.output.decode())
            except:
                log("Could not decode error output")
        except FileNotFoundError:
            log("git command not found")
        except Exception as e:
            log(f"An error occurred: {e}")

    log(f"CWD: {os.getcwd()}")
    run_git(["status"])
    run_git(["log", "-n", "5", "--decorate", "--oneline", "--all"])
    run_git(["remote", "-v"])
    run_git(["branch", "-vv"])
