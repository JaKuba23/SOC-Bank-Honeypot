# Typowe importy, które mogą powodować problemy:
from api.fetcher import fetch_exchange_rate  # Czy plik api/fetcher.py istnieje?
from api.utils import convert_eur_to_pln     # Czy plik api/utils.py istnieje?
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector
# Symulacja bazy danych użytkowników
USERS = [
    {
        "id": 1,
        "username": "admin",
        "fullname": "Admin User",
        "password_hash": "admin", # W rzeczywistości użyj hashowania!
        "account": "ACC00000001",
        "balance": 10000000.00,  # Bardzo wysokie saldo dla admina do manualnych operacji
        "history": [],
        "role": "admin"
    },
    {
        "id": 2,
        "username": "William",
        "fullname": "William Smith",
        "password_hash": "tajnehaslo",
        "account": "ACC00000002",
        "balance": 7500.00,
        "history": [],
        "role": "user"
    },
    {
        "id": 3,
        "username": "Emma",
        "fullname": "Emma Johnson",
        "password_hash": "qwerty",
        "account": "ACC00000003",
        "balance": 3200.00,
        "history": [],
        "role": "user"
    },
    {
        "id": 4,
        "username": "Olivia",
        "fullname": "Olivia Brown",
        "password_hash": "olivia123",
        "account": "ACC00000004",
        "balance": 15000.00,
        "history": [],
        "role": "user"
    },
    {
        "id": 5,
        "username": "James",
        "fullname": "James Davis",
        "password_hash": "jamespass",
        "account": "ACC00000005",
        "balance": 800.50,
        "history": [],
        "role": "user"
    },
    {
        "id": 6,
        "username": "Sophia",
        "fullname": "Sophia Wilson",
        "password_hash": "sophiaSecure",
        "account": "ACC00000006",
        "balance": 2100.75,
        "history": [],
        "role": "user"
    }
]

def get_user_by_username(username):
    for u in USERS:
        if u["username"] == username:
            return u
    return None

def get_user_by_account(account):
    for u in USERS:
        if u["account"] == account:
            return u
    return None

def verify_password(stored_password_hash, provided_password):
    # W rzeczywistej aplikacji użyj bezpiecznych metod porównywania hashy
    return stored_password_hash == provided_password

def update_user_transaction(user_id, amount_change, transaction_details):
    user = next((u for u in USERS if u['id'] == user_id), None)
    if user:
        user['balance'] = round(user['balance'] + amount_change, 2) # Zaokrąglenie do 2 miejsc po przecinku
        user.setdefault('history', []).insert(0, transaction_details) # Dodaj na początek listy (najnowsze pierwsze)
        # Ograniczenie historii do np. ostatnich 50 transakcji
        user['history'] = user['history'][:50]
        return True
    return False