#!/usr/bin/env python3
"""
IoT IDS — One-command setup + launch script.
Run this instead of app.py on first launch:  python run.py
After first launch you can also use:         python app.py
"""

import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'iot_ids.db')

# Auto-init database if missing
if not os.path.exists(DB_PATH):
    print("[*] Database not found. Initializing…")
    from database.init_db import init_db
    init_db()
else:
    print(f"[✓] Database found at {DB_PATH}")

# Launch Flask
print("[*] Starting IoT IDS Flask server…")
print("[*] Open your browser and visit:  http://127.0.0.1:5000")
print("[*] Press Ctrl+C to stop the server.\n")

from app import app
app.run(debug=True, port=5000, use_reloader=False)
