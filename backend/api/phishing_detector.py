from collections import defaultdict
import time

class PhishingDetector:
    def __init__(self):
        self.attempts = defaultdict(list)

    def record_attempt(self, ip):
        now = time.time()
        self.attempts[ip].append(now)
        # Clean up old attempts (older than 5 minutes)
        self.attempts[ip] = [t for t in self.attempts[ip] if now - t < 300]

    def is_suspicious(self, ip):
        return len(self.attempts[ip]) >= 3