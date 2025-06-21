import json
import os

DATA_FILE = 'products_providers.json'
CONFIG_FILE = 'config.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def add_record(record):
    data = load_data()
    data.append(record)
    save_data(data)

def delete_record(index):
    data = load_data()
    if 0 <= index < len(data):
        data.pop(index)
        save_data(data)

def modify_record(record):
    data = load_data()
    for i, r in enumerate(data):
        if r['blueprint_id'] == record['blueprint_id'] and r['provider']['id'] == record['provider']['id']:
            data[i] = record
            save_data(data)
            break

def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("Config file not found.")
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)
