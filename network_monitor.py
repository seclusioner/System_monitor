import psutil
import time
import os
import json
import socket

NET_TMP_FILE = "/tmp/net_stats.json"

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def get_net_speed():
    current = psutil.net_io_counters()
    now = time.time()

    if os.path.exists(NET_TMP_FILE):
        try:
            with open(NET_TMP_FILE, 'r') as f:
                last = json.load(f)
        except json.JSONDecodeError:
            last = {
                'bytes_sent': current.bytes_sent,
                'bytes_recv': current.bytes_recv,
                'time': now
            }
    else:
        last = {
            'bytes_sent': current.bytes_sent,
            'bytes_recv': current.bytes_recv,
            'time': now
        }

    with open(NET_TMP_FILE, 'w') as f:
        json.dump({
            'bytes_sent': current.bytes_sent,
            'bytes_recv': current.bytes_recv,
            'time': now
        }, f)

    time_diff = now - last['time'] if now - last['time'] > 0 else 1
    tx_speed = (current.bytes_sent - last['bytes_sent']) / time_diff
    rx_speed = (current.bytes_recv - last['bytes_recv']) / time_diff

    return tx_speed, rx_speed