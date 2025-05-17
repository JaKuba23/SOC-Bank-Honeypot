from flask import Flask, request, jsonify, session
from flask_cors import CORS
from api.fetcher import fetch_exchange_rate
from api.utils import convert_eur_to_pln
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector
from api.users_db import USERS, get_user_by_username, get_user_by_account, verify_password
import random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=False  # True tylko na HTTPS!
)
app.permanent_session_lifetime = timedelta(hours=1)
CORS(app, supports_credentials=True)

detector = PhishingDetector()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = get_user_by_username(username)
    if user and verify_password(user, password):
        session.permanent = True
        session["username"] = username
        return jsonify({"success": True, "fullname": user["fullname"], "account": user["account"], "balance": user["balance"]})
    else:
        HoneypotLogger.log_suspicious(f"Failed login attempt for user: {username}")
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop("username", None)
    return jsonify({"success": True})

@app.route('/api/me', methods=['GET'])
def me():
    username = session.get("username")
    if not username:
        return jsonify({"logged_in": False, "error": "Session expired"}), 401
    user = get_user_by_username(username)
    return jsonify({"logged_in": True, "fullname": user["fullname"], "account": user["account"], "balance": user["balance"]})

@app.route('/api/users', methods=['GET'])
def users():
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify([
        {"fullname": u["fullname"], "account": u["account"]}
        for u in USERS if u["username"] != username
    ])

@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    ip = request.remote_addr

    sender_user = get_user_by_username(username)
    recipient_account = data.get('recipient_account')
    amount_str = data.get('amount')

    recipient_user = get_user_by_account(recipient_account)
    if not recipient_user or recipient_user["username"] == username:
        HoneypotLogger.log_suspicious(f"Invalid recipient from {ip}: {recipient_account}")
        return jsonify({"error": "Invalid recipient account."}), 400

    try:
        eur = float(amount_str)
        if eur <= 0:
            raise ValueError("Non-positive amount")
        if sender_user["balance"] < eur:
            return jsonify({"error": "Insufficient funds."}), 400
    except Exception:
        detector.record_attempt(ip)
        HoneypotLogger.log_suspicious(f"Invalid amount from {ip}: {amount_str}")
        if detector.is_suspicious(ip):
            HoneypotLogger.log_phishing_attempt(ip, f"Multiple invalid attempts: {amount_str}")
        return jsonify({"error": "Invalid amount."}), 400

    try:
        rate = fetch_exchange_rate()
        pln = convert_eur_to_pln(eur, rate)
        sender_user["balance"] -= eur
        recipient_user["balance"] += eur
        return jsonify({"pln": round(pln, 2), "rate_used": rate, "new_balance": sender_user["balance"]})
    except Exception as e:
        HoneypotLogger.log_suspicious(f"Exchange rate fetch error from {ip}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def random_public_ip():
    first = random.choice([i for i in range(11, 223) if i not in (10, 127, 192, 172)])
    return f"{first}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

@app.route('/api/test-transfers', methods=['POST'])
def test_transfers():
    results = []
    for _ in range(10):
        sender = random.choice(USERS)
        recipient = random.choice([u for u in USERS if u != sender])
        amount = round(random.uniform(1, min(sender["balance"], 500)), 2)
        ip = random_public_ip()
        if random.random() < 0.3:
            msg = f"phishing attempt detected: {amount} EUR {sender['fullname']} -> {recipient['fullname']}"
            HoneypotLogger.log_phishing_attempt(ip, msg)
            level = "WARNING"
        else:
            msg = f"Test transfer: {amount} EUR {sender['fullname']} -> {recipient['fullname']}"
            HoneypotLogger.log_suspicious(f"{msg} [IP: {ip}]")
            level = "INFO"
        if sender["balance"] >= amount:
            sender["balance"] -= amount
            recipient["balance"] += amount
        results.append({
            "from": sender["fullname"],
            "to": recipient["fullname"],
            "amount": amount,
            "ip": ip,
            "level": level,
            "msg": msg
        })
    return jsonify({"success": True, "results": results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)