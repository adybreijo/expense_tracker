def receipt_product(receipts):
    """Flatten receipts into (receipt, product) pairs.
    Each pair references the live receipt and product dicts (not copies),
    so editing an item through a pair also edits it inside its receipt.
    Args:
        receipts: List of receipt dicts.
    Returns:
        list: (receipt, product) tuples, one per product across all receipts.
    """
    result = []
    for receipt in receipts:
        for item in receipt["products"]:
            result.append((receipt, item))
    return result


def only_products(receipts):
    """Collect every product across all receipts, without its receipt.
    Args:
        receipts: List of receipt dicts.
    Returns:
        list: The product dicts (live references), receipt info discarded.
    """
    pairs = receipt_product(receipts)
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
    return [(receipt, item) for receipt, item in pairs if receipt.get(field, item.get(field)) == info]


def receipts_by_field(receipts, field, value):
    """Return the receipts where a receipt or product field equals value, each listed once.
    Args:
        receipts: List of receipt dicts.
        field: Name of the field to compare (e.g. "store", "category").
        value: Value the field must equal.
    Returns:
        list: The matching receipt dicts, without duplicates.
    """
    pairs = filter_pairs(receipt_product(receipts), field, value)
    results = []
    seen_ids = set()

    for receipt, _ in pairs:
        if receipt["receipt_id"] not in seen_ids:
            results.append(receipt)
            seen_ids.add(receipt["receipt_id"])
    return results


def filter_by_period(receipts, start, end):
    """Return the receipts whose date falls within [start, end].
    Args:
        receipts: List of receipt dicts.
        start: Start of the period, as an ISO date string.
        end: End of the period, as an ISO date string.
    Returns:
        list: The matching receipt dicts.
    """
    receipt_period = [expense for expense in receipts if start <= expense["date"] <= end]
    return sorted(receipt_period, key=lambda receipt: receipt["date"])


def values_for_field(receipts, field):
    """List the distinct values of a field, looking at receipts for "store" and "notes" and at products otherwise.
    Args:
        receipts: List of receipt dicts.
        field: "store", "notes", "product" or "category".
    Returns:
        list: Distinct values, sorted alphabetically (empty list if none).
    """
    if field in ("store", "notes"):
        return fields_names(receipts, field)
    return fields_names(only_products(receipts), field)


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


def next_receipt_id(data):
    """Hand out the next receipt id and advance the saved counter.
    Unlike generate_id, ids are never reused, even after deleting the
    newest receipt.
    Args:
        data: The full data dict; its "next_receipt_id" is incremented.
    Returns:
        int: The id to use for the new receipt.
    """
    receipt_id = data["next_receipt_id"]
    data["next_receipt_id"] += 1
    return receipt_id


def get_category(data_categories, product):
    """Look up the category saved for a product.
    Args:
        data_categories: The catalog dict ({product: category}).
        product: The product name to look up.
    Returns:
        str: The product's category, or None if it isn't in the catalog.
    """
    return data_categories.get(product)


def category_names(data_categories):
    """Collect the distinct categories saved in the catalog.
    Comparison is case-insensitive; the first-seen casing is kept.
    Args:
        data_categories: The catalog dict ({product: category}).
    Returns:
        list: Distinct categories, sorted alphabetically
            (case-insensitive, empty list if none).
    """
    seen = []
    seen_lower = set()
    for category in data_categories.values():
        if category.lower() not in seen_lower:
            seen.append(category)
            seen_lower.add(category.lower())
    return sorted(seen, key=str.lower)


def update_category(products, product, new_category):
    """Set a product's category on every line where it differs.
    Edits the product dicts in place.
    Args:
        products: List of product dicts (live references, e.g. from
            only_products()).
        product: Name of the product to recategorize.
        new_category: Category to set.
    Returns:
        int: How many lines were changed.
    """
    changed = 0
    for item in products:
        if item["product"] == product and item["category"] != new_category:
            item["category"] = new_category
            changed += 1
    return changed


def is_period_ok(start_date, end_date):
    """Check that a date range is valid (start on or before end).

    Args:
        start_date: Start of the period, as an ISO date string.
        end_date: End of the period, as an ISO date string.

    Returns:
        bool: True if start_date <= end_date.
    """
    return start_date <= end_date


def current_dates_period(receipts):
    """Find the earliest and latest receipt dates.
    Args:
        receipts: List of receipt dicts.
    Returns:
        tuple: (min_date, max_date) as ISO date strings, or (None, None) if the list is empty.
    """
    dates = [receipt["date"] for receipt in receipts]
    return (min(dates), max(dates)) if dates else (None, None)
