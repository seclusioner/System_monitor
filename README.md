# Raspberry Pi System Monitoring and Remote Management Project

## 📝 Project Overview
The goal of this project is to build a remote monitoring system for Raspberry Pi's status (within a local network), with the following features:
- Regularly collect CPU, RAM, disk, and temperature information, including historical data
- Store collected data and error logs for querying (collector.log and system_monitor.db)
- Display real-time status charts via Web UI (based on Bootstrap 5 + AdminLTE)
- Provide anomaly notification functionality (via Email)
- Support remote reboot, shutdown, as well as GPIO monitoring and control

This system does not require additional hardware modules, and relies solely on the Raspberry Pi motherboard and basic software resources.

Demo Video: [Youtube](https://youtu.be/WHCoINdR3FU)

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
Remote reboot and shutdown require the user to input a password, and system will sends alert emails when the system detects anomalies (e.g., high CPU temperature). You need to create this file to set your password and email details, as the following section:

``` bash
nano .env # only once
ADMIN_PASSWORD=yourpassword
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "yourpassword"
EMAIL_RECEIVER = "youremail@gmail.com"
```

For the email password, refer to Google's [Apppasswords](https://myaccount.google.com/apppasswords)

## System Setup (Option)
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

* System service
If you want to activate the service automatically, you can set the system service:
``` bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable system-monitor.service
```

Create content of `system-monitor.service`:
``` txt
# /etc/systemd/system/system-monitor.service
[Unit]
Description=Raspberry Pi System Monitor Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Desktop/system_monitor
ExecStart=/bin/bash /home/pi/Desktop/system_monitor/run.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Setting & Activate:
``` bash
sudo systemctl enable system-monitor.service
sudo systemctl start system-monitor.service
sudo systemctl status system-monitor.service # option
```


## References
- UI Interface：[AdminLTE](https://github.com/ColorlibHQ/AdminLTE)


## Future Work
- Add C/C++ driver code to control GPIO pins directly through the UI interface
- Integrate an AI model to optimize and execute downstream tasks
