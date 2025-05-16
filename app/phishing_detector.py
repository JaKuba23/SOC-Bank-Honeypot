class PhishingDetector:
    def __init__(self):
        self.attempts = {}

    def record_attempt(self, ip):
        self.attempts[ip] = self.attempts.get(ip, 0) + 1

    def is_suspicious(self, ip, threshold=3):
        return self.attempts.get(ip, 0) >= threshold