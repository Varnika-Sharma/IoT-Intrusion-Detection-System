import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database",
    "iot_ids.db"
)

if not os.path.exists(DB_PATH):
    from database.init_db import init_db
    init_db()

from app import app
