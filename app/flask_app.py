from flask import Flask, request, jsonify
from flask_cors import CORS
from fetcher import fetch_exchange_rate
from utils import convert_eur_to_pln
from honeypot_logger import HoneypotLogger
from phishing_detector import PhishingDetector

app = Flask(__name__)
CORS(app)
detector = PhishingDetector()

@app.route('/api/convert', methods=['POST'])
def api_convert():
    data = request.get_json()
    ip = request.remote_addr

    if not data or 'amount' not in data:
        HoneypotLogger.log_suspicious(f"Malformed request from {ip}: {data}")
        return jsonify({"error": "Missing 'amount' parameter"}), 400

    try:
        eur = float(data['amount'])
        if eur < 0:
            raise ValueError("Negative amount")
    except Exception as e:
        detector.record_attempt(ip)
        HoneypotLogger.log_suspicious(f"Invalid amount from {ip}: {data.get('amount')}")
        if detector.is_suspicious(ip):
            HoneypotLogger.log_phishing_attempt(ip, f"Multiple invalid attempts: {data.get('amount')}")
        return jsonify({"error": "Invalid amount"}), 400

    try:
        rate = fetch_exchange_rate()
        pln = convert_eur_to_pln(eur, rate)
        return jsonify({"pln": pln, "rate_used": rate})
    except Exception as e:
        HoneypotLogger.log_suspicious(f"Exchange rate fetch error from {ip}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)