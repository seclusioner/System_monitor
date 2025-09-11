from dotenv import load_dotenv
import subprocess
import time
from database import create_table, fetch_recent_stats
from flask import Flask, request, jsonify, render_template
from network_monitor import get_net_speed
import psutil
import os

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

import RPi.GPIO as GPIO
from gpio_config import load_config, enable_pin, disable_pin

GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)

import platform
import socket

REVISION_MAP = {
    ##### Raspberry Pi 3 Model B (BCM2837) #####
    "a02082": "BCM2837",
    "a22082": "BCM2837",
    "a020d3": "BCM2837B0",
    ##### Raspberry Pi 3 Model B+ (BCM2837B0) #####
    "a32082": "BCM2837B0",

    ##### Raspberry Pi 4 (BCM2711) #####
    # "a03111": "BCM2711",
    # "b03111": "BCM2711",
    # "c03111": "BCM2711",

    ##### 其他常見版本 #####
    # "900092": "BCM2835 (Zero)",
    # "9000c1": "BCM2835 (Zero W)",

    # 可擴充對應碼 ....
}

create_table()
app = Flask(__name__)

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_raw = f.readline()
            return round(int(temp_raw) / 1000, 1)
    except:
        return None

def get_os_release_info():
    info = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    info[k] = v.strip('"')
    except:
        pass
    return info

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "Unavailable"
    finally:
        s.close()
    return ip

def get_soc_from_revision():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "Revision" in line:
                    revision = line.strip().split(":")[1].strip().lower()
                    return REVISION_MAP.get(revision, f"Unknown SoC (rev: {revision})")
    except Exception as e:
        return f"Unavailable ({e})"
    
# User Interface
@app.route("/api")
def api():
    cpu_list = psutil.cpu_percent(interval=0.1, percpu=True)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temperature = get_cpu_temperature()
    load1, load5, load15 = os.getloadavg()
    net_io = psutil.net_io_counters()
    tx_speed, rx_speed = get_net_speed()

    return jsonify({
        "cpu": cpu_list,
        "memory": memory,
        "disk": disk,
        "temperature": temperature,
        "load1": round(load1, 2),
        "load5": round(load5, 2),
        "load15": round(load15, 2),
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv,
        'tx_speed': tx_speed,
        'rx_speed': rx_speed
    })

@app.route("/api/system_info")
def system_info():
    info = {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "device_model": "Unknown",
        "soc_chip": get_soc_from_revision(),
        "ip_address": "Unavailable"
    }

    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "Model" in line:
                    info["device_model"] = line.strip().split(":")[1].strip()
                    break
    except:
        pass

    try:
        ip = subprocess.check_output(["hostname", "-I"]).decode().split()
        if ip:
            info["ip_address"] = ip[0]
    except:
        pass

    return jsonify(info)

@app.route("/<action>", methods=["POST"])
def system_control(action):
    data = request.get_json()
    if not data or data.get("password") != ADMIN_PASSWORD:
        return jsonify({"status": "error", "message": "Incorrect password."}), 403

    if action not in ["shutdown", "reboot"]:
        return jsonify({"status": "error", "message": "Invalid action."}), 400

    # 回應前端再執行關機
    def execute_action():
        time.sleep(3)
        if action == "shutdown":
            subprocess.call(['sudo', 'shutdown', 'now'])
        else:
            subprocess.call(['sudo', 'reboot'])

    # 先用 background thread 執行 shutdown，避免阻塞 HTTP 回傳
    import threading
    threading.Thread(target=execute_action).start()

    return jsonify({"status": "success", "message": f"{action.capitalize()} initiated in 3 seconds."})


@app.route('/history')
def history():
    data = fetch_recent_stats()
    return render_template('history.html', stats=data)


@app.route("/gpio/status")
def gpio_status():
    config = load_config()
    result = []
    for pin in config["available_pins"]:
        try:
            mode = GPIO.gpio_function(pin)
            if mode == GPIO.IN:
                mode_name = "IN"
                level = GPIO.input(pin)
            elif mode == GPIO.OUT:
                mode_name = "OUT"
                level = GPIO.input(pin)
            else:
                mode_name = "ALT"
                level = None
        except Exception:
            mode_name = "UNKNOWN"
            level = None
        result.append({
            "pin": pin,
            "enabled": pin in config["enabled_pins"],
            "mode": mode_name,
            "level": level
        })
    return jsonify(result)

@app.route("/gpio/set_enable", methods=["POST"])
def set_enable():
    data = request.get_json()
    pin = data.get("pin")
    enabled = data.get("enabled")
    if enabled:
        enable_pin(pin)
    else:
        disable_pin(pin)
    return jsonify({"status": "ok", "pin": pin, "enabled": enabled})

@app.route("/gpio/configure", methods=["POST"])
def gpio_configure():
    data = request.get_json()
    pin = data.get("pin")
    direction = data.get("direction")
    try:
        if direction == "in":
            GPIO.setup(pin, GPIO.IN)
        elif direction == "out":
            GPIO.setup(pin, GPIO.OUT)
        else:
            return jsonify({"status": "error", "message": "Invalid direction"}), 400
        return jsonify({"status": "ok", "pin": pin, "direction": direction})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/gpio/set_state", methods=["POST"])
def gpio_set_state():
    data = request.get_json()
    pin = data.get("pin")
    state = data.get("state")
    try:
        # GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
        return jsonify({"status": "ok", "pin": pin, "new_state": state})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================
@app.route("/") # main page
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
