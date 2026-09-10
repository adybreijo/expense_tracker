import cli
import storage

from . import queries


def add_data(previous_data, prompt, field, default=None):
    """Let the user reuse a previously entered value or type a new one.

    Args:
        previous_data: List of expense dicts to collect existing values from.
        prompt: Text shown when no previous values exist and the user must
            type one from scratch.
        field: Name of the field to collect existing values for (e.g.
            "store", "category").
        default: Value pre-selected/pre-filled when the user presses Enter.

    Returns:
        str: The chosen or typed value.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    fields = queries.fields_names(previous_data, field)  

    if not fields:
        return cli.valid_string(prompt, default=default)

    options = ["New entrance"] + fields
    print(f'-- {field.capitalize()}--')
    choice = cli.chose_from_list(options, default=default)

    if choice == "New entrance":
        return cli.valid_string(prompt, default=default)
    return choice


def add_expense_fields(known_products, defaults=None):
    """Prompt for the fields of a single expense.

    Works for both adding a new expense and editing an existing one: any
    field present in defaults is offered back to the user as the value to
    keep by pressing Enter.

    Args:
        data: The full data dict ({"expenses": [...], "receipts": [...]}),
            used to look up previously entered stores/categories.
        defaults: Existing expense dict to pre-fill values from, or None
            when adding a brand-new expense.
        ask_date_store: If True, also prompt for "date" and "store" (used
            when editing a single expense). If False, those two fields are
            taken from defaults without asking again (used when adding
            several items to the same purchase/receipt).

    Returns:
        dict: The expense with all fields (date, store, product, category,
            price, paid, quantity, unit, notes) filled in.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    defaults = defaults or {}

    product = add_data(known_products, "Product: ", "product", defaults.get("product"))
    category = add_data(known_products, "Category: ", "category", defaults.get("category"))
    unit_price = cli.read_float(
        "Product price: ", min_value=0.01, default=defaults.get("unit_price")
    )
    total_paid = cli.read_float(
        "How much you paid: ", min_value=0.01, default=defaults.get("total_paid")
    )
    
    return {
        **defaults,
        "product": product,
        "category": category,
        "unit_price": unit_price,
        "total_paid": total_paid
    }

def ask_fix_data(source_list,defaults= None):
    defaults = defaults or {}
    date = cli.add_valid_date("Date [YYYY-MM-DD]: ", default=defaults.get("date"))
    store = add_data(source_list, "Store: ", "store", defaults.get("store"))
    total_paid = cli.read_float("Enter the total you paid: ", min_value=0.01,default=defaults.get("total_paid"))
    notes = cli.check_cancel(input("Notes: ")).strip() or defaults.get("notes", "")
    return date, store,total_paid,notes


def add_complete_purchase(data):
    """Run the full "add a purchase" flow and persist the result.
    Asks for the purchase date, store and total paid once, then repeatedly
    asks for expense items (product, category, price, etc.) until the user
    cancels. Cancelling with no items entered discards the purchase
    entirely; otherwise the new expenses and the receipt are appended to
    data and saved to disk.

    Args:
        data: The full data dict ({"receipts": [...]})
            to append the new purchase to.
    """
    print("-- Add new expenses to your list or purchases --")
    print(
        f" [Type: *{', '.join(cli.CANCEL_WORDS)}'* at any time to cancel and return to the menu.]\n"
    )
    print("Please enter your purchase information as follows:")
    expenses = []

    try:
        receipt_id = queries.generate_id(data["receipts"], "receipt_id")
        date,store,total_paid,notes = ask_fix_data(data["receipts"])

        while True:
            known_products = queries.only_products(data) + expenses
            new_expense = add_expense_fields(known_products)
            new_expense['product_id'] = queries.generate_id(expenses, "product_id")
            expenses.append(new_expense)
            print(f" -- {new_expense['product'].capitalize()}  -{new_expense['category']} -${new_expense['total_paid']:.2f}")
            add_another  = cli.yes_no_question('Add more products: ')
            if not add_another :
                break
    except cli.Cancelled:
        print()

    if not expenses:
        print("Nothing was added")
        return
    receipt = {'receipt_id': receipt_id, 'date': date, 'store':store,'total_paid': total_paid, 'notes': notes, 'products':expenses}

    data["receipts"].append(receipt)
    print(f"Receipt saved: {store.capitalize()}, {len(expenses)} product(s), total: ${total_paid:.2f}")
    storage.save_json(data)
