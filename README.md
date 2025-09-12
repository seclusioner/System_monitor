# Raspberry Pi System Monitoring and Remote Management Project

## 📝 Project Overview
The goal of this project is to build a remote monitoring system for Raspberry Pi's status (within a local network), with the following features:
- Regularly collect CPU, RAM, disk, and temperature information, including historical data
- Store collected data and error logs for querying (collector.log and system_monitor.db)
- Display real-time status charts via Web UI (based on Bootstrap 5 + AdminLTE)
- Provide anomaly notification functionality (via Email)
- Support remote reboot, shutdown, as well as GPIO monitoring and control

This system does not require additional hardware modules, and relies solely on the Raspberry Pi motherboard and basic software resources.


## 🧩 Tested Hardware Information
- Model: Raspberry Pi 3 Model B Rev 1.2
- Hardware Platform: BCM2835 (actually BCM2837 SoC)
- CPU Model: ARMv7 Processor rev 4 (v7l)


## Usage
Install Virtual Environment Dependencies (Run only once)
``` bash
sudo apt update
sudo apt install python3-venv -y
```

Activate Environment & Run the Program (Run only once)
``` bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Afterward, simply run the following command to start the monitoring system:
``` bash
./run.sh
```

## Code Setup
`email_notify.py`:
This .py file sends alert emails when the system detects anomalies (e.g., high CPU temperature). You need to modify this part of the code to set your email details, primarily in the following section:
``` python
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "yourpassword"
EMAIL_RECEIVER = "youremail@gmail.com"
```
For the password, refer to Google's [Apppasswords](https://myaccount.google.com/apppasswords)


`gpio_config.py`:
GPIO settings may not be compatible, so you might need to modify the DEFAULT_CONFIG section or directly modify the .json file. The current configuration is as follows:
``` python
import json
import os

CONFIG_PATH = "gpio_config.json"

# $ raspi-gpio get
DEFAULT_CONFIG = {
    "available_pins": list(range(0, 28)),  # GPIO 0~27
    "enabled_pins": []  # 尚未啟用任何 pin
}
...
```

`.env`:
Remote reboot and shutdown require the user to input a password. You need to create the .env file and add your password as follows:
``` bash
nano .env
ADMIN_PASSWORD=yourpassword
```

## System Setup
* Automatic Scheduling
Run the following command to edit your crontab file:
``` bash
crontab -e
```

Then, add the following entries:
``` bash
@reboot rm -f /home/pi/collector.log
* * * * * /usr/bin/python3 /home/pi/Desktop/system_monitor/collector.py >> /home/pi/collector.log 2>&1
0 * * * * /usr/bin/python3 /home/pi/Desktop/system_monitor/cleaner.py
0 0 * * * > /home/pi/collector.log
```

## 參考
- UI Interface：[AdminLTE](https://github.com/ColorlibHQ/AdminLTE)
