import requests

def fetch_exchange_rate():
    url = "https://api.nbp.pl/api/exchangerates/rates/A/EUR/?format=json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return float(data['rates'][0]['mid'])