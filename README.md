# IoT Intrusion Detection System (IDS)
### B.Tech Computer Science — Minor Project

A professional, fully functional **IoT IDS Dashboard** built with:
- **Backend**: Python Flask
- **Database**: SQLite (no external DB server needed)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Detection**: Rule-based intrusion detection engine

---

## Expected Output (Screenshots Description)

| Page | What You See |
|------|-------------|
| **Dashboard** | Dark cybersecurity UI with 4 KPI cards (Total Devices, Active, Alerts, System Status), recent alerts list, device health doughnut chart, live log feed, and IDS scan button |
| **Devices** | Grid of 10 IoT device cards colour-coded by status (green=safe, red=suspicious, grey=offline), click any card for a detail modal |
| **Alerts** | Table of all IDS alerts with severity badges (CRITICAL/HIGH/MEDIUM/LOW), resolve buttons, and a scan-now action |
| **Logs** | Searchable/filterable table of all system events with colour-coded log levels (INFO/WARNING/DANGER) |
| **Reports** | 5 Chart.js charts: daily alert trend, severity doughnut, device status pie, alert-type bar, log-level bar |

---

## Folder Structure

```
iot_ids/
│
├── app.py                  ← Flask backend (routes + detection engine)
├── run.py                  ← One-command launch script
├── requirements.txt
├── README.md
│
├── database/
│   ├── init_db.py          ← DB creation + seed data
│   └── iot_ids.db          ← Auto-created on first run (SQLite)
│
├── static/
│   ├── css/
│   │   └── style.css       ← Full dark cybersecurity theme
│   └── js/
│       └── main.js         ← Shared utilities (fetch, toast, clock)
│
└── templates/
    ├── base.html           ← Sidebar + topbar layout
    ├── dashboard.html      ← Dashboard page
    ├── devices.html        ← Device monitor page
    ├── alerts.html         ← Alert system page
    ├── logs.html           ← Log viewer page
    └── reports.html        ← Reports & charts page
```

---

## Installation & Setup

### Step 1 — Prerequisites
Make sure you have Python 3.8+ installed:
```bash
python --version
# Should print Python 3.8.x or higher
```

### Step 2 — Download / Extract the project
Place the `iot_ids/` folder anywhere on your computer.

### Step 3 — Create a virtual environment (recommended)
```bash
cd iot_ids
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run the project
```bash
python run.py
```

The script will:
1. Auto-initialize the SQLite database with 10 IoT devices, 8 alerts, and 15 log entries
2. Start the Flask development server on port 5000

### Step 6 — Open in browser
```
http://127.0.0.1:5000
```

---

## How to Use

### Dashboard
- View live KPI cards updated via REST API
- Watch the **Live Log Feed** update every 8 seconds (simulated live data)
- Click **▶ Run Detection Scan** to trigger the rule-based IDS engine

### Devices Page
- Browse all 10 simulated IoT devices
- Filter by status (Safe / Suspicious / Offline) or device type
- Click any device card to open a detail modal

### Alerts Page
- View all open and resolved alerts
- Filter by severity (Critical / High / Medium / Low) or status
- Click **✓ Resolve** to mark an alert as resolved
- Click **▶ Scan Now** to run a fresh detection pass

### Logs Page
- Search logs by keyword (device name, IP, event type, details)
- Filter by log level (INFO / WARNING / DANGER)
- Auto-refreshes every 10 seconds

### Reports Page
- View 5 analytics charts powered by Chart.js
- All data sourced from the SQLite database in real-time

---

## Detection Rules (IDS Engine)

The rule-based engine (`/api/detect`) checks every device against 4 rules:

| Rule | Trigger Condition | Severity |
|------|------------------|----------|
| **Unknown Device** | MAC starts with `FF:FF` or device type is `Unknown` | HIGH |
| **Brute-Force Login** | Device status is `suspicious` AND type is `Sensor` | CRITICAL |
| **Traffic Spike** | Camera device simulated packet rate > 400 pkt/s | MEDIUM |
| **Suspicious IP** | Last IP octet ≥ 200 (anomalous DHCP range) | HIGH |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard headline stats |
| GET | `/api/devices` | All devices |
| GET | `/api/devices/<id>` | Device detail |
| GET | `/api/alerts?status=open` | Alerts (filterable) |
| POST | `/api/alerts/<id>/resolve` | Resolve an alert |
| GET | `/api/logs?q=keyword&level=DANGER` | Logs (searchable) |
| GET | `/api/reports/summary` | Chart data |
| POST | `/api/detect` | Run IDS detection engine |
| POST | `/api/simulate` | Add one simulated log entry |

---

## Viva Talking Points

1. **What is an IDS?** — An Intrusion Detection System monitors network traffic and device behaviour to identify potential security threats.
2. **Why rule-based?** — Rule-based detection is deterministic, explainable, and suitable for embedded/IoT environments with known threat patterns.
3. **Why Flask?** — Lightweight, Python-native, RESTful API design, easy to extend.
4. **Why SQLite?** — Zero-configuration, file-based, perfect for small-scale IoT deployments without infrastructure overhead.
5. **Real-world extension** — In production, replace simulated data with actual packet sniffing (using Scapy or PCAP) and add ML anomaly detection (Isolation Forest, Autoencoders).

---

## Technologies Used

| Layer | Technology |
|-------|-----------|
| Web Framework | Python Flask 2.3+ |
| Database | SQLite3 (built into Python) |
| Frontend | HTML5, CSS3, Vanilla JS (ES2020) |
| Charts | Chart.js 4.4.1 (CDN) |
| Design | Custom dark cybersecurity theme |
| Detection | Rule-based engine (Python) |

---

*Built for educational purposes — B.Tech CS Minor Project*
