import cli
import storage

from . import purchases, queries


def _chose_filter():
    """Ask the user which field to filter expenses by.

    Returns:
        str: One of "store", "date", "product", "category".

    Raises:
        Cancelled: If the user types a cancel word.
    """
    filters = {1: "store", 2: "date", 3: "product", 4: "category"}
    while True:
        print("Chose filter:\n1. Store\n2. Date\n3. Product\n4. Category")
        by_filter = cli.read_int(">>: ")
        if not cli.value_in_options(by_filter, 1, 2, 3, 4):
            print("Please choose 1, 2, 3 or 4.")
            continue
        return filters[by_filter]


def log(data):
    """Ask the user for a filter and value, and return the matching expenses.

    Loops until at least one matching expense is found.

    Args:
        data: The full data dict ({"expenses": [...], "receipts": [...]}).

    Returns:
        list: The expense dicts matching the chosen filter and value.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    print("Enter the filter and the date you want to search for: ")

    stores = queries.fields_names(data["expenses"], "store")
    products = queries.fields_names(data["expenses"], "product")
    categories = queries.fields_names(data["expenses"], "category")
    values_by_field = {"store": stores, "product": products, "category": categories}
    while True:
        filter_user = _chose_filter()

        if filter_user == "date":
            value = cli.add_valid_date()
        else:
            options = values_by_field[filter_user]
            if not options:
                print(f"No {filter_user} recorded yet.")
                continue
            value = cli.chose_from_list(options, f"Choose {filter_user}: ")

        results = queries.filter_by_field(data["expenses"], filter_user, value)
        if not results:
            print(f"No expenses found for that {filter_user}.")
            continue
        return results


def edit_expense(info_by_category, all_info):
    """Let the user pick one expense from a filtered list and edit it.

    Args:
        info_by_category: List of expense dicts to choose from (the result
            of log()).
        all_info: The full data dict; the matching expense is replaced in
            all_info["expenses"] and the change is saved to disk.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    existing = cli.chose_from_list(
        info_by_category, "Enter the number of the data to modify: "
    )
    print(", ".join(f"{k}: {v}" for k, v in existing.items()))
    updated = purchases.add_expense_fields(
        all_info, defaults=existing, ask_date_store=True
    )
    index = next(i for i, exp in enumerate(all_info["expenses"]) if exp is existing)
    all_info["expenses"][index] = updated

    storage.save_json(all_info)


def delete_expense(info_by_category, all_info):
    """Let the user pick one expense from a filtered list and delete it.

    Asks for confirmation before deleting.

    Args:
        info_by_category: List of expense dicts to choose from (the result
            of log()).
        all_info: The full data dict; the matching expense is removed from
            all_info["expenses"] and the change is saved to disk.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    delete = cli.chose_from_list(
        info_by_category, "Enter the number of the data to delete: "
    )
    print(", ".join(f"{k}: {v}" for k, v in delete.items()))
    confirm = cli.yes_no_question("Delete this information??")
    if confirm:
        index = next(i for i, exp in enumerate(all_info["expenses"]) if exp is delete)
        del all_info["expenses"][index]
        storage.save_json(all_info)
        print("Information deleted successfully")
    else:
        print("Operation canceled")


def _is_period_ok(start_date, end_date):
    """Check that a date range is valid (start on or before end).

    Args:
        start_date: Start of the period, as an ISO date string.
        end_date: End of the period, as an ISO date string.

    Returns:
        bool: True if start_date <= end_date.
    """
    return start_date <= end_date


def manage_expenses(data):
    """Run the Edit/Delete/Purchase-for-period submenu until the user goes back.

    Args:
        data: The full data dict ({"expenses": [...], "receipts": [...]}).

    Raises:
        Cancelled: If the user types a cancel word (currently propagates
            to the caller instead of returning to this submenu — see note
            above).
    """
    while True:
        print("1. Edit\n2. Delete\n3.Purchase for period\n4.Go back to main menu")
        option = cli.read_int("Chose an option from menu:", min_value=1)
        if not cli.value_in_options(option, 1, 2, 3, 4):
            print("Enter a valid number.")
            continue

        if option == 1:
            print("Edit information")
            info_by_filter = log(data)
            edit_expense(info_by_filter, data)
            print("Information modified succesfully")
        elif option == 2:
            info_by_filter = log(data)
            delete_expense(info_by_filter, data)
        elif option == 3:
            while True:
                start_date = cli.add_valid_date()
                end_date = cli.add_valid_date()
                if _is_period_ok(start_date, end_date):
                    break
            by_period = queries.filter_by_period(data["expenses"], start_date, end_date)
            for expense in by_period:
                print(", ".join(f"{k}: {v}" for k, v in expense.items()))
        else:
            break
