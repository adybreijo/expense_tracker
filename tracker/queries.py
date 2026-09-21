def receipt_product(data):
    """Flatten all receipts into (receipt, product) pairs.
    Each pair references the live receipt and product dicts (not copies),
    so editing an item through a pair also edits it inside `data`.
    Args:
        data: The full data dict ({"receipts": [...]}).
    Returns:
        list: (receipt, product) tuples, one per product across all receipts.
    """
    result = []

    for receipt in data["receipts"]:
        for item in receipt["products"]:
            result.append((receipt, item))

    return result


def only_products(data):
    """Collect every product across all receipts, without its receipt.
    Args:
        data: The full data dict ({"receipts": [...]}).
    Returns:
        list: The product dicts (live references), receipt info discarded.
    """
    pairs = receipt_product(data)
    return [item for _, item in pairs]


def fields_names(data, field):
    """Collect the distinct values of a field across a list of dicts.
    Comparison is case-insensitive; the first-seen casing of each value is
    kept, but the result is sorted alphabetically (case-insensitive) for
    display.
    Args:
        data: List of dicts (e.g. receipts or products).
        field: Name of the field to collect values for (e.g. "store",
            "category", "product").
    Returns:
        list: Distinct values found for field, sorted alphabetically
            (case-insensitive, empty list if none).
    """
    seen = []
    seen_lower = set()
    for dictionary in data:
        value = dictionary[field]
        if value is not None and value.lower() not in seen_lower:
            seen.append(value)
            seen_lower.add(value.lower())
    return sorted(seen, key=str.lower)


def filter_pairs(pairs, field, info):
    """Filter (receipt, item) pairs by a receipt-level or product-level field.
    The field is looked up on the receipt first, then on the product.
    Args:
        pairs: List of (receipt, item) tuples, as built by receipt_product().
        field: Name of the field to compare (e.g. "store", "category").
        info: Value the field must equal.
    Returns:
        list: The (receipt, item) tuples where the field equals info.
    """
    return [
        (receipt, item)
        for receipt, item in pairs
        if receipt.get(field, item.get(field)) == info
    ]


def filter_by_period(receipts, start, end):
    """Return the receipts whose date falls within [start, end].
    Args:
        receipts: List of receipt dicts.
        start: Start of the period, as an ISO date string.
        end: End of the period, as an ISO date string.
    Returns:
        list: The matching receipt dicts.
    """
    return [expense for expense in receipts if start <= expense["date"] <= end]


def generate_id(data, field):
    """Compute the next id to use for a new receipt or product.
    Uses max(existing ids) + 1 instead of len(data) + 1, so ids stay unique
    even after something in the middle of the list has been deleted. Product
    ids are only unique within their own receipt's "products" list.
    Args:
        data: List of dicts to scan (e.g. data["receipts"] for a new
            receipt_id, or the products of one receipt for a new
            product_id).
        field: Name of the id field to look at (e.g. "receipt_id",
            "product_id").
    Returns:
        int: 1 if data is empty, otherwise the highest existing value of
            field, plus 1.
    """
    return max((receipt[field] for receipt in data), default=0) + 1
