def receip_item(data):
    result = []
    for receipt in data["receipts"]:
        for item in receipt["products"]:
            result.append((receipt, item))
    return result

def only_products(data):
    pairs = receip_item(data)
    return [item for _, item in pairs]
    

def fields_names(data, field):
    """Collect the distinct values of a field across a list of expenses.

    Comparison is case-insensitive; the first-seen casing of each value is
    kept in the result.

    Args:
        data: List of expense dicts.
        field: Name of the field to collect values for (e.g. "store").

    Returns:
        list: Distinct values found for field, in first-seen order (empty
            list if none).
    """
    seen = []
    seen_lower = set()
    for dictionary in data:
        value = dictionary.get(field)
        if value is not None and value.lower() not in seen_lower:
            seen.append(value)
            seen_lower.add(value.lower())
    return sorted(seen, key=str.lower) 


def filter_pairs(pairs, field, info):
    """Filter (receipt, item) pairs by a receipt-level or product-level field."""
    return [
        (receipt, item)
        for receipt, item in pairs
        if receipt.get(field, item.get(field)) == info
    ]


def filter_by_field(expenses, field, info):

    return [expense for expense in expenses if expense[field] == info]


def filter_by_period(expenses, start, end):
    """Return the expenses whose date falls within [start, end].

    Args:
        expenses: List of expense dicts.
        start: Start of the period, as an ISO date string.
        end: End of the period, as an ISO date string.

    Returns:
        list: The matching expense dicts.
    """
    return [expense for expense in expenses if start <= expense["date"] <= end]


def generate_id(data,field):
    return max((receipt[field] for receipt in data), default=0) + 1
    



#   { 
#       "receipt_id": "2"
#       "date": "2026-08-05",
#       "store": "Bodega Aurrera",
#       "total_paid": 1455.00,
#       "notes": "compra quincenal",76r
#       "products": [
#         {"product_id": "1","product": "pollo", "category": "carnicos",    "unit_price": 50.50,  "total_paid": 505.00},
#         {"product_id": "2","product": "arroz", "category": "misceláneas", "unit_price": 950.00, "total_paid": 950.00},
#         {"product_id": "3","product": "leche",  "category": "lacteos",   "unit_price": 30.00, "total_paid": 30.00},
#         {"product_id": "4","product": "pan",    "category": "panaderia", "unit_price": 25.00, "total_paid": 25.00},
#         {"product_id": "5","product": "aromatizador Ponil", "category": "limpieza", "unit_price": 50.00, "total_paid": 50.00}
#       ]
#     }
