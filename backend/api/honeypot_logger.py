import logging
from collections import deque
from datetime import datetime

class HoneypotLogger:
    log_file = "honeypot.log"
    logs = deque(maxlen=200)
    transfers = deque(maxlen=50)

    @staticmethod
    def log_transfer(ip, sender, recipient, amount):
        msg = f"Transfer: {amount} EUR {sender} -> {recipient}"
        HoneypotLogger.logs.append({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "INFO",
            "ip": ip,
            "msg": msg
        })
        HoneypotLogger.transfers.append({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": sender,
            "to": recipient,
            "amount": amount,
            "ip": ip
        })
        logging.info(msg)

    @staticmethod
    def log_suspicious(msg, ip=""):
        HoneypotLogger.logs.append({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "WARNING",
            "ip": ip,
            "msg": msg
        })
        logging.warning(msg)

    @staticmethod
    def log_phishing_attempt(ip, msg):
        HoneypotLogger.logs.append({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "CRITICAL",
            "ip": ip,
            "msg": msg
        })
        logging.critical(msg)

    @staticmethod
    def get_last_logs(n=100):
        return list(HoneypotLogger.logs)[-n:]

    @staticmethod
    def get_last_transfers(n=20):
        return list(HoneypotLogger.transfers)[-n:]