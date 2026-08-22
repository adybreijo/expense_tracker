import json
import os

DATA_PATH = os.path.dirname(os.path.abspath(__file__))
JSON_DATA = os.path.join(DATA_PATH,'expenses.json')

def load_json(default,path=JSON_DATA):
    """Load JSON data from disk.
    Args:
        default: Value to return if the file does not exist, is empty,
            or contains invalid JSON.
        path: Path to the JSON file. Defaults to JSON_DATA.
    Returns:
        The parsed JSON content, or default if the file could not be read.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return default

    try:
        with open(path,'r',encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        print(f'Warning: {path} contains invalid JSON ({error})')
        print('Starting empty — saving will overwrite the existing file.')
        return default


def save_json(data,path=JSON_DATA):
    """Write data to disk as JSON, overwriting the existing file.
    Args:
        data: A JSON-serializable object (e.g. list of dicts).
        path: Path to the JSON file. Defaults to JSON_DATA.
    """

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data,file,ensure_ascii=False ,indent=4)
