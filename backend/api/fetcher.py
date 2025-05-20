import requests
from flask import Blueprint, jsonify
from .auth import require_api_token

fetcher_bp = Blueprint('fetcher', __name__)

def fetch_exchange_rate():
    url = "https://api.nbp.pl/api/exchangerates/rates/A/EUR/?format=json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return float(data['rates'][0]['mid'])

@fetcher_bp.route('/api/exchange-rate', methods=['GET'])
@require_api_token
def get_exchange_rate():
    try:
        rate = fetch_exchange_rate()
        return jsonify({"eur_pln": rate})
    except Exception as e:
        return jsonify({"error": str(e)}), 500