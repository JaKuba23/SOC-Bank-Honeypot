# Currency-Phish-Honeypot

A Python-based honeypot and security monitoring project that retrieves real-time EUR to PLN exchange rates, detects suspicious activities, and demonstrates SOC-ready logging and detection techniques.

## Features

- Simulates a secure online banking transfer form (EUR to PLN).
- Validates sender, recipient and amount.
- All transfer attempts (including invalid) are logged for SOC analysis.
- SOC badge and icons in UI to highlight monitoring.
- CLI and web frontend (Flask API + HTML/JS).

## Security & SOC Integration

- **Honeypot Logging:** All suspicious or malformed input is logged for further analysis.
- **Phishing Detection:** The system tracks repeated suspicious attempts and can trigger alerts.
- **SOC Ready:** Logs are formatted for easy ingestion by SIEM/SOC platforms (Splunk, ELK, QRadar, etc.).
- **Incident Response:** The project can be used as a training tool for blue teamers to analyze logs and detect attack patterns.

## Usage

1. Start backend:
   ```
   python -m api.transfer
   ```
2. Open `app/frontend/index.html` in your browser.
3. Test transfers and review `honeypot.log` for SOC analysis.