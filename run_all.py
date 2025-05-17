import subprocess
import sys
import os
import time
import webbrowser

def run_backend():
    return subprocess.Popen([sys.executable, "-m", "api.transfer"])

def run_soc_dashboard():
    return subprocess.Popen([sys.executable, os.path.join("app", "soc_dashboard.py")])

def run_frontend_server():
    frontend_dir = os.path.join("app", "frontend")
    return subprocess.Popen([sys.executable, "-m", "http.server", "8080"], cwd=frontend_dir)

if __name__ == "__main__":
    print("Starting backend (api.transfer)...")
    backend_proc = run_backend()
    time.sleep(3)
    print("Starting SOC dashboard (app/soc_dashboard.py)...")
    soc_proc = run_soc_dashboard()
    time.sleep(3)
    print("Starting frontend HTTP server (http://localhost:8080)...")
    frontend_proc = run_frontend_server()
    time.sleep(2)
    print("Opening browser windows...")
    webbrowser.open_new("http://localhost:8080/login.html")
    # Otwieraj dashboard frontendowy, nie backendowy!
    webbrowser.open_new("http://localhost:8080/soc_dashboard.html")

    print("All services started. Press Ctrl+C to stop.")
    try:
        while True:
            if backend_proc.poll() is not None or soc_proc.poll() is not None or frontend_proc.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        for proc in [backend_proc, soc_proc, frontend_proc]:
            if proc.poll() is None:
                proc.terminate()
        print("All services stopped.")
        sys.exit(0)