import cli
import storage

from . import queries


def data_by_filter(data):
    """Ask the user for a filter and value, and return the matching receipts.
    Filters by store, exact date, product or category. Loops until at least
    one matching receipt is found.
    Args:
        data: The full data dict ({"receipts": [...]}).
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


def choose_receipt(receipts, prompt="Choose a receipt: "):
    """Print each candidate receipt and let the user pick one.
    Args:
        receipts: List of receipt dicts to choose from.
        prompt: Text shown above the numbered list.
    Returns:
        dict: The chosen receipt.
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

    while True:
        chose = cli.read_int(prompt=">>: ")
        if cli.value_in_options(chose, *range(1, len(receipts) + 1)):
            return sorted_receipts[chose - 1]
        print("Enter a valid option.")


def delete_expense(info_by_category, all_info):
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
    delete = choose_receipt(info_by_category, prompt="Enter the number of the data to delete: ")
    print(", ".join(f"{k}: {v}" for k, v in delete.items() if k != "products" and k != "receipt_id"))
    confirm = cli.yes_no_question("Delete this information?? (y/n): ")
    if confirm:
        for index, receipt in enumerate(all_info["receipts"]):
            if receipt["receipt_id"] == delete["receipt_id"]:
                del all_info["receipts"][index]
                break
        storage.save_json(all_info)
        print("Information deleted successfully")
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


def _current_dates_period(data):
    dates = [receipt["date"] for receipt in data]
    return (min(dates), max(dates)) if dates else (None, None)


def _print_receipt(receipt, receipt_number):
    date = receipt["date"]
    store = receipt["store"]
    total_paid = receipt["total_paid"]
    notes = receipt["notes"]
    print(f"Receipt # {receipt_number}:")
    print(f"    Store: {store.capitalize()}\n    Date: {date}\n    Total paid: ${total_paid}\n    Notes: {notes}")
    products = receipt["products"]
    for product_number, prod in enumerate(products, start=1):
        name = prod["product"]
        category = prod["category"]
        price = prod["unit_price"]
        paid = prod["paid_product"]
        print(f"    # {product_number} - Product: {name.capitalize()}")
        print(f"        Category: {category.capitalize()}\n        Unit_price: ${price}\n        Paid: ${paid}")


def manage_expenses(data):
    """Run the Delete/Purchase-for-period submenu until the user goes back.
    Args:
        data: The full data dict ({"receipts": [...]}).
    """

    while True:
        try:
            print("Menu:\n1. Delete\n2. Purchase for period\n3. Go back to main menu")
            option = cli.read_int("Chose an option from menu: ", min_value=1)

            if not cli.value_in_options(option, 1, 2, 3):
                print("Enter a valid number.")
                continue

            if option == 1:
                print("\n--Delete information--")
                # modify to delete all receipt
                info_by_filter = data_by_filter(data)
                delete_expense(info_by_filter, data)

            elif option == 2:
                print("\n--Purchase for period--")
                min_date, max_date = _current_dates_period(data["receipts"])
                if min_date is None:
                    print("There are not receipts")
                    continue
                print(f"Your receipts go to {min_date} - {max_date}")
                while True:
                    start_date = cli.add_valid_date(prompt="Enter the first date: ")
                    end_date = cli.add_valid_date(prompt="Enter the second date: ")
                    if _is_period_ok(start_date, end_date):
                        break
                    print("Enter a start date lower than a second date")
                by_period = queries.filter_by_period(data["receipts"], start_date, end_date)
                if by_period:
                    print(f"\nIn this period you have {len(by_period)} receipts")
                    for receipt_number, expense in enumerate(by_period, start=1):
                        _print_receipt(expense, receipt_number)
                        print()
                else:
                    print("There are not receipts on that period.\n")

            else:
                print()
                break

        except cli.Cancelled:
            print()


# delete by product
