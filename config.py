import json
import os

def load_config():
    with open(config_file, 'r') as configfile:
        CONFIG = json.load(configfile)
    return CONFIG

def save_config():
    with open(config_file, 'w') as configfile:
        json.dump(CONFIG, configfile, indent=4,ensure_ascii=False)

run_path = os.path.split(os.path.realpath(__file__))[0]
# RUN_PATH = os.getcwd()

config_file = f'{run_path}/tw.json'
CONFIG = load_config()
if not "LifetimeStats" in CONFIG:
    CONFIG["LifetimeStats"] = {}
