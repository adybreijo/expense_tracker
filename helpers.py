import json
import os

DATA_PATH = os.path.dirname(os.path.abspath(__file__))
JSON_DATA = os.path.join(DATA_PATH,'expenses.json')

CANCEL_WORDS = {'q', 'quit', 'cancel'}

class Cancelled(Exception):
    """The user asked to abort the current operation."""

def check_cancel(entry):
    """Check whether the user typed a word that means "cancel".
    Args:
        entry: The raw text the user typed.
    Returns:
        str: The same entry, unchanged, if it is not a cancel word.
    Raises:
        Cancelled: If entry (case-insensitive, stripped) is one of CANCEL_WORDS.
    """
    if entry.strip().lower() in CANCEL_WORDS:
        raise Cancelled
    return entry

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

def value_in_options(value,*options):
    if not all(isinstance(x, int) and not isinstance(x,bool) for x in (*options, value)):
        print("All options must be integers")
        return False
    return value in options


def read_int(prompt,default= None,min_value= 0):
    return _read_number(prompt,int,default,min_value)

def read_float(prompt, default=None,min_value = 0):
    return _read_number(prompt, float, default,min_value)

def _read_number(prompt,cast,default=None,min_value = 0):
    """Shared loop for read_int / read_float.  Rejects values below min_value."""
    while True:
        entry = check_cancel(input(prompt)).strip()

        if not entry and default is not None:
            return default

        try:
            value = cast(entry)
        except ValueError:
            print('Enter a valid number, try again...')
            continue

        if value < min_value:
            print(f'The value cannot be less than {min_value}, try again...')
            continue
        return value
     

def valid_string(prompt,default = None, letters_only = False):
    """Ask until the user types a non-empty string.
    letters_only=True rejects anything that is not a letter or a space.
    """
    while True:
        info = check_cancel(input(prompt)).strip()

        if not info:
            if default is not None:
                return default
                    
            print('This field cannot be empty, try again...')
            continue

        if letters_only and not all(c.isalpha() or c.isspace() for c in info):
                print('Only letters are allowed, try again...')
                continue
        return info
    

def yes_no_question(prompt):
    while True:
        answer = check_cancel(input(prompt)).strip().lower()
        if answer == 'y':
            return True
        if answer == 'n':
            return False

        print("Please enter 'y' or 'n'.")



# def navegate_dict(data, field, default=None):
#      for dictionary in data:
#           if field not in dictionary:
               