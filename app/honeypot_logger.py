import logging

logging.basicConfig(
    filename='honeypot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HoneypotLogger:
    @staticmethod
    def log_suspicious(message):
        logging.warning(f"Suspicious input detected: {message}")

    @staticmethod
    def log_phishing_attempt(ip, details):
        logging.warning(f"Phishing attempt from {ip}: {details}")