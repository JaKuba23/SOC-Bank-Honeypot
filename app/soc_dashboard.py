from flask import Flask, jsonify, render_template, request, send_from_directory
import re
import os

app = Flask(__name__, template_folder='frontend')

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'honeypot.log')

def parse_log_line(line):
    pattern = r'(?P<datetime>[\d\- :,.]+) - (?P<level>\w+) - (?P<msg>.+)'
    match = re.match(pattern, line)
    if match:
        msg = match.group('msg')
        ip_match = re.search(r'from ([\d\.]+)', msg)
        ip = ip_match.group(1) if ip_match else ''
        return {
            'datetime': match.group('datetime'),
            'level': match.group('level'),
            'msg': msg,
            'ip': ip
        }
    return None

@app.route('/api/logs')
def get_logs():
    filter_ip = request.args.get('ip')
    filter_level = request.args.get('level')
    filter_keyword = request.args.get('keyword')
    logs = []
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE, encoding='utf-8') as f:
        for line in f:
            entry = parse_log_line(line)
            if not entry:
                continue
            if filter_ip and filter_ip not in entry['ip']:
                continue
            if filter_level and filter_level.lower() != entry['level'].lower():
                continue
            if filter_keyword and filter_keyword.lower() not in entry['msg'].lower():
                continue
            logs.append(entry)
    return jsonify(logs)

@app.route('/dashboard')
def dashboard():
    return send_from_directory('frontend', 'soc_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)