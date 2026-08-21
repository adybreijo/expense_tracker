
def info_exists(data, field):
    """
    It iterates over a list of dictionaries, and selesct the given fields,
    it returns a list with all tha values of the field given or empty if none
    """
    seen = []
    seen_lower = set()
    for dictionary in data:
        value = dictionary.get(field)
        if value is not None and value.lower() not in seen_lower:
            seen.append(value)
            seen_lower.add(value.lower())
    return seen



def filter_by_product(expenses, product):
    pass

def filter_by_category(expenses, category):
    pass

def stores(expenses):
    pass

def filter_by_date(expenses, date):
    pass

def filter_by_period(expenses, start, end):
    pass

def total(expenses):
    pass

# pasar toda la info del json o ya filtrada??