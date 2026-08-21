from datetime import date, datetime

def parse_date(value,allow_future= False):
    """Returns a date or ValueError with the proper message."""
    if isinstance(value,date):
        parsed = value
    else:
        try:
            parsed = datetime.strptime(value, '%Y-%m-%d').date()

        except ValueError:
            raise ValueError('Enter a valid date as YYYY-MM-DD')
        
    if not allow_future and parsed > date.today():
        raise ValueError('The date cannot be in the future')
    return parsed
