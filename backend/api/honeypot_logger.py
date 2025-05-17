import logging
from datetime import datetime

# Konfiguracja podstawowego loggingu, jeśli nie jest już skonfigurowany globalnie
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HoneypotLogger:
    log_file = "honeypot.log" # Można to przenieść do konfiguracji
    logs = [] # Przechowuje logi w pamięci dla API
    transfers = [] # Przechowuje logi transferów w pamięci dla API

    @staticmethod
    def _log_to_file(level, msg, ip=""):
        """Pomocnicza metoda do zapisu do pliku."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {level.upper()} - IP: {ip if ip else 'N/A'} - {msg}\n"
        try:
            with open(HoneypotLogger.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            # W przypadku problemu z zapisem do pliku, loguj do standardowego wyjścia
            print(f"ERROR writing to log file: {e}")
            print(log_entry)


    @staticmethod
    def log_transfer(ip, sender, recipient, amount):
        """Loguje udany transfer."""
        msg = f"Transfer: {amount} EUR from {sender} to {recipient}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry_details = {
            "datetime": timestamp,
            "level": "INFO", # Transfery są zwykle informacyjne
            "ip": ip,
            "sender": sender,
            "recipient": recipient,
            "amount_eur": amount,
            "msg": msg
        }
        HoneypotLogger.transfers.append(log_entry_details)
        HoneypotLogger.logs.append(log_entry_details) # Dodaj również do ogólnych logów
        
        HoneypotLogger._log_to_file("INFO", msg, ip)
        logging.info(msg) # Logowanie również przez standardowy logger Pythona

    @staticmethod
    def log_suspicious(msg, ip=""):
        """Loguje podejrzane zdarzenie (domyślnie jako WARNING)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry_details = {
            "datetime": timestamp,
            "level": "WARNING", # Podejrzane zdarzenia są ostrzeżeniami
            "ip": ip,
            "msg": msg
        }
        HoneypotLogger.logs.append(log_entry_details)
        
        HoneypotLogger._log_to_file("WARNING", msg, ip)
        logging.warning(f"SUSPICIOUS - IP: {ip} - {msg}") # Logowanie przez standardowy logger

    @staticmethod
    def log_phishing_attempt(ip, msg):
        """Loguje próbę phishingu (jako CRITICAL)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry_details = {
            "datetime": timestamp,
            "level": "CRITICAL", # Próby phishingu są krytyczne
            "ip": ip,
            "msg": msg
        }
        HoneypotLogger.logs.append(log_entry_details)

        HoneypotLogger._log_to_file("CRITICAL", msg, ip)
        logging.critical(f"PHISHING ATTEMPT - IP: {ip} - {msg}") # Logowanie przez standardowy logger

    @staticmethod
    def log_info(msg, ip=""):
        """Loguje zdarzenie informacyjne."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry_details = {
            "datetime": timestamp,
            "level": "INFO",
            "ip": ip,
            "msg": msg
        }
        HoneypotLogger.logs.append(log_entry_details)

        HoneypotLogger._log_to_file("INFO", msg, ip)
        logging.info(f"INFO - IP: {ip} - {msg}") # Logowanie przez standardowy logger


    @staticmethod
    def get_last_logs(n=100):
        """Zwraca ostatnie N logów (od najnowszych)."""
        return sorted(HoneypotLogger.logs, key=lambda x: x["datetime"], reverse=True)[:n]

    @staticmethod
    def get_last_transfers(n=20):
        """Zwraca ostatnie N transferów (od najnowszych)."""
        return sorted(HoneypotLogger.transfers, key=lambda x: x["datetime"], reverse=True)[:n]

# Przykładowe użycie (można usunąć lub zakomentować)
if __name__ == "__main__":
    # Konfiguracja loggera Pythona dla testów
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    HoneypotLogger.log_info("System started.", "127.0.0.1")
    HoneypotLogger.log_transfer("192.168.1.10", "Alice", "Bob", 100.00)
    HoneypotLogger.log_suspicious("Multiple failed login attempts.", "10.0.0.5")
    HoneypotLogger.log_phishing_attempt("203.0.113.45", "Clicked on a phishing link to /login.php")
    
    print("\nLast Logs:")
    for log in HoneypotLogger.get_last_logs(5):
        print(log)
    
    print("\nLast Transfers:")
    for tr in HoneypotLogger.get_last_transfers(5):
        print(tr)