# Currency-Phish-Honeypot

A Python-based honeypot and security monitoring project that simulates a secure online banking environment, retrieves real-time EUR to PLN exchange rates, detects suspicious activities, and demonstrates SOC-ready logging and detection techniques.

## Features

- Fake online banking platform with login, user accounts, and transfer functionality.
- Real-time EUR to PLN currency conversion using NBP API.
- Validates sender, recipient, and amount for each transfer.
- All transfer attempts (including invalid or suspicious) are logged for SOC analysis.
- SOC badge and icons in UI to highlight monitoring.
- Web frontend (HTML/JS) and REST API (Flask).
- SOC dashboard for live log analysis, filtering, and test generation.
- Automated security and functionality tests.

## Security & SOC Integration

- **Honeypot Logging:** All suspicious or malformed input is logged for further analysis.
- **Phishing Detection:** The system tracks repeated suspicious attempts and can trigger alerts.
- **SOC Ready:** Logs are formatted for easy ingestion by SIEM/SOC platforms (Splunk, ELK, QRadar, etc.).
- **Incident Response:** The project can be used as a training tool for blue teamers to analyze logs and detect attack patterns.
- **SOC Dashboard:** Web panel for live log monitoring, filtering by IP/level/keyword, and running automated test transfers.

## Usage

1. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start backend:**
   ```
   python -m api.transfer
   ```

3. **Start SOC dashboard in a new terminal:**
   ```
   python app/soc_dashboard.py
   ```

4. **Open the banking frontend:**
   - Open `app/frontend/login.html` in your browser to log in and use the fake bank.

5. **Open the SOC dashboard:**
   - Open `app/frontend/soc_dashboard.html` or go to [http://127.0.0.1:5001/dashboard](http://127.0.0.1:5001/dashboard) in your browser.

6. **Run automated tests:**
   ```
   pytest tests/
   ```

## Example Users

- **anna / haslo123**
- **jan / tajnehaslo**
- **ewa / qwerty**

## Log Analysis

- All logs are saved in `honeypot.log` in the project root.
- Use the SOC dashboard to filter, search, and analyze logs in real time.

**This project is designed for educational and demonstration purposes in the field of cybersecurity and SOC operations.**