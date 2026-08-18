from datetime import date, datetime
import helpers


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



def add_valid_date(prompt,default= None,allow_future= False):
    """Return a date as YYYY-MM-DD."""
    if default is not None:
        default = parse_date(default,allow_future)
        prompt = f'{prompt.rstrip()} [{default.isoformat()}]: '

    while True:
        entry = helpers.check_cancel(input(prompt)).strip()

        if not entry:
            if default is not None:
                return default.isoformat()
            print('Enter a date, try again...')
            continue

        try:
            return parse_date(entry, allow_future).isoformat()
        except ValueError as err:
            print(f'{err}, try again...')


def info_exists(data, field):
    """
    It iterates over a list of dictionaries, and selesct the given fields,
    it returns a list with all tha values of the field given or empty if none
    """
    seen = []

    for dictionary in data:
        if field in dictionary and dictionary[field] not in seen:
            seen.append(dictionary[field])
    return seen


def add_data(previous_data,prompt,field):
    """
    used in add_complete_purchase() to
    let the user pick an existing value or type a new one
    """
    if not all(isinstance(value, str) for value in (prompt, field)):
        print('Prompt and field must be strings')
        return None
    
    fields = info_exists(previous_data,field)
    
    if not fields:
        return helpers.valid_string(prompt)
        
    print(f'{field.capitalice()}: ')
    options = tuple(range(1,len(fields) + 1))
    pairs = tuple(enumerate(fields,start=1))

    for number, name in  pairs:
        print(f"{number}: {name}")

    while True:
        chose = helpers.read_int('Choose the number: ')
        chose_in_options = helpers.value_in_options(chose,*options) 
        if chose_in_options:         
            for number, name in pairs:
                if number == chose:
                    return name
        print("Enter a valid option.")



def add_complete_purchase():
    previous_data = helpers.load_json([])
    print(f"Type '{', '.join(helpers.CANCEL_WORDS)}' at any prompt to cancel and return to the menu.")
    expenses = []

    try:
    
        purchase_date = add_valid_date('Date [YYYY-MM-DD]: ')
        store = add_data(previous_data,'Store: ','store')

        while True:
            product = helpers.check_cancel(input('Product: ')).strip()
            if not product:
                break
            category = add_data(previous_data,'Category: ','category')
            price = helpers.read_float('Price: ',min_value=0.01)
            quantity = helpers.read_int('Quantity: ',default=1,min_value=1)
            unit = helpers.valid_string('Unit [u]: ',default='u')

            new_expense = {'date': purchase_date, 'store': store,'product':product,'category':category,'price':price,'quantity':quantity,'unit':unit}
            expenses.append(new_expense)
            previous_data.append(new_expense)
            print(f' -- {product}  -{category} -{price:.2f}')
            
    except helpers.Cancelled:
        print()

    if not expenses:
        print('Nothing was added')
        return

    helpers.save_json(previous_data)

