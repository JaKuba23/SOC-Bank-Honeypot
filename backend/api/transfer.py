
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_cors import cross_origin
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector
from api.users_db import USERS, get_user_by_username, get_user_by_account, verify_password, update_user_transaction
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_very_secret_key_here_please_change_it_for_real_project"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)
app.permanent_session_lifetime = timedelta(hours=1)

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
detector = PhishingDetector()

# --- Endpointy API (login, logout, me, users, transfer - jak poprzednio, ale z drobnymi usprawnieniami) ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data: return jsonify({"logged_in": False, "message": "No data provided"}), 400
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"logged_in": False, "message": "Username and password are required"}), 400

    app.logger.info(f"Login attempt for user: {username} from IP: {request.remote_addr}")
    user = get_user_by_username(username)

    if user and verify_password(user["password_hash"], password):
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user.get('role', 'user') # Zapisz rolę w sesji
        HoneypotLogger.log_info(f"User '{username}' logged in successfully.", request.remote_addr)
        app.logger.info(f"User '{username}' logged in successfully. Role: {session['role']}")
        return jsonify({
        "logged_in": True,  # Backend zwraca "logged_in" zamiast "success"
        "message": "Login successful",
        "user": {"username": user["username"], "fullname": user["fullname"], "role": user.get("role", "user")}
    }), 200
    else:
        detector.failed_login_attempt(request.remote_addr, username)
        log_msg = f"Failed login attempt for user '{username}'."
        if detector.is_suspicious(request.remote_addr):
            log_msg = f"Suspicious login activity for user '{username}'. Too many failed attempts."
            HoneypotLogger.log_phishing_attempt(request.remote_addr, log_msg)
        else:
            HoneypotLogger.log_suspicious(log_msg, request.remote_addr)
        app.logger.warning(log_msg + f" IP: {request.remote_addr}")
        return jsonify({"logged_in": False, "message": "Invalid username or password"}), 401

@app.route('/api/transfer', methods=['POST'])
@cross_origin(origins=["http://localhost:3000"], supports_credentials=True)
def transfer():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    recipient_account = data.get('recipient_account')
    amount_eur = data.get('amount_eur')
    try:
        amount_eur = float(amount_eur)
    except Exception:
        return jsonify({"error": "Invalid amount"}), 400

    sender_id = session['user_id']
    sender = next((u for u in USERS if u['id'] == sender_id), None)
    recipient = get_user_by_account(recipient_account)
    if not sender or not recipient:
        return jsonify({"error": "Invalid sender or recipient"}), 400
    if sender['id'] == recipient['id']:
        return jsonify({"error": "Cannot transfer to yourself"}), 400
    if sender['balance'] < amount_eur:
        return jsonify({"error": "Insufficient funds"}), 400

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sender_tx_details = {
        "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
        "amount_eur": -amount_eur, "datetime": current_time_str, "ip": request.remote_addr
    }
    recipient_tx_details = {
        "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
        "amount_eur": amount_eur, "datetime": current_time_str, "ip": request.remote_addr
    }
    update_user_transaction(sender['id'], -amount_eur, sender_tx_details)
    update_user_transaction(recipient['id'], amount_eur, recipient_tx_details)
    HoneypotLogger.log_transfer(request.remote_addr, sender['fullname'], recipient['fullname'], amount_eur)
    return jsonify({"message": "Transfer successful", "new_balance": sender['balance']}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    username = session.get('username', 'Unknown user')
    HoneypotLogger.log_info(f"User '{username}' logged out.", request.remote_addr)
    app.logger.info(f"User '{username}' logged out. IP: {request.remote_addr}")
    session.clear()
    return jsonify({"logged_out": True, "message": "Logout successful"}), 200

@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({"logged_in": False}), 401
    user_id = session['user_id']
    user = next((u for u in USERS if u['id'] == user_id), None)
    if not user:
        session.clear()
        return jsonify({"logged_in": False}), 401
    return jsonify({
        "logged_in": True,
        "fullname": user["fullname"],
        "account": user["account"],
        "balance": user["balance"],
        "role": user.get("role", "user"),
        "history": user.get("history", [])
    })


@app.route('/api/users', methods=['GET'])
def users_list_api(): # Zmieniona nazwa funkcji
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    current_user_id = session.get('user_id')
    # Zwracamy listę użytkowników bez bieżącego użytkownika, aby nie mógł sobie przelać
    user_list_data = [
        {"id": u["id"], "fullname": u["fullname"], "account": u["account"]}
        for u in USERS if u['id'] != current_user_id
    ]
    return jsonify(user_list_data)

def _handle_valid_transfer(data, ip, now):
    sender = get_user_by_username(data.get("sender"))
    recipient = get_user_by_username(data.get("recipient"))
    amount = float(data.get("amount", 1))
    
    if not sender or not recipient or sender["balance"] < amount:
        return jsonify({"error": "Invalid users or insufficient funds"}), 400
        
    # Process valid transfer
    sender_tx = {
        "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
        "amount_eur": -amount, "datetime": now, "ip": ip
    }
    recipient_tx = {
        "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
        "amount_eur": amount, "datetime": now, "ip": ip
    }
    update_user_transaction(sender['id'], -amount, sender_tx)
    update_user_transaction(recipient['id'], amount, recipient_tx)
    HoneypotLogger.log_transfer(ip, sender['fullname'], recipient['fullname'], amount)
    return jsonify({"message": "Valid transfer simulated"}), 200

def _handle_invalid_transfer(data, ip):
    sender = get_user_by_username(data.get("sender"))
    recipient = get_user_by_username(data.get("recipient"))
    amount = float(data.get("amount", 1))
    
    if not sender or not recipient:
        HoneypotLogger.log_suspicious(f"Transfer attempt to invalid recipient: {data.get('recipient')}", ip)
        return jsonify({"message": "Invalid recipient transfer simulated"}), 200
    if sender["balance"] < amount:
        HoneypotLogger.log_suspicious(f"Transfer attempt with insufficient funds by {sender['username']}", ip)
        return jsonify({"message": "Insufficient funds transfer simulated"}), 200
    return jsonify({"error": "Invalid test"}), 400

def _handle_failed_login(data, ip):
    username = data.get("username", "unknown")
    detector.failed_login_attempt(ip, username)
    HoneypotLogger.log_suspicious(f"Failed login attempt for user '{username}'", ip)
    return jsonify({"message": "Failed login simulated"}), 200

def _handle_phishing(data, ip):
    username = data.get("username", "unknown")
    for _ in range(5):
        detector.failed_login_attempt(ip, username)
    HoneypotLogger.log_phishing_attempt(ip, f"Multiple failed logins for '{username}' (phishing simulation)")
    return jsonify({"message": "Phishing attempt simulated"}), 200

@app.route('/api/test-transfers', methods=['POST'])
@cross_origin(origins=["http://localhost:3000"], supports_credentials=True)
def test_transfers():
    data = request.get_json() or {}
    ip = request.remote_addr or "127.0.0.1"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users = [u for u in USERS if u.get("role", "user") == "user"]
    # 70% INFO, 15% WARNING, 10% FRAUD (CRITICAL), 5% phishing
    event_types = ["valid_transfer", "invalid_transfer", "fraud", "phishing"]
    weights = [0.7, 0.15, 0.1, 0.05]  # 70% info, 15% warning, 10% critical, 5% phishing

    event = random.choices(event_types, weights=weights)[0]

    if event == "valid_transfer":
        sender, recipient = random.sample(users, 2)
        amount = round(random.uniform(1, min(200, sender["balance"])), 2)
        sender_tx = {
            "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
            "amount_eur": -amount, "datetime": now, "ip": ip
        }
        recipient_tx = {
            "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
            "amount_eur": amount, "datetime": now, "ip": ip
        }
        update_user_transaction(sender['id'], -amount, sender_tx)
        update_user_transaction(recipient['id'], amount, recipient_tx)
        HoneypotLogger.log_transfer(ip, sender['fullname'], recipient['fullname'], amount)
        return jsonify({"message": "Valid transfer simulated"}), 200

    elif event == "invalid_transfer":
        sender = random.choice(users)
        recipient = {"fullname": "Nonexistent", "account": "ACC99999999"}
        amount = round(sender["balance"] + random.uniform(100, 1000), 2)
        HoneypotLogger.log_suspicious(f"Transfer attempt of {amount} EUR to invalid recipient: {recipient['account']}", ip)
        return jsonify({"message": "Invalid recipient transfer simulated"}), 200

    elif event == "phishing":
        username = random.choice([u["username"] for u in users])
        for _ in range(5):
            detector.failed_login_attempt(ip, username)
        HoneypotLogger.log_phishing_attempt(ip, f"Multiple failed logins for '{username}' (phishing simulation)")
        return jsonify({"message": "Phishing attempt simulated"}), 200

    elif event == "fraud":
        sender, recipient = random.sample(users, 2)
        amount = round(random.uniform(1000, 5000), 2)
        msg = f"FRAUD ALERT: Unusual transfer {amount} EUR from {sender['fullname']} to {recipient['fullname']} (flagged as fraud)"
        HoneypotLogger.log_phishing_attempt(ip, msg)
        return jsonify({"message": "Fraudulent transfer attempt simulated"}), 200

    return jsonify({"message": "Unknown event"}), 200
            
@app.route('/api/live-transfers', methods=['GET'])
def live_transfers():
    # Dostępne dla admina (frontend powinien to kontrolować)
    return jsonify(HoneypotLogger.get_last_transfers(20))

@app.route('/api/logs', methods=['GET'])
def logs():
    # Dostępne dla admina (frontend powinien to kontrolować)
    return jsonify(HoneypotLogger.get_last_logs(100))

@app.route('/api/simulate-transfers', methods=['POST'])
def simulate_transfers():
    results = []
    num_operations = random.randint(1, 2)
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tylko zwykli użytkownicy biorą udział w symulacji
    regular_users = [u for u in USERS if u.get('role', 'user') == 'user']
    if len(regular_users) < 2: # Potrzebujemy co najmniej dwóch zwykłych użytkowników
        return jsonify({"message": "Not enough regular users for simulation.", "results": []}), 200


    for _ in range(num_operations):
        ip = f"10.1.{random.randint(1,254)}.{random.randint(1,254)}" # Inny zakres IP dla symulatora
        action_type = random.choice(["simulated_user_transfer", "failed_login_sim", "suspicious_access_sim"])

        if action_type == "simulated_user_transfer":
            sender, recipient = random.sample(regular_users, 2) # Losowy nadawca i odbiorca (różni)
            amount = round(random.uniform(5, 150), 2)

            if sender['balance'] >= amount:
                sender_tx_details = {
                    "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
                    "amount_eur": -amount, "amount_pln": -amount, "datetime": current_time_str, "ip": ip
                }
                update_user_transaction(sender['id'], -amount, sender_tx_details)

                recipient_tx_details = {
                    "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
                    "amount_eur": amount, "amount_pln": amount, "datetime": current_time_str, "ip": ip
                }
                update_user_transaction(recipient['id'], amount, recipient_tx_details)
                
                msg = f"Simulated User Transfer: {amount} EUR from {sender['fullname']} to {recipient['fullname']}"
                HoneypotLogger.log_transfer(ip, sender['fullname'], recipient['fullname'], amount)
                results.append({"status": "simulated_user_transfer_success", "details": msg})
            else:
                msg = f"Simulated User Transfer Attempt FAILED (Insufficient Funds): {amount} EUR from {sender['fullname']} to {recipient['fullname']}. Balance: {sender['balance']}"
                HoneypotLogger.log_suspicious(msg, ip)
                results.append({"status": "simulated_user_transfer_failed_funds", "details": msg})

        elif action_type == "failed_login_sim":
            test_user = random.choice(["attacker_sim", "guest_sim", regular_users[0]['username']])
            detector.failed_login_attempt(ip, test_user)
            log_msg = f"Simulated: Failed login attempt for user '{test_user}'."
            if detector.is_suspicious(ip):
                 log_msg = f"Simulated: Suspicious login activity for user '{test_user}'. Too many failed attempts."
                 HoneypotLogger.log_phishing_attempt(ip, log_msg)
            else:
                HoneypotLogger.log_suspicious(log_msg, ip)
            results.append({"status": "sim_failed_login", "details": log_msg})
        
        elif action_type == "suspicious_access_sim":
            target_resource = random.choice(["/admin/panel.php", "/api/v1/users/all", "/backup.zip", "/.env"])
            msg = f"Simulated: Suspicious access attempt to '{target_resource}'."
            HoneypotLogger.log_suspicious(msg, ip)
            results.append({"status": "sim_suspicious_access", "details": msg})

    if results:
      app.logger.info(f"Simulated {len(results)} operations. First: {results[0]['details']}")
    return jsonify({"message": f"{len(results)} test operations simulated.", "results": results}), 200

if __name__ == '__main__':
    # Uruchomienie serwera Flask
    # W środowisku produkcyjnym użyj serwera WSGI jak Gunicorn lub Waitress
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
