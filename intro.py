import json
import os

DATA_PATH = os.path.dirname(os.path.abspath(__file__))
JSON_DATA = os.path.join(DATA_PATH,'expenses.json')

def load_json(path,default):
    if not os.path.exists(path):
        print(f'The path does not exist: {path}') 
        return default
    if os.path.getsize(path) == 0:
        print('This file is empty')
        return default
    try:
        with open(path,'r',encoding='utf-8') as file:
                return json.load(file)
    except json.JSONDecodeError as error:
            print(f'Invalid JSON content: {error}')
            return default


def save_json(path,data):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data,file)

