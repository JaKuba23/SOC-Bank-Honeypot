import requests

API_URL = "http://127.0.0.1:5000/api/transfer"

def test_valid_transfer():
    data = {"sender": "Anna Nowak", "recipient": "Tomasz Kamiński", "amount": 100}
    r = requests.post(API_URL, json=data)
    assert r.status_code == 200
    assert "pln" in r.json()

def test_negative_amount():
    data = {"sender": "Anna Nowak", "recipient": "Tomasz Kamiński", "amount": -100}
    r = requests.post(API_URL, json=data)
    assert r.status_code == 400

def test_same_sender_recipient():
    data = {"sender": "Anna Nowak", "recipient": "Anna Nowak", "amount": 100}
    r = requests.post(API_URL, json=data)
    assert r.status_code == 400

def test_sql_injection():
    data = {"sender": "Anna Nowak", "recipient": "Tomasz Kamiński", "amount": "1; DROP TABLE users"}
    r = requests.post(API_URL, json=data)
    assert r.status_code == 400

def test_xss():
    data = {"sender": "Anna Nowak", "recipient": "Tomasz Kamiński", "amount": "<script>alert(1)</script>"}
    r = requests.post(API_URL, json=data)
    assert r.status_code == 400