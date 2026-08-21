from datetime import date, datetime

import cli
import storage
from . import dates
from . import queries



def add_valid_date(prompt,default= None,allow_future= False):
    """Return a date as YYYY-MM-DD."""
    if default is not None:
        default = dates.parse_date(default,allow_future)
        prompt = f'{prompt.rstrip()} [{default.isoformat()}]: '

    while True:
        entry = cli.check_cancel(input(prompt)).strip()

        if not entry:
            if default is not None:
                return default.isoformat()
            print('Enter a date, try again...')
            continue

        try:
            return dates.parse_date(entry, allow_future).isoformat()
        except ValueError as err:
            print(f'{err}, try again...')


def add_data(previous_data,prompt,field):
    """
    used in add_complete_purchase() to
    let the user pick an existing value or type a new one
    """
    if not all(isinstance(value, str) for value in (prompt, field)):
        print('Prompt and field must be strings')
        return None
    
    fields = queries.info_exists(previous_data,field)
    
    if not fields:
        return cli.valid_string(prompt)
        
    print(f'{field.capitalize()}: ')
    options = tuple(range(1,len(fields) + 1))
    pairs = tuple(enumerate(fields,start=1))

    for number, name in  pairs:
        print(f"{number}: {name}")

    while True:
        chose = cli.read_int('Choose the number: ')
        chose_in_options = cli.value_in_options(chose,*options) 
        if chose_in_options:         
            for number, name in pairs:
                if number == chose:
                    return name
        print("Enter a valid option.")



def add_complete_purchase():
    previous_data = storage.load_json({"expenses": [], "receipts": []},)
    print(f" -- Type: *{', '.join(cli.CANCEL_WORDS)}'* at any time to cancel and return to the menu.--")
    print("Please enter your purchase information as follows:")
    expenses = []
    receipt = []

    try:
    
        purchase_date = add_valid_date('Date [YYYY-MM-DD]: ')
        store = add_data(previous_data["expenses"],'Store: ','store')
        total_paid = cli.read_float("Enter the total you paid: ", min_value=0.01)
        receipt.append({'date':purchase_date, 'store': store,'total_paid':total_paid})

        while True:
            product = cli.check_cancel(input('Product: ')).strip()
            if not product:
                break
            category = add_data(previous_data["expenses"],'Category: ','category')
            price = cli.read_float('Product price: ', min_value=0.01)
            paid = cli.read_float('How much you paid: ', min_value=0.01)

            quantity = cli.read_int('Quantity: ',default=1,min_value=1)
            unit = cli.valid_string('Unit [u]: ',default='u')
            notes = cli.check_cancel(input('Enter adicional notes: '))

            new_expense = {'date': purchase_date, 'store': store,'product':product,'category':category,'price':price,'paid':paid,'quantity':quantity,'unit':unit,'notes':notes}
            expenses.append(new_expense)

            print(f' -- {product}  -{category} -{price:.2f}')
            
    except cli.Cancelled:
        print()

    if not expenses:
        print('Nothing was added')
        return

    previous_data["expenses"].extend(expenses)
    previous_data["receipts"].extend(receipt)

    storage.save_json(previous_data)

