import cli
import storage

from . import queries


def add_data(previous_data, prompt, field, default=None):
    """Let the user pick a previously used value for a field, or type a new one.
    Shows a numbered list of the distinct values already seen for `field`
    in `previous_data`, plus a "New entrance" option to type a value from
    scratch. If no previous values exist, skips straight to typing one.
    Args:
        previous_data: List of dicts (receipts or products) to collect
            existing values of `field` from.
        prompt: Text shown when asking the user to type a value (used both
            when no previous values exist, and after choosing "New entrance").
        field: Name of the field to collect existing values for (e.g.
            "store", "category", "product").
        default: Value pre-selected when the user presses Enter on the list,
            or pre-filled when typing.
    Returns:
        str: The chosen existing value, or the newly typed one.
    Raises:
        Cancelled: If the user types a cancel word.
    """

    fields = queries.fields_names(previous_data, field)

    if not fields:
        return cli.valid_string(prompt, default=default)

    options = ["New entrance"] + fields
    choice = cli.chose_from_list(options, prompt=f"Chose a {field}: ", default=default)
    print(f"{choice.capitalize()}")

    if choice == "New entrance":
        return cli.valid_string(prompt, default=default)
    return choice


def add_product_fields(known_products):
    """Prompt for the fields of a new product line.

    Args:
        known_products: List of product dicts (already saved, plus any
            added earlier in the current session) used to suggest
            previously used product names and categories.

    Returns:
        dict: The product with "product", "category", "unit_price" and
            "paid_product" filled in (no "product_id" yet).

    Raises:
        Cancelled: If the user types a cancel word.
    """
    product = add_data(known_products, "Product: ", "product")
    print()
    category = add_data(known_products, "Category: ", "category")
    print()
    unit_price = cli.read_float("Product price: ", min_value=0.01)
    print()
    paid_product = cli.read_float("How much you paid: ", min_value=0.01)

    return {
        "product": product,
        "category": category,
        "unit_price": unit_price,
        "paid_product": paid_product,
    }


def ask_fixed_data(source_list):
    """Prompt for the receipt-level fields of a new purchase.

    Args:
        source_list: List of receipt dicts used to suggest previously used
            store names.

    Returns:
        tuple: (date, store, total_paid, notes) for the receipt.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    date = cli.add_valid_date("Date [DD-MM-YYYY]: ")
    print()
    store = add_data(source_list, "Store: ", "store")
    print()
    total_paid = cli.read_float("Enter the total you paid: ", min_value=0.01)
    print()
    notes = cli.check_cancel(input("Notes: ")).strip()
    return date, store, total_paid, notes


def modify_fixed_data(fixed_data_info):
    """Let the user fix one or more receipt-level fields already entered.
    Shows the current values, then repeatedly asks which field to correct
    and its new value, until the user says there's nothing else to fix.
    Fields not chosen keep the value they came in with.

    Args:
        fixed_data_info: dict with the receipt's current "date", "store",
            "total_paid" and "notes".

    Returns:
        tuple: (date, store, total_paid, notes) with the corrections applied.

    Raises:
        Cancelled: If the user types a cancel word.
    """
    date, store, total_paid, notes = (
        fixed_data_info["date"],
        fixed_data_info["store"],
        fixed_data_info["total_paid"],
        fixed_data_info["notes"],
    )
    while True:
        print(
            f"Fields saved: \nDate: {date}\nStore: {store}\nTotal paid: ${total_paid}\nNotes: {notes}\n"
        )
        field = cli.chose_from_list(
            ("Date", "Store", "Total paid", "Notes"), "Which field you want to modify: "
        )
        if field == "Date":
            date = cli.add_valid_date("Enter a new date", default=date)
        elif field == "Store":
            store = cli.valid_string("Enter the new store name: ", default=store)
        elif field == "Total paid":
            total_paid = cli.read_float(
                ("Enter the new total paid: "), min_value=0.01, default=total_paid
            )
        else:
            notes = cli.check_cancel(input("Enter the new notes: ")).strip() or notes
        exit = cli.yes_no_question("Fix another field (y/n): ")
        if not exit:
            print(
                f"\nFinal data: \nDate: {date}\nStore: {store}\nTotal paid: ${total_paid}\nNotes: {notes}"
            )
            break
    return date, store, total_paid, notes


def modify_product(product_info):
    """Let the user fix one or more fields of a product just entered.

    Shows the current values, then repeatedly asks which field to correct
    and its new value, until the user says there's nothing else to fix.
    Fields not chosen keep the value they came in with.

    Args:
        product_info: dict with the product's current "product", "category",
            "unit_price" and "paid_product".

    Returns:
        dict: The product with "product", "category", "unit_price" 
            and "paid_product" filled in (no "product_id" yet).

    Raises:
        Cancelled: If the user types a cancel word.
    """

    product, category, unit_price, paid_product = (
        product_info["product"],
        product_info["category"],
        product_info["unit_price"],
        product_info["paid_product"],
    )

    while True:
        print(
            f"Fields saved: \nProduct: {product.capitalize()}\nCategory: {category.capitalize()}\nUnit price: ${unit_price}\nPaid: ${paid_product}"
        )
        field = cli.chose_from_list(
            ("Product", "Category", "Unit price", "Paid"),
            "Which field you want to modify",
        )
        if field == "Product":
            product = cli.valid_string("Enter the new product name: ", default=product)

        elif field == "Category":
            category = cli.valid_string(
                "Enter the new category name: ", default=category
            )

        elif field == "Unit price":
            unit_price = cli.read_float(
                ("Enter the new price for unit: "), min_value=0.01, default=unit_price
            )

        else:
            paid_product = cli.read_float(
                ("Enter the new total you paid for this product: "),
                min_value=0.01,
                default=paid_product,
            )

        exit = cli.yes_no_question("Fix another field (y/n): ")
        if not exit:
            print(
                f"\nFinal data: \nProduct: {product.capitalize()}\nCategory: {category.capitalize()}\nUnit price: ${unit_price}\nPaid: ${paid_product}"
            )
            break

    return {
        "product": product,
        "category": category,
        "unit_price": unit_price,
        "paid_product": paid_product,
    }


def add_complete_purchase(data):
    """Run the full "add a purchase" flow and persist the result.

    Asks for the receipt's date, store, total paid and notes once, with a
    chance to correct any of them before continuing. Then repeatedly asks
    for products (product, category, price, amount paid), each with its own
    chance to correct it before it's saved, until the user answers "no" to
    adding another, or cancels. Cancelling before any product is saved
    discards the purchase entirely; cancelling while entering or fixing a
    product still saves the receipt with the products already saved before
    it.

    Args:
        data: The full data dict ({"receipts": [...]}); the new receipt is
            appended to it and the result is saved to disk.
    """
    print("-- Add new expenses to your list or purchases --")
    print(
        f" [Type: *{', '.join(cli.CANCEL_WORDS)}'* at any time to cancel and return to the menu.]\n"
    )
    print("Please enter your purchase information as follows:")
    expenses = []

    try:
        receipt_id = queries.generate_id(data["receipts"], "receipt_id")
        date, store, total_paid, notes = ask_fixed_data(data["receipts"])
        print()
        modify = cli.chose_from_list(("Add product", "Modify data"), "Next step: ")
        if modify == "Modify data":
            print("\n-- Modify data--")
            defaults = {
                "date": date,
                "store": store,
                "total_paid": total_paid,
                "notes": notes,
            }
            date, store, total_paid, notes = modify_fixed_data(defaults)

        while True:
            print(f"\nProducts so far: {len(expenses)}")
            known_products = queries.only_products(data) + expenses
            new_expense = add_product_fields(known_products)
            while True:
                action = cli.yes_no_question("Fix product info (y/n): ")
                if action:
                    print("--Modify product--")
                    new_expense = modify_product(new_expense)
                else:
                    break
            new_expense["product_id"] = queries.generate_id(expenses, "product_id")
            expenses.append(new_expense)
            print(
                f" -- {new_expense['product'].capitalize()}  -{new_expense['category']} -${new_expense['paid_product']:.2f}"
            )
            new_product = cli.yes_no_question("Add more products (y/n): ")
            if not new_product:
                break
    except cli.Cancelled:
        print()

    if not expenses:
        print("Nothing was added")
        return
    receipt = {
        "receipt_id": receipt_id,
        "date": date,
        "store": store,
        "total_paid": total_paid,
        "notes": notes,
        "products": expenses,
    }

    data["receipts"].append(receipt)
    print(
        f"Receipt saved: {store.capitalize()}, {len(expenses)} product(s), total: ${total_paid:.2f}\n\n"
    )
    storage.save_json(data)
