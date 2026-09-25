from datetime import date
import math

import dates

CANCEL_WORDS = {"q", "quit", "cancel"}


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


def read_int(prompt="Enter a valid number", default=None, min_value=0):
    """Prompt the user for an integer, retrying until a valid one is entered.
    Args:
        prompt: Text shown to the user.
        default: Value returned if the user presses Enter without typing anything.
        min_value: Smallest value accepted; lower entries are rejected.
    Returns:
        int: The value the user entered, or default.
    Raises:
        Cancelled: If the user types a cancel word.
    """

    return _read_number(prompt, int, default, min_value)


def read_float(prompt, default=None, min_value=0):
    """Prompt the user for a float, retrying until a valid one is entered.
    Args:
        prompt: Text shown to the user.
        default: Value returned if the user presses Enter without typing anything.
        min_value: Smallest value accepted; lower entries are rejected.
    Returns:
        float: The value the user entered, or default.
    Raises:
        Cancelled: If the user types a cancel word.
    """

    return _read_number(prompt, float, default, min_value)


def _read_number(prompt, cast, default=None, min_value=0):
    """Shared input loop for read_int / read_float.

    Args:
        prompt: Text shown to the user.
        cast: Type to convert the raw input to (int or float).
        default: Value returned if the user presses Enter without typing anything.
        min_value: Smallest value accepted; lower entries are rejected.

    Returns:
        The parsed and validated value, or default.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    while True:

        entry = check_cancel(input(prompt)).strip()

        if not entry and default is not None:
            return default

        try:
            value = cast(entry)
        except ValueError:
            print("Enter a valid number, try again...")
            continue

        if not math.isfinite(value):
            print("Enter a valid number, try again...")
            continue

        if value < min_value:
            print(f"The value cannot be less than {min_value}, try again...")
            continue
        return value


def valid_string(prompt, default=None, letters_only=False):
    """Ask until the user types a non-empty string.

    Args:
        prompt: Text shown to the user.
        default: Value returned if the user presses Enter without typing anything.
        letters_only: If True, reject any input containing characters other
            than letters or spaces.

    Returns:
        str: The text the user entered, in lowercase, or default.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    while True:
        info = check_cancel(input(prompt)).strip()

        if not info:
            if default is not None:
                return default

            print("This field cannot be empty, try again...")
            continue

        if letters_only and not all(c.isalpha() or c.isspace() for c in info):
            print("Only letters are allowed, try again...")
            continue
        return info.lower()


def yes_no_question(prompt):
    """Ask a yes/no question until the user answers 'y' or 'n'.

    Args:
        prompt: Text shown to the user.

    Returns:
        bool: True if the user answered 'y', False if 'n'.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    while True:
        answer = check_cancel(input(prompt)).strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False

        print("Please enter 'y' or 'n'.")


def value_in_options(value, *options):
    """Check whether value is one of the given integer options.

    Args:
        value: The value to check.
        *options: The allowed integer values.

    Returns:
        bool: True if value is an int (not bool) present in options; False
            otherwise (also prints a warning if any argument is not an int).
    """
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in (*options, value)):
        print("All options must be integers")
        return False
    return value in options


def chose_from_list(options, prompt="Choose the number: ", default=None):
    """Print a numbered list and let the user pick one item from it.
    Args:
        options: Sequence of strings to choose from; each is shown by its
            position (1-based). Items must be strings (they are capitalized
            for display).
        prompt: Text shown when asking for the number.
        default: Item to return if the user presses Enter without typing
            anything; must be present in options to take effect.
    Returns:
        The selected item from options.
    Raises:
        Cancelled: If the user types a cancel word.
    """
    if options:
        print(prompt)
        for number, name in enumerate(options, start=1):
            print(f"{number}: {name.capitalize()}")

    default_index = options.index(default) + 1 if default in options else None

    while True:
        chose = read_int(prompt=">>: ", default=default_index)
        if value_in_options(chose, *range(1, len(options) + 1)):
            return options[chose - 1]
        print("Enter a valid option.")


def add_valid_date(prompt="Enter a date [DD-MM-YYYY]: ", default=None, allow_future=False):
    """Prompt the user for a date and return it in ISO format.
    Args:
        prompt: Text shown to the user; if default is given, the default
            date is appended to it in brackets.
        default: Date (ISO string YYYY-MM-DD or date object) returned if the
            user presses Enter without typing anything.
        allow_future: If False (default), reject dates later than today.
    Returns:
        str: The chosen date in ISO format (YYYY-MM-DD).
    Raises:
        Cancelled: If the user types a cancel word.
    """
    if default is not None:
        if isinstance(default, str):
            default = date.fromisoformat(default)
        default = dates.parse_date(default, allow_future)
        prompt = f"{prompt.rstrip()} [{default.isoformat()}]: "

    while True:
        entry = check_cancel(input(prompt)).strip()

        if not entry:
            if default is not None:
                return default.isoformat()
            print("Enter a date, try again...")
            continue

        try:
            return dates.parse_date(entry, allow_future).isoformat()
        except ValueError as err:
            print(f"{err}, try again...")
