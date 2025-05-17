import subprocess
import sys
import os

if __name__ == "__main__":
    # Get the directory of the current script
    backend = subprocess.Popen([sys.executable, "-m", "api.transfer"])
    try:
        backend.wait()
    except KeyboardInterrupt:
        backend.terminate()