USERS = [
    {"username": "admin", "fullname": "Admin", "password": "admin", "account": "11111111", "balance": 10000},
    {"username": "William", "fullname": "William Smith", "password": "tajnehaslo", "account": "22222222", "balance": 5000},
    {"username": "Emma", "fullname": "Emma Johnson", "password": "qwerty", "account": "33333333", "balance": 3000},
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

def verify_password(user, password):
    return user["password"] == password