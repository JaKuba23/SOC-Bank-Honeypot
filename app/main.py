from fetcher import fetch_exchange_rate
from utils import convert_eur_to_pln
from honeypot_logger import HoneypotLogger
from phishing_detector import PhishingDetector

def main():
    detector = PhishingDetector()
    print("=== Currency-Phish-Honeypot CLI ===")
    try:
        rate = fetch_exchange_rate()
        print(f"Current EUR -> PLN rate: {rate:.4f}")
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return

    while True:
        user_input = input("Enter the amount in Euros (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break
        try:
            amount = float(user_input)
            if amount < 0:
                raise ValueError("Negative amount")
        except Exception:
            HoneypotLogger.log_suspicious(f"Invalid CLI input: '{user_input}'")
            print("Invalid input. Please enter a positive number.")
            continue

        pln = convert_eur_to_pln(amount, rate)
        print(f"{amount} EUR = {pln} PLN")

if __name__ == "__main__":
    main()