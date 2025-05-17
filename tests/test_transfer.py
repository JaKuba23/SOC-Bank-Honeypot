# test_transfer.py
import requests

API_URL = "http://localhost:5000/api/transfer"
LOGIN_URL = "http://localhost:5000/api/login"

def login(username, password):
    s = requests.Session()
    res = s.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200
    return s

def test_valid_transfer():
    s = login("anna", "haslo123")
    data = {"recipient_account": "PL27114020040000300201355387", "amount": 100}
    r = s.post(API_URL, json=data)
    assert r.status_code == 200
    assert "pln" in r.json()

def test_negative_amount():
    s = login("anna", "haslo123")
    data = {"recipient_account": "PL27114020040000300201355387", "amount": -100}
    r = s.post(API_URL, json=data)
    assert r.status_code == 400

def test_same_sender_recipient():
    s = login("anna", "haslo123")
    data = {"recipient_account": "PL61109010140000071219812874", "amount": 100}
    r = s.post(API_URL, json=data)
    assert r.status_code == 400

def test_sql_injection():
    s = login("anna", "haslo123")
    data = {"recipient_account": "PL27114020040000300201355387", "amount": "1; DROP TABLE users"}
    r = s.post(API_URL, json=data)
    assert r.status_code == 400

def test_xss():
    s = login("anna", "haslo123")
    data = {"recipient_account": "PL27114020040000300201355387", "amount": "<script>alert(1)</script>"}
    r = s.post(API_URL, json=data)
    assert r.status_code == 400

if __name__ == "__main__":
    test_valid_transfer()
    test_negative_amount()
    test_same_sender_recipient()
    test_sql_injection()
    test_xss()
    print("✅ Wszystkie testy zakończone pomyślnie")
