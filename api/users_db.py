import hashlib

# Fake baza użytkowników (login, hasło, saldo, imię, nazwisko, numer konta)
USERS = [
    {
        "username": "anna",
        "password": hashlib.sha256("haslo123".encode()).hexdigest(),
        "fullname": "Anna Nowak",
        "account": "PL61109010140000071219812874",
        "balance": 10000.00
    },
    {
        "username": "jan",
        "password": hashlib.sha256("tajnehaslo".encode()).hexdigest(),
        "fullname": "Jan Kowalski",
        "account": "PL27114020040000300201355387",
        "balance": 8000.00
    },
    {
        "username": "ewa",
        "password": hashlib.sha256("qwerty".encode()).hexdigest(),
        "fullname": "Ewa Szymańska",
        "account": "PL30102010260000042270201111",
        "balance": 12000.00
    }
]

def get_user_by_username(username):
    return next((u for u in USERS if u["username"] == username), None)

def get_user_by_account(account):
    return next((u for u in USERS if u["account"] == account), None)

def verify_password(user, password):
    return user and user["password"] == hashlib.sha256(password.encode()).hexdigest()