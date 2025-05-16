from flask import Flask, request, jsonify
from flask_cors import CORS
from api.fetcher import fetch_exchange_rate
from api.utils import convert_eur_to_pln
from api.honeypot_logger import HoneypotLogger
from api.phishing_detector import PhishingDetector

app = Flask(__name__)
CORS(app)
detector = PhishingDetector()

@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    data = request.get_json()
    ip = request.remote_addr

    sender = data.get('sender')
    recipient = data.get('recipient')
    amount_str = data.get('amount')

    if not sender or not recipient or sender == recipient:
        HoneypotLogger.log_suspicious(f"Invalid sender/recipient from {ip}: {sender} -> {recipient}")
        return jsonify({"error": "Invalid sender or recipient."}), 400

    try:
        eur = float(amount_str)
        if eur <= 0:
            raise ValueError("Non-positive amount")
    except Exception:
        detector.record_attempt(ip)
        HoneypotLogger.log_suspicious(f"Invalid amount from {ip}: {amount_str}")
        if detector.is_suspicious(ip):
            HoneypotLogger.log_phishing_attempt(ip, f"Multiple invalid attempts: {amount_str}")
        return jsonify({"error": "Invalid amount."}), 400

    try:
        rate = fetch_exchange_rate()
        pln = convert_eur_to_pln(eur, rate)
        HoneypotLogger.log_suspicious(f"Transfer attempt from {ip}: {eur} EUR {sender} -> {recipient} ({pln} PLN)")
        return jsonify({"pln": pln, "rate_used": rate})
    except Exception as e:
        HoneypotLogger.log_suspicious(f"Exchange rate fetch error from {ip}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)