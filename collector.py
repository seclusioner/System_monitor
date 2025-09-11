from database import create_table, insert_stats
from network_monitor import get_net_speed, check_internet
from email_notify import send_email
import psutil
import os

FLAG_PATH = "/tmp/temp_alert.flag"
NET_ALERT_FLAG = "/tmp/net_alert_flag"

def should_send_net_alert(is_connected: bool):
    """
    判斷是否要針對網路斷線發送 Email：
    - 若當前為斷線且尚未發送過，回傳 True 並寫入旗標
    - 若恢復連線且之前發送過，則清除旗標
    - 其他狀況不發信
    """
    if not is_connected and not os.path.exists(NET_ALERT_FLAG):
        with open(NET_ALERT_FLAG, 'w') as f:
            f.write("sent")
        return True

    elif is_connected and os.path.exists(NET_ALERT_FLAG):
        os.remove(NET_ALERT_FLAG)

    return False

def should_send_temp_alert(current_temp, threshold=70, cooldown=65):
    if current_temp >= threshold and not os.path.exists(FLAG_PATH):
        with open(FLAG_PATH, 'w') as f:
            f.write("sent")
        return True  # 要發信
    elif current_temp < cooldown and os.path.exists(FLAG_PATH):
        os.remove(FLAG_PATH)  # 溫度回穩後清除旗標
    return False

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_raw = f.readline()
            return round(int(temp_raw) / 1000, 1)
    except:
        return None

def collect_and_store():
    ######## HW usage ########
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temperature = get_cpu_temperature()

    ######## CPU loading ########
    load1, load5, load15 = os.getloadavg()
    
    ######## Internet ########
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    tx_speed, rx_speed = get_net_speed()
    flag_internet = check_internet()

    ######## Insert into DB ########
    insert_stats(cpu, memory, disk, temperature, load1, load5, load15)

    print(f"Inserted: CPU={cpu}%, Mem={memory}%, Disk={disk}%, Temp={temperature}°C, Load={load1}, " \
        f"Tx: {bytes_sent / (1024**2):.4f} MB, Rx: {bytes_recv / (1024**2):.4f} MB, " \
        f"Tx rate = {tx_speed/1024:.2f} KB/s, Rx rate = {rx_speed/1024:.2f} KB/s")
    
    if temperature and should_send_temp_alert(temperature):
        send_email("⚠️ 樹梅派溫度過高", f"偵測到CPU 溫度為 {temperature}°C")

    if should_send_net_alert(flag_internet):
        send_email("⚠️ 樹梅派網路斷線", f"偵測到樹梅派網路斷線，請檢察區域網路是否正確")

if __name__ == "__main__":
    create_table()
    collect_and_store()
