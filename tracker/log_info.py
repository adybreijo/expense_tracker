import cli
import storage

from . import queries


def data_by_filter(data):
    """Ask the user for a filter and value, and return the matching receipts.
    Filters by store, exact date, product or category. Loops until at least
    one matching receipt is found.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    Returns:
        list: The receipt dicts matching the chosen filter and value, each listed once.
    """
    print("Enter the filter you want to search for: ")
    stores = queries.fields_names(data["receipts"], "store")
    products = queries.fields_names(queries.only_products(data), "product")
    categories = queries.fields_names(queries.only_products(data), "category")
    values_by_field = {"store": stores, "product": products, "category": categories}

    while True:
        filter_user = cli.chose_from_list(("store", "date", "product", "category"), "Chose filter: ")

        if filter_user == "date":
            value = cli.add_valid_date()
        else:
            options = values_by_field[filter_user]
            if not options:
                print(f"No {filter_user} recorded yet.")
                continue
            value = cli.chose_from_list(options, f"Choose {filter_user}: ")

        pairs = queries.filter_pairs(queries.receipt_product(data), filter_user, value)
        results = []
        seen_ids = set()

        for receipt, _ in pairs:
            if receipt["receipt_id"] not in seen_ids:
                results.append(receipt)
                seen_ids.add(receipt["receipt_id"])
        if not results:
            print(f"No expenses found for that {filter_user}.")
            continue
        return results


def pick_item(sorted_items):
    """Ask the user for a number until it matches one of the listed items.
    Args:
        sorted_items: The items in the same order they were printed to the user.
    Returns:
        The item the user picked.
    Raises:
        Cancelled: If the user types a cancel word.
    """
    while True:
        chose = cli.read_int(prompt=">>: ")
        if cli.value_in_options(chose, *range(1, len(sorted_items) + 1)):
            return sorted_items[chose - 1]
        print("Enter a valid option.")


def chose_product(receipt, prompt="Choose a product: "):
    """Print the products of a receipt and let the user pick one.
    Args:
        receipt: The receipt dict whose "products" list is shown.
        prompt: Text shown above the numbered list.
    Returns:
        dict: The chosen product, or None if the receipt has no products.
    Raises:
        Cancelled: If the user types a cancel word.
    """
    if not receipt["products"]:
        print("There are not products to show.")
        return None
    sorted_products = sorted(receipt["products"], key=lambda prod: prod["product"])
    print(prompt)

    for number, prod in enumerate(sorted_products, start=1):
        paid_product = f"{prod['paid_product']:.2f}"
        name = prod["product"].capitalize()
        category = prod["category"].capitalize()
        print(f"{number}: {name} - {category:<8} - ${paid_product:>9}")

    return pick_item(sorted_products)


def choose_receipt(receipts, prompt="Choose a receipt: "):
    """Print each candidate receipt and let the user pick one.
    Args:
        receipts: List of receipt dicts to choose from.
        prompt: Text shown above the numbered list.
    Returns:
        dict: The chosen receipt, or None if the list is empty.
    Raises:
        Cancelled: If the user types a cancel word.
    """
    if not receipts:
        print("There are not receipts to show.")
        return None
    print(prompt)
    sorted_receipts = sorted(receipts, key=lambda receipt: receipt["date"])
    for number, receipt in enumerate(sorted_receipts, start=1):
        price = f"{receipt['total_paid']:.2f}"
        date = receipt["date"]
        store = receipt["store"].capitalize()
        print(f"{number}: {date} - {store:<8} - ${price:>9}")

    return pick_item(sorted_receipts)


def delete_product(data, receipt_info):
    """Let the user pick one product from a receipt and delete it.
    Asks for confirmation before deleting.
    Args:
        data: The full data dict; it is saved to disk after deleting.
        receipt_info: The receipt dict the product is removed from.
    Raises:
        Cancelled: If the user types a cancel word.
    """
    one_product = chose_product(receipt_info)
    if one_product is None:
        return

    product_name = one_product["product"]
    last_product = len(receipt_info["products"]) == 1
    if last_product:
        print("This is the only product in this receipt; the receipt will be deleted too.")
    confirm = cli.yes_no_question(f"Do you want to delete {product_name.capitalize()} (y/n): ")
    if confirm:
        if last_product:
            for index, receipt in enumerate(data["receipts"]):
                if receipt["receipt_id"] == receipt_info["receipt_id"]:
                    del data["receipts"][index]
                    break
            print(f"{product_name.capitalize()} and its receipt have been erased")
        else:
            receipt_info["products"].remove(one_product)
            print(f"{product_name.capitalize()} and its data has been erased")
        storage.save_json(data)
    else:
        print("Action canceled by user")


def delete_complete_receipt(info_by_category, all_info):
    """Let the user pick one receipt from a filtered list and delete it.

    Asks for confirmation before deleting.

    Args:
        info_by_category: List of receipt dicts to choose from (the result
            of data_by_filter()).
        all_info: The full data dict; the matching receipt is removed from
            all_info["receipts"] and the change is saved to disk.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    receipt_to_delete = choose_receipt(info_by_category, prompt="Enter the number of the data to delete: ")
    print(", ".join(f"{k}: {v}" for k, v in receipt_to_delete.items() if k != "products" and k != "receipt_id"))
    confirm = cli.yes_no_question("Delete this information?? (y/n): ")
    if confirm:
        for index, receipt in enumerate(all_info["receipts"]):
            if receipt["receipt_id"] == receipt_to_delete["receipt_id"]:
                del all_info["receipts"][index]
                break
        storage.save_json(all_info)
        print("Receipt deleted successfully")
    else:
        print("Operation canceled\n")


def _is_period_ok(start_date, end_date):
    """Check that a date range is valid (start on or before end).

    Args:
        start_date: Start of the period, as an ISO date string.
        end_date: End of the period, as an ISO date string.

    Returns:
        bool: True if start_date <= end_date.
    """
    return start_date <= end_date


def _current_dates_period(receipts):
    """Find the earliest and latest receipt dates.
    Args:
        receipts: List of receipt dicts.
    Returns:
        tuple: (min_date, max_date) as ISO date strings, or (None, None) if the list is empty.
    """
    dates = [receipt["date"] for receipt in receipts]
    return (min(dates), max(dates)) if dates else (None, None)


def _print_receipt(receipt, receipt_number):
    """Print a receipt's fields followed by each of its products.
    Args:
        receipt: The receipt dict to print.
        receipt_number: Position shown in the "Receipt #" header.
    """
    date = receipt["date"]
    store = receipt["store"]
    total_paid = receipt["total_paid"]
    notes = receipt["notes"]
    print(f"Receipt # {receipt_number}:")
    print(f"    Store: {store.capitalize()}\n    Date: {date}\n    Total paid: ${total_paid:.2f}\n    Notes: {notes}")
    products = sorted(receipt["products"], key=lambda prod: prod["product"])
    for product_number, prod in enumerate(products, start=1):
        name = prod["product"]
        category = prod["category"]
        price = prod["unit_price"]
        paid = prod["paid_product"]
        print(f"    # {product_number} - Product: {name.capitalize()}")
        print(f"        Category: {category.capitalize()}\n        Unit_price: ${price:.2f}\n        Paid: ${paid:.2f}")


def delete_data_menu(data):
    """Ask whether to delete a complete receipt or one product, and run that option.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    Raises:
        Cancelled: If the user types a cancel word.
    """
    print("\n--Delete information--")
    while True:
        print(f"\nMenu:\n1. Delete complete receipt\n2. Delete a product info from a receipt")
        option = cli.read_int("Chose an option from menu: ", min_value=1)
        if not cli.value_in_options(option, 1, 2):
            print("Enter a valid number.")
            continue
        if option == 1:
            print("--Delete complete receipt--")
            if not data["receipts"]:
                print("There are not receipts to delete.")
                return
            info_by_filter = data_by_filter(data)
            delete_complete_receipt(info_by_filter, data)
        elif option == 2:
            print("--Delete a product--")
            receipt = choose_receipt(data["receipts"])
            if receipt is None:
                return
            delete_product(data, receipt)
        return


def purchase_for_period(data):
    """Ask for a date range and print every receipt inside it.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    Raises:
        Cancelled: If the user types a cancel word.
    """
    print("\n--Purchase for period--")
    min_date, max_date = _current_dates_period(data["receipts"])
    if min_date is None:
        print("There are not receipts")
        return
    print(f"Your receipts go to {min_date} - {max_date}")
    while True:
        start_date = cli.add_valid_date(prompt="Enter the first date: ")
        end_date = cli.add_valid_date(prompt="Enter the second date: ")
        if _is_period_ok(start_date, end_date):
            break
        print("The start date must be on or before the end date, try again...")
    by_period = queries.filter_by_period(data["receipts"], start_date, end_date)
    if by_period:
        print(f"\nIn this period you have {len(by_period)} receipts")
        for receipt_number, expense in enumerate(by_period, start=1):
            _print_receipt(expense, receipt_number)
            print()
        return
    else:
        print("There are not receipts on that period.\n")


def manage_expenses_menu(data):
    """Run the Delete/Purchase-for-period submenu until the user goes back.
    A cancel word at this menu returns to the main menu; a cancel word
    inside an option returns to this menu.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    """

    while True:
        print("Menu:\n1. Delete\n2. Purchase for period\n3. Go back to main menu")
        try:
            option = cli.read_int("Chose an option from menu: ", min_value=1)
        except cli.Cancelled:
            print()
            return

        if not cli.value_in_options(option, 1, 2, 3):
            print("Enter a valid number.")
            continue
        try:

            if option == 1:
                delete_data_menu(data)

            elif option == 2:
                purchase_for_period(data)

            else:
                print()
                break

        except cli.Cancelled:
            print("\nOperation cancelled by user.\n")
