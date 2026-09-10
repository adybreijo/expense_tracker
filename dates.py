from datetime import date, datetime


def parse_date(value, allow_future=False):
    """Parse a date and validate it is not in the future unless allowed.

    Args:
        value: A date object, or a string in YYYY-MM-DD format.
        allow_future: If False (default), reject dates later than today.

    Returns:
        date: The parsed date.

    Raises:
        ValueError: If value is a string that doesn't match YYYY-MM-DD,
            or if the date is in the future and allow_future is False.
    """
    if isinstance(value, date):
        parsed = value
    else:
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()

        except ValueError:
            raise ValueError("Enter a valid date as YYYY-MM-DD")

    if not allow_future and parsed > date.today():
        raise ValueError("The date cannot be in the future")
    return parsed
