"""
IoT Intrusion Detection System (IDS)
=====================================
Minor Project - B.Tech Computer Science
Flask Backend  |  SQLite Database  |  Rule-Based Detection Engine

Run:
    python app.py

Endpoints:
    /                  → Dashboard
    /devices           → Device Monitoring
    /alerts            → Alert System
    /logs              → Log Viewer
    /reports           → Reports & Charts
    /api/*             → JSON API consumed by frontend JS
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import random
from datetime import datetime, timedelta

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'iot_ids.db')


# ── DB helper ──────────────────────────────────────────────────────────────────
def get_db():
    """Open a SQLite connection with row-factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(sql, args=(), one=False):
    """Execute a SELECT and return list-of-dicts (or single dict)."""
    conn = get_db()
    cur = conn.execute(sql, args)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(sql, args=()):
    """Execute INSERT / UPDATE / DELETE and commit."""
    conn = get_db()
    cur = conn.execute(sql, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def dashboard():
    return render_template('dashboard.html', page='dashboard')


@app.route('/devices')
def devices():
    return render_template('devices.html', page='devices')


@app.route('/alerts')
def alerts():
    return render_template('alerts.html', page='alerts')


@app.route('/logs')
def logs():
    return render_template('logs.html', page='logs')


@app.route('/reports')
def reports():
    return render_template('reports.html', page='reports')


# ══════════════════════════════════════════════════════════════════════════════
#  API – DASHBOARD STATS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/stats')
def api_stats():
    """Return headline numbers for the dashboard cards."""
    total_devices     = query_db('SELECT COUNT(*) AS c FROM devices', one=True)['c']
    active_devices    = query_db("SELECT COUNT(*) AS c FROM devices WHERE status != 'offline'", one=True)['c']
    suspicious_devices = query_db("SELECT COUNT(*) AS c FROM devices WHERE status = 'suspicious'", one=True)['c']
    open_alerts       = query_db("SELECT COUNT(*) AS c FROM alerts WHERE status = 'open'", one=True)['c']
    critical_alerts   = query_db("SELECT COUNT(*) AS c FROM alerts WHERE severity = 'critical' AND status = 'open'", one=True)['c']
    total_logs        = query_db('SELECT COUNT(*) AS c FROM logs', one=True)['c']

    # System is safe only if no open high/critical alerts
    system_status = 'CRITICAL' if critical_alerts > 0 else ('WARNING' if open_alerts > 0 else 'SECURE')

    return jsonify({
        'total_devices':      total_devices,
        'active_devices':     active_devices,
        'suspicious_devices': suspicious_devices,
        'open_alerts':        open_alerts,
        'critical_alerts':    critical_alerts,
        'total_logs':         total_logs,
        'system_status':      system_status,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  API – DEVICES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/devices')
def api_devices():
    """Return all devices."""
    devices = query_db('SELECT * FROM devices ORDER BY status DESC, name ASC')
    return jsonify(devices)


@app.route('/api/devices/<int:device_id>', methods=['GET'])
def api_device_detail(device_id):
    device = query_db('SELECT * FROM devices WHERE id = ?', (device_id,), one=True)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device)


# ══════════════════════════════════════════════════════════════════════════════
#  API – ALERTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/alerts')
def api_alerts():
    """Return alerts, optionally filtered by status."""
    status = request.args.get('status', '')
    if status:
        alerts = query_db('SELECT * FROM alerts WHERE status = ? ORDER BY timestamp DESC', (status,))
    else:
        alerts = query_db('SELECT * FROM alerts ORDER BY timestamp DESC')
    return jsonify(alerts)


@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def api_resolve_alert(alert_id):
    """Mark a single alert as resolved."""
    execute_db('UPDATE alerts SET status = ? WHERE id = ?', ('resolved', alert_id))
    # Log the resolution
    execute_db(
        'INSERT INTO logs (event_type, source_ip, destination, device_name, details, log_level) VALUES (?, ?, ?, ?, ?, ?)',
        ('ALERT_RESOLVED', 'Admin Console', 'IDS System', 'Admin', f'Alert #{alert_id} resolved by administrator.', 'INFO')
    )
    return jsonify({'success': True, 'message': f'Alert #{alert_id} resolved.'})


# ══════════════════════════════════════════════════════════════════════════════
#  API – LOGS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/logs')
def api_logs():
    """Return logs with optional keyword search."""
    search = request.args.get('q', '').strip()
    level  = request.args.get('level', '').strip()

    sql  = 'SELECT * FROM logs'
    args = []
    conditions = []

    if search:
        conditions.append('(device_name LIKE ? OR source_ip LIKE ? OR details LIKE ? OR event_type LIKE ?)')
        args += [f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%']
    if level:
        conditions.append('log_level = ?')
        args.append(level)

    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)

    sql += ' ORDER BY timestamp DESC LIMIT 200'
    logs = query_db(sql, args)
    return jsonify(logs)


# ══════════════════════════════════════════════════════════════════════════════
#  API – REPORTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/reports/summary')
def api_reports_summary():
    """Aggregated data for the Reports page charts."""
    # Device breakdown
    safe_count       = query_db("SELECT COUNT(*) AS c FROM devices WHERE status = 'safe'", one=True)['c']
    suspicious_count = query_db("SELECT COUNT(*) AS c FROM devices WHERE status = 'suspicious'", one=True)['c']
    offline_count    = query_db("SELECT COUNT(*) AS c FROM devices WHERE status = 'offline'", one=True)['c']

    # Alert breakdown by severity
    sev_rows = query_db(
        "SELECT severity, COUNT(*) AS c FROM alerts GROUP BY severity"
    )
    severity_map = {r['severity']: r['c'] for r in sev_rows}

    # Alert breakdown by type
    type_rows = query_db(
        "SELECT alert_type, COUNT(*) AS c FROM alerts GROUP BY alert_type ORDER BY c DESC"
    )

    # Alerts over last 7 days (simulated daily distribution)
    daily_alerts = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        row = query_db(
            "SELECT COUNT(*) AS c FROM alerts WHERE timestamp LIKE ?", (f'{day}%',), one=True
        )
        daily_alerts.append({'date': day, 'count': row['c']})

    # Log level distribution
    log_rows = query_db(
        "SELECT log_level, COUNT(*) AS c FROM logs GROUP BY log_level"
    )
    log_map = {r['log_level']: r['c'] for r in log_rows}

    return jsonify({
        'device_status': {
            'safe':       safe_count,
            'suspicious': suspicious_count,
            'offline':    offline_count,
        },
        'severity_breakdown': {
            'low':      severity_map.get('low', 0),
            'medium':   severity_map.get('medium', 0),
            'high':     severity_map.get('high', 0),
            'critical': severity_map.get('critical', 0),
        },
        'alert_types':  [{'type': r['alert_type'], 'count': r['c']} for r in type_rows],
        'daily_alerts': daily_alerts,
        'log_levels': {
            'INFO':    log_map.get('INFO', 0),
            'WARNING': log_map.get('WARNING', 0),
            'DANGER':  log_map.get('DANGER', 0),
        },
    })


# ══════════════════════════════════════════════════════════════════════════════
#  INTRUSION DETECTION ENGINE  (rule-based simulation)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/detect', methods=['POST'])
def api_detect():
    """
    Run the rule-based intrusion detection engine.
    Checks all devices against four detection rules and generates alerts.
    Called by the frontend "Run Detection Scan" button.
    """
    new_alerts = []
    devices = query_db('SELECT * FROM devices')

    for device in devices:
        ip   = device['ip_address']
        name = device['name']

        # ── Rule 1: Unknown Device (MAC starts with FF or device_type is Unknown) ──
        if device['device_type'] == 'Unknown' or device['mac_address'].startswith('FF:FF'):
            _raise_alert(new_alerts, 'Unknown Device Detected', 'high', name, ip,
                         f'Device "{name}" has an unregistered MAC address and unknown device type. '
                         f'Possible rogue device on the network.')
            _update_device_status(ip, 'suspicious')
            _log_event('UNKNOWN_DEVICE', ip, 'IDS Engine', name,
                       f'Rule triggered: Unknown device. MAC: {device["mac_address"]}', 'DANGER')

        # ── Rule 2: Multiple Failed Logins (simulated by "suspicious" status + sensor type) ──
        if device['status'] == 'suspicious' and device['device_type'] == 'Sensor':
            _raise_alert(new_alerts, 'Multiple Failed Login Attempts', 'critical', name, ip,
                         f'Device "{name}" triggered brute-force detection. '
                         f'Over 10 failed authentication attempts in 60 seconds.')
            _log_event('FAILED_LOGIN', ip, 'Auth Server', name,
                       'Rule triggered: Brute-force threshold exceeded.', 'DANGER')

        # ── Rule 3: Excessive Network Requests (simulated random traffic spike for cameras) ──
        if device['device_type'] == 'Camera':
            simulated_pps = random.randint(80, 600)   # packets per second
            if simulated_pps > 400:
                _raise_alert(new_alerts, 'Excessive Network Requests', 'medium', name, ip,
                             f'Device "{name}" sent {simulated_pps} packets/s — '
                             f'{round(simulated_pps/50)}x above baseline (50 pkt/s).')
                _log_event('TRAFFIC_SPIKE', ip, 'IDS Engine', name,
                           f'Rule triggered: Packet rate {simulated_pps}/s.', 'WARNING')

        # ── Rule 4: Suspicious IP Activity (non-RFC1918 last-octet patterns) ──
        last_octet = int(ip.split('.')[-1])
        if last_octet >= 200:
            _raise_alert(new_alerts, 'Suspicious IP Activity', 'high', name, ip,
                         f'Device at {ip} has an anomalous IP address (last octet ≥200). '
                         f'May indicate unauthorized DHCP assignment or static override.')
            _log_event('SUSPICIOUS_IP', ip, 'IDS Engine', name,
                       'Rule triggered: Anomalous IP last-octet.', 'DANGER')

    # Add a scan-complete system log
    _log_event('SCAN', 'localhost', 'IDS Engine', 'IDS System',
               f'Detection scan completed. {len(new_alerts)} new alert(s) generated.', 'INFO')

    return jsonify({
        'success':    True,
        'new_alerts': len(new_alerts),
        'alerts':     new_alerts,
        'message':    f'Scan complete. {len(new_alerts)} new intrusion alert(s) generated.',
    })


# ══════════════════════════════════════════════════════════════════════════════
#  SIMULATE LIVE TRAFFIC (called by JS interval for real-time feel)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """Add one random realistic log entry to give a live-feed feeling."""
    info_events = [
        ('CONNECTION',    '192.168.1.10', 'Gateway',    'Smart Thermostat',   'Heartbeat received. Temperature: 22.4 °C.',          'INFO'),
        ('CONNECTION',    '192.168.1.12', 'Gateway',    'Smart Door Lock',    'Status ping: door locked. Battery 85%.',              'INFO'),
        ('CONNECTION',    '192.168.1.30', 'Gateway',    'Smart Meter',        'Meter sync. Cumulative: 1023.7 kWh.',                 'INFO'),
        ('CONNECTION',    '192.168.1.13', 'Gateway',    'IP Camera - Server', 'Motion event cleared. Recording saved.',              'INFO'),
        ('TRAFFIC_NORM',  '192.168.1.11', 'IDS Engine', 'IP Camera - Lobby',  'Traffic within normal bounds. 48 pkt/s.',             'INFO'),
        ('SYSTEM',        'localhost',    'IDS Engine', 'IDS System',         'Watchdog tick. All rules active.',                   'INFO'),
    ]
    warn_events = [
        ('FAILED_LOGIN',  '192.168.1.21', 'Auth Server', 'Industrial Sensor B', 'Failed SSH login attempt detected.', 'WARNING'),
        ('TRAFFIC_SPIKE', '192.168.1.21', 'IDS Engine',  'Industrial Sensor B', 'Elevated traffic: 312 pkt/s.',       'WARNING'),
        ('DISCONNECTION', '192.168.1.50', 'Switch-02',   'Access Point Node',   'Device not responding to ping.',     'WARNING'),
    ]

    # 70% chance info, 30% chance warning
    pool = info_events if random.random() < 0.7 else warn_events
    entry = random.choice(pool)
    _log_event(*entry)

    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _raise_alert(collector, alert_type, severity, device_name, ip, description):
    """Insert an alert into DB and append to collector list."""
    # Avoid exact duplicates (same type + IP already open)
    existing = query_db(
        "SELECT id FROM alerts WHERE alert_type = ? AND ip_address = ? AND status = 'open'",
        (alert_type, ip), one=True
    )
    if existing:
        return  # skip duplicate

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    aid = execute_db(
        'INSERT INTO alerts (alert_type, severity, device_name, ip_address, description, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (alert_type, severity, device_name, ip, description, 'open', ts)
    )
    collector.append({
        'id': aid, 'alert_type': alert_type, 'severity': severity,
        'device_name': device_name, 'ip_address': ip,
        'description': description, 'status': 'open', 'timestamp': ts,
    })


def _update_device_status(ip, status):
    execute_db('UPDATE devices SET status = ? WHERE ip_address = ?', (status, ip))


def _log_event(event_type, source_ip, destination, device_name, details, log_level):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_db(
        'INSERT INTO logs (event_type, source_ip, destination, device_name, details, log_level, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (event_type, source_ip, destination, device_name, details, log_level, ts)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Auto-initialize DB if it doesn't exist yet
    if not os.path.exists(DB_PATH):
        from database.init_db import init_db
        init_db()
    app.run(debug=True, port=5000)
