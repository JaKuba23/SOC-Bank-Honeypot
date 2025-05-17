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
    # Serwer HTTP dla frontendu na porcie 8080
    frontend_dir = os.path.join("app", "frontend")
    return subprocess.Popen([sys.executable, "-m", "http.server", "8080"], cwd=frontend_dir)

if __name__ == "__main__":
    print("Starting backend (api.transfer)...")
    backend_proc = run_backend()
    time.sleep(2)
    print("Starting SOC dashboard (app/soc_dashboard.py)...")
    soc_proc = run_soc_dashboard()
    time.sleep(2)
    print("Starting frontend HTTP server (http://localhost:8080)...")
    frontend_proc = run_frontend_server()
    time.sleep(2)
    print("Opening browser windows...")
    webbrowser.open("http://localhost:8080/login.html")
    webbrowser.open("http://127.0.0.1:5001/dashboard")

    print("All services started. Press Ctrl+C to stop.")
    try:
        backend_proc.wait()
        soc_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend_proc.terminate()
        soc_proc.terminate()
        frontend_proc.terminate()