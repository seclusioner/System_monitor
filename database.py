import sqlite3
from datetime import datetime
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system_monitor.db')

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu REAL,
            memory REAL,
            disk REAL,
            temperature REAL,
            load1 REAL,
            load5 REAL,
            load15 REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_stats(cpu, memory, disk, temperature, load1, load5, load15):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute('''
        INSERT INTO system_stats (timestamp, cpu, memory, disk, temperature, load1, load5, load15)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, cpu, memory, disk, temperature, load1, load5, load15))

    conn.commit()
    conn.close()

def fetch_recent_stats(limit=100):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, cpu, memory, disk, temperature, load1, load5, load15
        FROM system_stats
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()

    stats = [
        {
            'timestamp': row[0],
            'cpu': row[1],
            'memory': row[2],
            'disk': row[3],
            'temperature': row[4],
            'load1': row[5],
            'load5': row[6],
            'load15': row[7]
        }
        for row in reversed(rows)
    ]

    return stats

