# Currency-Phish-Honeypot

A Python-based honeypot and security monitoring project that simulates a secure online banking environment, retrieves real-time EUR to PLN exchange rates, detects suspicious activities, and demonstrates SOC-ready logging and detection techniques.

---

## Features

- Fake online banking platform with login, user accounts, and transfer functionality.
- Real-time EUR to PLN currency conversion using NBP API.
- Validates sender, recipient, and amount for each transfer.
- All transfer attempts (including invalid or suspicious) are logged for SOC analysis.
- SOC badge and icons in UI to highlight monitoring.
- Web frontend (HTML/JS) and REST API (Flask).
- SOC dashboard for live log analysis, filtering, and test generation.
- Automated security and functionality tests.
- **One-click launch:** Start backend, frontend server, and SOC dashboard with a single script.

---

## Architecture

+--------+        +---------------------+        +---------------------+
|  User  |<-----> | Frontend (HTML/JS)  |<-----> | Flask Backend (API) |
+--------+        +---------------------+        +---------------------+
                                                        |
                                                        v
                                            +--------------------------+
                                            | NBP Exchange Rate API    |
                                            +--------------------------+
                                                        |
                                                        v
                                            +--------------------------+
                                            | Honeypot Logger (log)    |
                                            +--------------------------+
                                                        |
                                                        v
                                            +--------------------------+
                                            | SOC Dashboard            |
                                            +--------------------------+
                                                        |
                                                        v
                                            +--------------------------+
                                            | SIEM/SOC Tools           |
                                            +--------------------------+

---

## Security & SOC Integration

- **Honeypot Logging:** All suspicious or malformed input is logged for further analysis.
- **Phishing Detection:** The system tracks repeated suspicious attempts and can trigger alerts.
- **SOC Ready:** Logs are formatted for easy ingestion by SIEM/SOC platforms (Splunk, ELK, QRadar, etc.).
- **Incident Response:** The project can be used as a training tool for blue teamers to analyze logs and detect attack patterns.
- **SOC Dashboard:** Web panel for live log monitoring, filtering by IP/level/keyword, and running automated test transfers.

---

## Usage

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the entire project with one command:**

   ```bash
   python run_all.py
   ```

   This will:
   - Start the backend (API) on port 5000
   - Start the SOC dashboard on port 5001
   - Start a frontend HTTP server on port 8080
   - Automatically open the login page and SOC dashboard in your browser

3. **Log in to the fake bank:**
   - Go to [http://localhost:8080/login.html](http://localhost:8080/login.html)
   - Example users:
     - **admin / admin**
     - **William / tajnehaslo**
     - **Emma / qwerty**

4. **Open the SOC dashboard:**
   - Automatically opens at [http://127.0.0.1:5001/dashboard](http://127.0.0.1:5001/dashboard)
   - Or open `app/frontend/soc_dashboard.html` in your browser

5. **Run automated tests (optional, in a separate terminal):**

   ```bash
   pytest tests/
   ```

---

## Log Analysis

- All logs are saved in `honeypot.log` in the project root.
- Use the SOC dashboard to filter, search, and analyze logs in real time.

---

## Example Log Entry

---
2025-05-17 12:34:56,789 - WARNING - Suspicious input detected: Invalid amount from 127.0.0.1: '1; DROP TABLE users'
2025-05-17 12:35:10,123 - WARNING - Phishing attempt from 127.0.0.1: Multiple invalid attempts: <script>alert(1)</script>

```

---

## Portfolio & SOC Value

This project demonstrates:

- Threat detection and logging
- Honeypot techniques
- Integration with security monitoring tools
- Secure coding and input validation
- Real-world cyber defense scenarios

---

## Stopping the Project

- To stop all services, press `Ctrl+C` in the terminal where `run_all.py` is running.

---

**This project is designed for educational and demonstration purposes in the field of cybersecurity and SOC operations.**
