import json
import os

CONFIG_PATH = "gpio_config.json"

# $ raspi-gpio get
DEFAULT_CONFIG = {
    "available_pins": list(range(0, 28)),  # GPIO 0~27
    "enabled_pins": []  # 尚未啟用任何 pin
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def enable_pin(pin):
    config = load_config()
    if pin not in config["enabled_pins"]:
        config["enabled_pins"].append(pin)
    save_config(config)

def disable_pin(pin):
    config = load_config()
    if pin in config["enabled_pins"]:
        config["enabled_pins"].remove(pin)
    save_config(config)
