from collections import defaultdict
import time

class PhishingDetector:
    def __init__(self):
        # Stores a list of login attempt timestamps for each IP
        self.login_attempts = defaultdict(list)
        self.suspicious_ips = set() # Using set for faster lookup

        # Configuration
        self.TIME_WINDOW_SECONDS = 300  # 5 min
        self.MAX_ATTEMPTS_IN_WINDOW = 3 # max ip etc

    def failed_login_attempt(self, ip_address): # Changed method name
        """Records a failed login attempt for a given IP."""
        current_time = time.time()

        # Remove old attempts (older than TIME_WINDOW_SECONDS)
        self.login_attempts[ip_address] = [
            timestamp for timestamp in self.login_attempts[ip_address]
            if current_time - timestamp < self.TIME_WINDOW_SECONDS
        ]

        # Add current attempt
        self.login_attempts[ip_address].append(current_time)

        # Check if IP is now suspicious
        if len(self.login_attempts[ip_address]) >= self.MAX_ATTEMPTS_IN_WINDOW:
            self.suspicious_ips.add(ip_address)
            # You can add logging here that IP has been flagged
            # print(f"DEBUG: IP {ip_address} marked as suspicious.")


    def is_suspicious(self, ip_address):
        """Checks if the given IP is currently considered suspicious."""
        # Check if it still meets the criteria (in case old attempts have expired)
        current_time = time.time()
        valid_attempts_in_window = [
            timestamp for timestamp in self.login_attempts[ip_address]
            if current_time - timestamp < self.TIME_WINDOW_SECONDS
        ]
        
        if len(valid_attempts_in_window) >= self.MAX_ATTEMPTS_IN_WINDOW:
            if ip_address not in self.suspicious_ips: # Add if not present, just in case
                self.suspicious_ips.add(ip_address)
            return True
        else:
            # If the number of attempts drops below threshold, remove from suspicious
            if ip_address in self.suspicious_ips:
                self.suspicious_ips.remove(ip_address)
                # print(f"DEBUG: IP {ip_address} no longer suspicious.")
            return False

    def get_suspicious_attempts_count(self, ip_address):
        """Returns the number of current attempts in the time window for the given IP."""
        current_time = time.time()
        return len([
            timestamp for timestamp in self.login_attempts[ip_address]
            if current_time - timestamp < self.TIME_WINDOW_SECONDS
        ])