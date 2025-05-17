<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SOC Dashboard - Honeypot</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
    <style>
        body {
            background: linear-gradient(120deg, #23243a 0%, #1a1d2b 100%);
            color: #eaf6fb;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
        }
        .container {
            max-width: 1300px;
            margin: 30px auto;
            background: rgba(30,34,54,0.98);
            border-radius: 18px;
            box-shadow: 0 0 40px #000b;
            padding: 32px 32px 24px 32px;
            animation: fadeIn 1.2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(40px);}
            to { opacity: 1; transform: translateY(0);}
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            letter-spacing: 2px;
            font-size: 2.3rem;
            color: #7ecfff;
            text-shadow: 0 2px 18px #0af2;
        }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        .filters input, .filters select, .filters button {
            padding: 10px 14px;
            border-radius: 7px;
            border: none;
            font-size: 15px;
            background: #232837;
            color: #eaf6fb;
            transition: box-shadow 0.2s;
        }
        .filters button {
            background: linear-gradient(90deg,#00c6fb 0%,#005bea 100%);
            color: #fff;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 2px 8px #005bea44;
        }
        .filters button:hover {
            background: linear-gradient(90deg,#005bea 0%,#00c6fb 100%);
        }
        #map {
            height: 320px;
            margin-bottom: 25px;
            border-radius: 12px;
            box-shadow: 0 0 12px #0009;
            animation: fadeIn 1.5s;
        }
        #chart {
            width: 100%;
            max-width: 700px;
            margin: 0 auto 30px auto;
            background: #232837;
            border-radius: 10px;
            box-shadow: 0 0 10px #0006;
            padding: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: #232837;
        }
        th, td {
            border: 1px solid #333a;
            padding: 8px;
            text-align: left;
        }
        th {
            background: #232837;
            color: #7ecfff;
        }
        tr.phishing { background: #ff3b3b33; }
        tr.suspicious { background: #ffe06633; }
        tr:hover { background: #2a2f43; transition: background 0.2s; }
        #testPanel {
            background: #1b2233;
            border-radius: 12px;
            margin: 30px 0 18px 0;
            padding: 18px 20px;
            box-shadow: 0 2px 18px #00c6fb33;
            animation: fadeIn 1.6s;
        }
        #testPanel h2 {
            color: #00c6fb;
            margin-top: 0;
            margin-bottom: 12px;
        }
        #testTable {
            width: 100%;
            border-collapse: collapse;
            background: #222a38;
            margin-top: 10px;
        }
        #testTable th, #testTable td {
            border: 1px solid #2a3a4a;
            padding: 7px 10px;
            text-align: left;
        }
        #testTable th {
            background: #1b2233;
            color: #7ecfff;
        }
        #testTable tr:hover {
            background: #223355;
        }
        .fadein {
            animation: fadeIn 1s;
        }
        @media (max-width: 900px) {
            .container { padding: 8px; }
            #map { height: 180px; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>SOC Dashboard</h1>
    <div class="filters">
        <input type="text" id="filterIp" placeholder="Filter by IP">
        <input type="text" id="filterKeyword" placeholder="Keyword">
        <select id="filterLevel">
            <option value="">All Levels</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
        </select>
        <button onclick="loadLogs()">Filter</button>
        <button onclick="runTestTransfers()">Run Test Transfers</button>
    </div>
    <div id="map"></div>
    <canvas id="chart"></canvas>
    <div id="testPanel" style="display:none;">
        <h2>Test Transfers</h2>
        <table id="testTable">
            <thead>
                <tr>
                    <th>From</th>
                    <th>To</th>
                    <th>Amount [EUR]</th>
                    <th>IP</th>
                    <th>Level</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
    <table id="logTable">
        <thead>
        <tr>
            <th>Date/Time</th>
            <th>Level</th>
            <th>IP</th>
            <th>Message</th>
        </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let map, markers = [];
let chart, chartData = {};

function initMap() {
    map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}

async function geoLocateIPs(ips) {
    const uniqueIps = [...new Set(ips.filter(ip => ip && ip !== '127.0.0.1' && ip !== '::1'))];
    const locations = {};
    for (const ip of uniqueIps) {
        try {
            const res = await fetch(`http://ip-api.com/json/${ip}?fields=status,country,city,lat,lon,query`);
            const data = await res.json();
            if (data.status === "success") locations[ip] = data;
        } catch {}
    }
    return locations;
}

function updateChart(logs) {
    chartData = {};
    logs.forEach(log => {
        const hour = log.datetime.slice(0, 13) + ":00";
        chartData[hour] = (chartData[hour] || 0) + 1;
    });
    const labels = Object.keys(chartData).sort();
    const data = labels.map(l => chartData[l]);
    if (chart) chart.destroy();
    chart = new Chart(document.getElementById('chart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Incidents per hour',
                data: data,
                borderColor: '#00c6fb',
                backgroundColor: '#005bea33',
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 7
            }]
        },
        options: {
            plugins: { legend: { labels: { color: '#7ecfff' } } },
            scales: {
                x: { ticks: { color: '#7ecfff' } },
                y: { ticks: { color: '#7ecfff' }, beginAtZero: true }
            }
        }
    });
}

async function loadLogs() {
    const ip = document.getElementById('filterIp').value;
    const keyword = document.getElementById('filterKeyword').value;
    const level = document.getElementById('filterLevel').value;
    let url = `http://localhost:5000/api/logs?`;
    if(ip) url += `ip=${ip}&`;
    if(keyword) url += `keyword=${keyword}&`;
    if(level) url += `level=${level}&`;
    const res = await fetch(url);
    const logs = await res.json();

    // Tabela logów
    const tbody = document.querySelector('#logTable tbody');
    tbody.innerHTML = '';
    logs.forEach(log => {
        const tr = document.createElement('tr');
        if(log.msg.includes('phishing')) tr.className = 'phishing';
        else if(log.msg.includes('Suspicious')) tr.className = 'suspicious';
        tr.innerHTML = `<td>${log.datetime}</td>
                        <td>${log.level}</td>
                        <td>${log.ip}</td>
                        <td>${log.msg}</td>`;
        tbody.appendChild(tr);
    });

    // Mapa: zaznacz IP
    clearMarkers();
    const ipList = logs.map(l => l.ip);
    const locations = await geoLocateIPs(ipList);
    for (const ip in locations) {
        const loc = locations[ip];
        const marker = L.marker([loc.lat, loc.lon]).addTo(map)
            .bindPopup(`<b>${ip}</b><br>${loc.city || ''}, ${loc.country || ''}`);
        markers.push(marker);
    }
    markers.forEach((m, i) => setTimeout(() => m.openPopup(), 400 + i*200));
    setTimeout(() => markers.forEach(m => m.closePopup()), 3000);

    // Wykres
    updateChart(logs);
}

async function runTestTransfers() {
    const res = await fetch('http://localhost:5000/api/test-transfers', {method: 'POST'});
    const data = await res.json();
    showTestResults(data.results || []);
    loadLogs();
}

function showTestResults(results) {
    const panel = document.getElementById('testPanel');
    const tbody = document.querySelector('#testTable tbody');
    if (!results.length) {
        panel.style.display = 'none';
        return;
    }
    panel.style.display = 'block';
    tbody.innerHTML = '';
    results.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.from}</td><td>${row.to}</td><td>${row.amount.toFixed(2)}</td>
                        <td>${row.ip || ''}</td><td>${row.level || ''}</td><td>${row.msg || ''}</td>`;
        tbody.appendChild(tr);
    });
    panel.classList.add('fadein');
    setTimeout(() => panel.classList.remove('fadein'), 1200);
}

initMap();
loadLogs();
</script>
</body>
</html>
`