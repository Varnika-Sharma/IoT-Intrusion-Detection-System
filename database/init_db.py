"""
IoT IDS - Database Initialization Script
Creates SQLite database with all required tables and seed data.
Run this once before starting the Flask app.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iot_ids.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ── Devices table ─────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            ip_address  TEXT    NOT NULL UNIQUE,
            mac_address TEXT,
            device_type TEXT,
            status      TEXT    DEFAULT 'safe',   -- safe | suspicious | offline
            last_seen   TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── Intrusion alerts table ─────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type   TEXT    NOT NULL,
            severity     TEXT    NOT NULL,   -- low | medium | high | critical
            device_name  TEXT,
            ip_address   TEXT,
            description  TEXT,
            status       TEXT    DEFAULT 'open',   -- open | resolved
            timestamp    TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── Network logs table ─────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type  TEXT    NOT NULL,
            source_ip   TEXT,
            destination TEXT,
            device_name TEXT,
            details     TEXT,
            log_level   TEXT    DEFAULT 'INFO',   -- INFO | WARNING | DANGER
            timestamp   TEXT    DEFAULT (datetime('now'))
        )
    ''')

    conn.commit()

    # ── Seed sample IoT devices ────────────────────────────────────────────────
    devices = [
        ('Smart Thermostat',    '192.168.1.10', 'AA:BB:CC:DD:EE:01', 'HVAC',       'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('IP Camera - Lobby',   '192.168.1.11', 'AA:BB:CC:DD:EE:02', 'Camera',     'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Smart Door Lock',     '192.168.1.12', 'AA:BB:CC:DD:EE:03', 'Security',   'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Industrial Sensor A', '192.168.1.20', 'AA:BB:CC:DD:EE:04', 'Sensor',     'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Industrial Sensor B', '192.168.1.21', 'AA:BB:CC:DD:EE:05', 'Sensor',     'suspicious', (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')),
        ('Smart Meter',         '192.168.1.30', 'AA:BB:CC:DD:EE:06', 'Energy',     'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Ventilation Unit',    '192.168.1.31', 'AA:BB:CC:DD:EE:07', 'HVAC',       'safe',       (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')),
        ('Unknown Device',      '192.168.1.99', 'FF:FF:FF:FF:FF:FF', 'Unknown',    'suspicious', (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')),
        ('IP Camera - Server',  '192.168.1.13', 'AA:BB:CC:DD:EE:08', 'Camera',     'safe',       datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Access Point Node',   '192.168.1.50', 'AA:BB:CC:DD:EE:09', 'Network',    'offline',    (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')),
    ]

    for dev in devices:
        cursor.execute('''
            INSERT OR IGNORE INTO devices (name, ip_address, mac_address, device_type, status, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', dev)

    conn.commit()

    # ── Seed sample alerts ─────────────────────────────────────────────────────
    now = datetime.now()
    alert_types = [
        ('Unknown Device Detected',       'high',     'Unknown Device',      '192.168.1.99',  'An unregistered MAC address FF:FF:FF:FF:FF:FF connected to the network.',          'open'),
        ('Multiple Failed Login Attempts', 'critical', 'Industrial Sensor B', '192.168.1.21',  '15 failed SSH login attempts detected within 60 seconds.',                         'open'),
        ('Excessive Network Requests',    'medium',   'Industrial Sensor B', '192.168.1.21',  'Device sent 4500 packets in 10 seconds — 9x above normal threshold.',               'open'),
        ('Suspicious IP Activity',        'high',     'Unknown Device',      '10.0.0.254',    'Outbound connection attempt to known malicious IP 10.0.0.254 blocked.',             'open'),
        ('Port Scan Detected',            'critical', 'Unknown Device',      '192.168.1.99',  'Sequential port scan from 192.168.1.99 covering ports 1–1024.',                    'open'),
        ('Unknown Device Detected',       'medium',   'Rogue Sensor',        '192.168.1.77',  'MAC address not in the approved device registry joined network segment B.',         'resolved'),
        ('Excessive Network Requests',    'low',      'Smart Meter',         '192.168.1.30',  'Slightly elevated packet rate (180/s vs 150/s baseline) — monitoring in progress.', 'resolved'),
        ('Suspicious IP Activity',        'high',     'IP Camera - Lobby',   '192.168.1.11',  'Attempted connection to external IP 203.0.113.42 on port 4444.',                   'open'),
    ]

    for i, alert in enumerate(alert_types):
        ts = (now - timedelta(hours=i * 2, minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, device_name, ip_address, description, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (*alert, ts))

    conn.commit()

    # ── Seed sample logs ───────────────────────────────────────────────────────
    log_entries = [
        ('CONNECTION',       '192.168.1.10', 'Gateway',       'Smart Thermostat',    'Device connected. Normal heartbeat established.',                         'INFO'),
        ('FAILED_LOGIN',     '192.168.1.21', 'Auth Server',   'Industrial Sensor B', 'Failed authentication attempt #1. Protocol: SSH.',                        'WARNING'),
        ('FAILED_LOGIN',     '192.168.1.21', 'Auth Server',   'Industrial Sensor B', 'Failed authentication attempt #7. Protocol: SSH.',                        'WARNING'),
        ('FAILED_LOGIN',     '192.168.1.21', 'Auth Server',   'Industrial Sensor B', 'Failed authentication attempt #15. Threshold exceeded — alert raised.',   'DANGER'),
        ('UNKNOWN_DEVICE',   '192.168.1.99', 'Switch-01',     'Unknown Device',      'Unregistered device joined VLAN 10. MAC: FF:FF:FF:FF:FF:FF.',             'DANGER'),
        ('TRAFFIC_SPIKE',    '192.168.1.21', 'IDS Engine',    'Industrial Sensor B', 'Packet rate 4500/s detected. Threshold: 500/s.',                          'DANGER'),
        ('OUTBOUND_BLOCK',   '192.168.1.11', 'Firewall',      'IP Camera - Lobby',   'Outbound TCP blocked to 203.0.113.42:4444 — suspicious port.',            'DANGER'),
        ('PORT_SCAN',        '192.168.1.99', 'IDS Engine',    'Unknown Device',      'Sequential port probing detected. Ports 1–1024 scanned in 4.2s.',         'DANGER'),
        ('CONNECTION',       '192.168.1.30', 'Gateway',       'Smart Meter',         'Normal meter reading sync. 0.4 kWh delta reported.',                      'INFO'),
        ('CONNECTION',       '192.168.1.12', 'Gateway',       'Smart Door Lock',     'Door lock heartbeat. Status: locked. Battery: 87%.',                      'INFO'),
        ('DISCONNECTION',    '192.168.1.50', 'Switch-02',     'Access Point Node',   'Device went offline. No response to ping for 120s.',                      'WARNING'),
        ('TRAFFIC_SPIKE',    '192.168.1.30', 'IDS Engine',    'Smart Meter',         'Minor traffic elevation noted. 180 packets/s vs 150/s baseline.',          'WARNING'),
        ('ALERT_RESOLVED',   '192.168.1.30', 'Admin Console', 'Smart Meter',         'Alert #7 marked resolved by system administrator.',                       'INFO'),
        ('CONNECTION',       '192.168.1.13', 'Gateway',       'IP Camera - Server',  'Reconnected after firmware update. Firmware v3.1.2 confirmed.',            'INFO'),
        ('SYSTEM',           'localhost',    'IDS Engine',    'IDS System',          'Intrusion Detection Engine started. Rules loaded: 12. Devices monitored: 10.', 'INFO'),
    ]

    for i, log in enumerate(log_entries):
        ts = (now - timedelta(minutes=i * 8 + random.randint(0, 7))).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO logs (event_type, source_ip, destination, device_name, details, log_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (*log, ts))

    conn.commit()
    conn.close()
    print(f"[✓] Database initialized at {DB_PATH}")
    print(f"[✓] {len(devices)} devices, {len(alert_types)} alerts, {len(log_entries)} log entries seeded.")


if __name__ == '__main__':
    init_db()
