import subprocess
import os
import platform
import time
import signal
import sys
import webbrowser

# --- Configuration ---
BACKEND_DIR = "backend"
FRONTEND_DIR = "frontend"

# ZMIENIONE: Uruchamiamy backend w inny sposób, dodając katalog nadrzędny do PYTHONPATH
if platform.system() == "Windows":
    BACKEND_CMD = ["cmd", "/c", "set", "PYTHONPATH=%PYTHONPATH%;.", "&&", "python", "-m", "api.transfer"]
else:
    BACKEND_CMD = ["bash", "-c", "PYTHONPATH=$PYTHONPATH:. python -m api.transfer"]

# Default frontend URL - will be opened in browser if auto_open_browser is True
FRONTEND_URL = "http://localhost:3000"
AUTO_OPEN_BROWSER = True

if platform.system() == "Windows":
    FRONTEND_CMD = ["cmd", "/c", "npm", "start"]
else:
    FRONTEND_CMD = ["npm", "start"]

backend_process = None
frontend_process = None
# --- End Configuration ---

def start_servers():
    """Start the backend and frontend servers."""
    global backend_process, frontend_process

    print("Starting Backend server...")
    try:
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
        
        # Redirect output so we can see errors
        backend_process = subprocess.Popen(
            BACKEND_CMD,
            cwd=BACKEND_DIR,
            creationflags=creation_flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Check if process started or immediately failed
        time.sleep(0.5)
        if backend_process.poll() is not None:  # Process already exited
            stdout, stderr = backend_process.communicate()
            print(f"ERROR: Backend server failed to start!")
            if stdout: print(f"Output: {stdout}")
            if stderr: print(f"Error: {stderr}")
            return False
            
        print(f"Backend server started (PID: {backend_process.pid}).")
        
        # Start a thread to read and print backend output
        def read_output(process, name):
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"[{name}]: {output.strip()}")
            
            # Read any remaining stderr
            for line in process.stderr:
                print(f"[{name} ERROR]: {line.strip()}")
                
        import threading
        threading.Thread(target=read_output, args=(backend_process, "Backend"), daemon=True).start()
        
    except FileNotFoundError:
        print(f"ERROR: Python interpreter or backend command not found. Make sure Python is in PATH and the path/command is correct: CWD='{BACKEND_DIR}', CMD='{' '.join(BACKEND_CMD)}'.")
        return False
    except Exception as e:
        print(f"ERROR starting Backend server: {e}")
        return False

    # Short pause to allow backend logs to appear before frontend starts
    time.sleep(3)  # Increased wait time

    print("\nStarting Frontend server...")
    try:
        creation_flags = 0 
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        frontend_process = subprocess.Popen(
            FRONTEND_CMD,
            cwd=FRONTEND_DIR,
            creationflags=creation_flags
        )
        print(f"Frontend server started (PID: {frontend_process.pid}).")
        print("React development server (frontend) needs a moment to compile.")
        if AUTO_OPEN_BROWSER:
            print(f"Will try to open browser at {FRONTEND_URL} in 5 seconds...")
            # Schedule browser opening after a delay
            def open_browser():
                time.sleep(5)  # Wait for React to start
                webbrowser.open(FRONTEND_URL)
            
            import threading
            threading.Thread(target=open_browser, daemon=True).start()
    except FileNotFoundError:
        print(f"ERROR: 'npm' command not found. Make sure Node.js (with npm) is installed and 'npm' is in your PATH.")
        if backend_process and backend_process.poll() is None: 
            _kill_process_tree(backend_process, "Backend")
            backend_process = None 
        return False
    except Exception as e:
        print(f"ERROR starting Frontend server: {e}")
        if backend_process and backend_process.poll() is None:
            _kill_process_tree(backend_process, "Backend")
            backend_process = None
        return False
    
    return True

def _kill_process_tree(process, name):
    """Helper function to stop process trees."""
    if not process or process.poll() is not None:
        return

    print(f"Stopping {name} server (PID: {process.pid})...")
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                check=False 
            )
        else:
            try:
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                print(f"{name} server (PID: {process.pid}) not found when trying to stop process group (may have already terminated).")
                try:
                    process.terminate() 
                except ProcessLookupError:
                    pass
        
        process.wait(timeout=10)
        print(f"{name} server stopped (wait completed).")
    except subprocess.TimeoutExpired:
        print(f"{name} server didn't terminate within 10 seconds. Attempting to force kill...")
        try:
            process.kill() 
            process.wait(timeout=5) 
            print(f"{name} server (kill) stopped.")
        except ProcessLookupError:
             print(f"{name} server (PID: {process.pid}) no longer exists during kill attempt.")
        except Exception as e_kill:
            print(f"Error while force killing {name} server: {e_kill}")
    except ProcessLookupError: 
        print(f"{name} server (PID: {process.pid}) no longer exists (ProcessLookupError).")
    except Exception as e:
        print(f"Unexpected error while stopping {name} server: {e}")


def stop_servers():
    """Stop both servers."""
    global backend_process, frontend_process
    print("\nAttempting to stop all servers...")

    if frontend_process:
        _kill_process_tree(frontend_process, "Frontend")
        frontend_process = None 
    else:
        print("Frontend server was not active or already stopped.")
    
    if backend_process:
        _kill_process_tree(backend_process, "Backend")
        backend_process = None 
    else:
        print("Backend server was not active or already stopped.")
    
    print("\nServer shutdown procedures completed.")


_original_sigint_handler = signal.getsignal(signal.SIGINT)
_original_sigterm_handler = signal.getsignal(signal.SIGTERM)

def graceful_signal_handler(signum, frame):
    signal_name = signal.Signals(signum).name
    print(f"\nReceived {signal_name} signal. Initiating server shutdown...")
    stop_servers()
    
    print(f"Servers stopped after {signal_name} signal. Exiting script.")
    
    current_handler_to_restore = None
    if signum == signal.SIGINT:
        current_handler_to_restore = _original_sigint_handler
        signal.signal(signal.SIGINT, current_handler_to_restore)
    elif signum == signal.SIGTERM and platform.system() != "Windows":
        current_handler_to_restore = _original_sigterm_handler
        signal.signal(signal.SIGTERM, current_handler_to_restore)

    # If the original handler was custom and callable, call it
    if current_handler_to_restore and callable(current_handler_to_restore) and \
       current_handler_to_restore not in (signal.SIG_DFL, signal.SIG_IGN):
        current_handler_to_restore(signum, frame)
    # If the original handler was default (SIG_DFL), re-send the signal for system's default action
    elif current_handler_to_restore == signal.SIG_DFL:
        # Make sure we're not in an infinite signal loop
        if frame.f_globals.get('_signal_recursion_guard', False):
            print("Signal recursion detected, forcing exit.")
            sys.exit(128 + signum)
        frame.f_globals['_signal_recursion_guard'] = True
        os.kill(os.getpid(), signum)
    # If signal was ignored (SIG_IGN) or handler is not callable, just exit
    else:
        sys.exit(128 + signum)


if __name__ == "__main__":
    print("=" * 57)
    print("  Currency Phish & SOC Honeypot - Control Script")
    print("=" * 57)
    print("\nThis script will start both Backend (Flask) and Frontend (React) servers.")
    print("Logs from both servers will be displayed in this window.")
    print("NOTE: Closing this window or pressing Ctrl+C will stop both servers.")
    print("-" * 57)

    # Check if required files exist
    if not os.path.exists(os.path.join(BACKEND_DIR, "api", "transfer.py")):
        print(f"ERROR: Backend file not found: {os.path.join(BACKEND_DIR, 'api', 'transfer.py')}")
        print("Please make sure your project structure is correct.")
        sys.exit(1)
        
    if not os.path.exists(os.path.join(FRONTEND_DIR, "package.json")):
        print(f"ERROR: Frontend package.json not found: {os.path.join(FRONTEND_DIR, 'package.json')}")
        print("Please make sure your project structure is correct.")
        sys.exit(1)

    signal.signal(signal.SIGINT, graceful_signal_handler)
    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, graceful_signal_handler)

    servers_started_successfully = False
    try:
        if start_servers():
            servers_started_successfully = True
            print("\n" + "-" * 69)
            print("  Backend and Frontend servers are running (or starting up).")
            print("  >>> PRESS ENTER IN THIS WINDOW TO STOP ALL SERVERS <<<  ")
            print("  Alternatively, press Ctrl+C once to initiate shutdown.")
            print("-" * 69)
            input() 
        else:
            print("\nFailed to start one or both servers. Check the messages above.")

    except KeyboardInterrupt:
        print("\nCtrl+C detected (KeyboardInterrupt in main loop).")
    finally:
        print("\n'finally' block: Starting server shutdown procedures (if active)...")
        stop_servers()

    print("\nControl script execution completed.")
    if not servers_started_successfully:
        sys.exit(1) 
    sys.exit(0)