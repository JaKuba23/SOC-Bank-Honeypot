# Typowe importy, które mogą powodować problemy:
from api.fetcher import fetch_exchange_rate  # Czy plik api/fetcher.py istnieje?
from api.utils import convert_eur_to_pln     # Czy plik api/utils.py istnieje?
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from api.fetcher import fetch_exchange_rate
from api.utils import convert_eur_to_pln
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector
from api.users_db import USERS, get_user_by_username, get_user_by_account, verify_password, update_user_transaction
import random
from datetime import datetime, timedelta
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.secret_key = "your_very_secret_key_here_please_change_it_for_real_project" # ZMIEŃ TO!

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax', # 'Strict' dla większego bezpieczeństwa, jeśli nie ma problemów
    SESSION_COOKIE_SECURE=False # Na produkcji True, jeśli używasz HTTPS
)
app.permanent_session_lifetime = timedelta(hours=1) # Czas trwania sesji

CORS(app,
     supports_credentials=True,
     origins=["http://localhost:3000"] # Zezwalaj tylko na frontend
)
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
            "logged_in": True,
            "message": "Login successful",
            # Zwracamy tylko niezbędne dane, reszta przez /api/me
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
        app.logger.warning(f"Access to /api/me without session. IP: {request.remote_addr}")
        return jsonify({"logged_in": False, "message": "User not authenticated"}), 401

    user_id = session['user_id']
    user = next((u for u in USERS if u['id'] == user_id), None)
    if user:
        app.logger.debug(f"Active session for user: {user['username']}, Role: {user.get('role', 'user')}. IP: {request.remote_addr}")
        return jsonify({
            "logged_in": True,
            "id": user["id"],
            "username": user["username"],
            "fullname": user["fullname"],
            "account": user["account"],
            "balance": user["balance"],
            "history": user.get("history", []),
            "role": user.get("role", "user")
        }), 200
    else: # Sytuacja awaryjna, user_id w sesji, ale nie ma go w USERS
        app.logger.error(f"User ID {user_id} in session but not found in USERS. Clearing session. IP: {request.remote_addr}")
        session.clear()
        return jsonify({"logged_in": False, "message": "Session error, user not found"}), 401


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

@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    if 'user_id' not in session:
        HoneypotLogger.log_suspicious("Unauthorized transfer attempt (no session).", request.remote_addr)
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    if not data: return jsonify({"error": "No data provided"}), 400

    recipient_account = data.get('recipient_account')
    amount_eur_str = data.get('amount_eur')
    
    sender_id = session['user_id']
    sender = next((u for u in USERS if u['id'] == sender_id), None)
    
    if not sender: # Sytuacja awaryjna
        HoneypotLogger.log_suspicious(f"Critical: Sender with ID {sender_id} (from session) not found for transfer.", request.remote_addr)
        session.clear() # Wyczyść sesję, bo jest niespójna
        return jsonify({"error": "Sender not found, session cleared"}), 400

    app.logger.info(f"Transfer attempt: From {sender['username']} ({sender['account']}) to account {recipient_account} for {amount_eur_str} EUR. IP: {request.remote_addr}")

    if not recipient_account or not amount_eur_str:
        HoneypotLogger.log_suspicious(f"Transfer attempt with missing data by {sender['username']}.", request.remote_addr)
        return jsonify({"error": "Recipient account and amount are required"}), 400

    try:
        amount_eur = float(amount_eur_str)
        if not (0.01 <= amount_eur <= 1000000): # Walidacja kwoty
            raise ValueError("Amount must be positive and within reasonable limits.")
    except ValueError as e:
        HoneypotLogger.log_suspicious(f"Invalid transfer amount '{amount_eur_str}' by {sender['username']}. Error: {e}", request.remote_addr)
        return jsonify({"error": f"Invalid amount: {e}"}), 400

    recipient = get_user_by_account(recipient_account)
    if not recipient:
        HoneypotLogger.log_suspicious(f"Transfer attempt to non-existent account '{recipient_account}' by {sender['username']}.", request.remote_addr)
        return jsonify({"error": "Recipient account not found"}), 404

    if sender['id'] == recipient['id']: # Sprawdzenie po ID, bo konto może być takie samo w teorii (choć tu nie)
        HoneypotLogger.log_suspicious(f"Self-transfer attempt by {sender['username']}.", request.remote_addr)
        return jsonify({"error": "Cannot transfer to yourself"}), 400
    
    if sender['balance'] < amount_eur:
        HoneypotLogger.log_suspicious(f"Insufficient funds for transfer by {sender['username']}. Balance: {sender['balance']}, Amount: {amount_eur}", request.remote_addr)
        return jsonify({"error": "Insufficient funds"}), 400

    try:
        exchange_rate = fetch_exchange_rate()
        amount_pln = convert_eur_to_pln(amount_eur, exchange_rate) if exchange_rate else amount_eur # Fallback
        
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sender_tx_details = {
            "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
            "amount_eur": -amount_eur, "amount_pln": -amount_pln if amount_pln else None, "datetime": current_time_str, "ip": request.remote_addr
        }
        update_user_transaction(sender['id'], -amount_eur, sender_tx_details)

        recipient_tx_details = {
            "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
            "amount_eur": amount_eur, "amount_pln": amount_pln if amount_pln else None, "datetime": current_time_str, "ip": request.remote_addr
        }
        update_user_transaction(recipient['id'], amount_eur, recipient_tx_details)

        HoneypotLogger.log_transfer(request.remote_addr, sender['fullname'], recipient['fullname'], amount_eur)
        app.logger.info(f"Transfer successful: {amount_eur} EUR from {sender['username']} to {recipient['username']}")
        return jsonify({
            "message": "Transfer successful", "new_balance": sender['balance'],
            "recipient_name": recipient['fullname'], "amount_eur": amount_eur,
            "amount_pln": amount_pln if amount_pln else "N/A (rate unavailable)"
        }), 200
    except requests.exceptions.RequestException as e:
        HoneypotLogger.log_suspicious(f"NBP API Error during transfer by {sender['username']}: {e}", request.remote_addr)
        app.logger.error(f"NBP API Error during transfer: {e}")
        # Mimo błędu NBP, przelew w EUR może się odbyć, ale bez kwoty w PLN
        # Można by to obsłużyć inaczej, np. blokując przelew lub informując użytkownika
        # Tutaj dla uproszczenia, przelew idzie, ale amount_pln będzie None
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sender_tx_details = {
            "type": "outgoing", "recipient_name": recipient['fullname'], "recipient_account": recipient['account'],
            "amount_eur": -amount_eur, "amount_pln": None, "datetime": current_time_str, "ip": request.remote_addr
        }
        update_user_transaction(sender['id'], -amount_eur, sender_tx_details)
        recipient_tx_details = {
            "type": "incoming", "sender_name": sender['fullname'], "sender_account": sender['account'],
            "amount_eur": amount_eur, "amount_pln": None, "datetime": current_time_str, "ip": request.remote_addr
        }
        update_user_transaction(recipient['id'], amount_eur, recipient_tx_details)
        HoneypotLogger.log_transfer(request.remote_addr, sender['fullname'], recipient['fullname'], amount_eur)
        app.logger.info(f"Transfer successful (NBP API failed): {amount_eur} EUR from {sender['username']} to {recipient['username']}")
        return jsonify({
            "message": "Transfer successful (exchange rate unavailable)", "new_balance": sender['balance'],
            "recipient_name": recipient['fullname'], "amount_eur": amount_eur, "amount_pln": "N/A"
        }), 200
    except Exception as e:
        HoneypotLogger.log_suspicious(f"Generic error during transfer by {sender['username']}: {str(e)}", request.remote_addr)
        app.logger.error(f"Unexpected error during transfer: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during the transfer."}), 500

@app.route('/api/live-transfers', methods=['GET'])
def live_transfers():
    # Dostępne dla admina (frontend powinien to kontrolować)
    return jsonify(HoneypotLogger.get_last_transfers(20))

@app.route('/api/logs', methods=['GET'])
def logs():
    # Dostępne dla admina (frontend powinien to kontrolować)
    return jsonify(HoneypotLogger.get_last_logs(100))

@app.route('/api/test-transfers', methods=['POST'])
def test_transfers():
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
