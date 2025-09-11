import sqlite3
from datetime import datetime, timedelta
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system_monitor.db')

def clean_old_records(hours=3):
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_time.isoformat()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM system_stats WHERE timestamp < ?", (cutoff_str,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Deleted {deleted} old records before {cutoff_str}")

if __name__ == "__main__":
    clean_old_records()
