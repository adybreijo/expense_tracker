import cli
from . import log_info
from . import queries


def total_price(receipts):
    return sum(rec["total_paid"] for rec in receipts)


def stats_by_product(receipts):
    products = {}
    for receipt in receipts:
        for prod in receipt["products"]:
            name = prod["product"]
            if name not in products:
                products[name] = 0
            products[name] += prod["paid_product"]
    return sorted(products.items(), key=lambda pair: pair[1], reverse=True)


def stats_by_store(receipts):
    total_expense = total_price(receipts)
    expense_by_product = stats_by_product(receipts)
    return total_expense, expense_by_product


def print_info_by_store(store, receipts):
    total, products = stats_by_store(receipts)
    print(f"Total expenses in store {store.capitalize()}: ${total:.2f}")
    print("Products purchases: ")
    width = max(len(product) for product, _ in products)
    for product, expense in products:
        print(f"{product.capitalize():<{width}} -- ${expense:>7.2f}")


def main_store_filter(receipts):
    stores = queries.values_for_field(receipts, "store")
    store = cli.chose_from_list(stores)
    receipts_by_store = queries.receipts_by_field(receipts, "store", store)
    print_info_by_store(store, receipts_by_store)


def total_for_single_field(receipts, field, value):
    total = 0
    times = 0
    for prod in queries.only_products(receipts):
        if prod[field] == value:
            total += prod["paid_product"]
            times += 1
    return total, times


def print_total_for_field(receipts, field):
    all_fields = queries.values_for_field(receipts, field)
    value = cli.chose_from_list(all_fields)
    total, times = total_for_single_field(receipts, field, value)
    print(f"{value.capitalize()}, purchases {times} times: ${total:.2f}")


def main_products_filter(receipts):
    print_total_for_field(receipts, "product")


def main_category_filter(receipts):
    print_total_for_field(receipts, "category")


def get_notes(receipts):
    notes = queries.values_for_field(receipts, "notes")
    return [note for note in notes if note]


def main_notes(receipts):
    notes = get_notes(receipts)
    if not notes:
        print("There are no notes in this period")
        return
    note = cli.chose_from_list(notes)
    note_receipts = queries.receipts_by_field(receipts, "notes", note)
    total = total_price(note_receipts)
    print(f"Total expenses for note '{note}': ${total:.2f}")


def info_by_period(receipts_by_period):
    print("Choose the filter you want to use: ")
    while True:
        try:
            option = cli.valid_option("Menu:\n1. Store\n2. Product\n3. Category\n4. Notes\n5. Go back\n>>: ", 1, 2, 3, 4, 5)
        except cli.Cancelled:
            return

        try:
            if option == 1:
                print("-- Stores --")
                main_store_filter(receipts_by_period)

            elif option == 2:
                print("-- Products --")
                main_products_filter(receipts_by_period)

            elif option == 3:
                print("-- Category --")
                main_category_filter(receipts_by_period)

            elif option == 4:
                print("-- Notes --")
                main_notes(receipts_by_period)

            else:
                break
        except cli.Cancelled:
            print("\nOperation cancelled by user.\n")


def total_by_field(receipts, field, paid_filed):
    field_expense = {}
    for receipt in receipts:
        field_name = receipt[field]
        if field_name not in field_expense:
            field_expense[field_name] = 0
        field_expense[field_name] += receipt[paid_filed]
    return field_expense


def total_by_store(receipts):
    return total_by_field(receipts, "store", "total_paid")


def total_by_categories(receipts):
    products = queries.only_products(receipts)
    return total_by_field(products, "category", "paid_product")


def total_by_notes(receipts):
    notes_receipts = [receipt for receipt in receipts if receipt["notes"]]
    return total_by_field(notes_receipts, "notes", "total_paid")


def total_by_date(receipts):
    return total_by_field(receipts, "date", "total_paid")


def total_by_month(by_dates):
    year_month_data = {}
    for date, total in by_dates.items():
        year_month = date[:7]
        if year_month not in year_month_data:
            year_month_data[year_month] = 0
        year_month_data[year_month] += total
    return year_month_data


def total_by_product(receipts):
    products_dict = queries.only_products(receipts)
    prodcuts_total = total_by_field(products_dict, "product", "paid_product")
    return prodcuts_total


def category_product(receipts):
    products = queries.only_products(receipts)
    category_product_data = {}
    for receipt in products:
        category = receipt["category"]
        product = receipt["product"]
        if category not in category_product_data:
            category_product_data[category] = {}
        if product not in category_product_data[category]:
            category_product_data[category][product] = 0
        category_product_data[category][product] += receipt["paid_product"]
    return category_product_data


def print_category_product(data):
    print("-- Products by category --")
    for category, prod_price in data.items():
        print(f"{category.capitalize()}")
        width = max(len(field) for field in prod_price)
        sorted_prod_total = dict(sorted(prod_price.items(), key=lambda pair: pair[1], reverse=True))
        for product, total in sorted_prod_total.items():
            print(f"    {product.capitalize():<{width}}  ${total:>8.2f}")


def print_totals_by_dict(total_dict, string_text, sort_key=lambda pair: pair[1]):
    print(string_text)
    width = max(len(field) for field in total_dict)
    sorted_dict = dict(sorted(total_dict.items(), key=sort_key, reverse=True))
    for field, total in sorted_dict.items():
        print(f"    {field.capitalize():<{width}}  ${total:>8.2f}")


def all_expenses(receipts):

    min_date, max_date = queries.current_dates_period(receipts)
    total = total_price(receipts)  # total expent
    by_stores = total_by_store(receipts)  # total expent by store: {store: total...}
    by_categories = total_by_categories(receipts)  # total expent by category: {category: total...}
    by_notes = total_by_notes(receipts)  # total expent by note: {note: total...}
    by_dates = total_by_date(receipts)  # total expent by date: {date: total...}
    by_month = total_by_month(by_dates)
    by_product = total_by_product(receipts)
    by_category_product = category_product(receipts)

    print(f"Period of time: {min_date} -- {max_date}")
    print(f"Total in all expenses: ${total:.2f}")
    print_totals_by_dict(by_month, "-- Months --")
    print_totals_by_dict(by_dates, "-- Dates --", lambda pair: pair[0])
    print_totals_by_dict(by_stores, "-- Stores --")
    print_totals_by_dict(by_categories, "-- Categories --")
    print_totals_by_dict(by_product, "-- Products --")
    print_category_product(by_category_product)
    if by_notes:
        print_totals_by_dict(by_notes, "-- Notes --")
    else:
        print("There are no notes")
    print()


def expenses_by_filter(data):
    """Ask for a time period and show the expenses inside it.
    A cancel word at this menu or inside an option returns to the main menu.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    """
    print("--Expenses--")
    while True:
        try:
            option = cli.valid_option(
                "Choose the time period you want to use: \n1. By period\n2. All expenses\n3. Go back to menu\n>>: ", 1, 2, 3
            )
        except cli.Cancelled:
            return
        try:
            if option == 1:
                by_period = log_info.purchase_for_period(data)
                if not by_period:
                    print(f"There are no receipts in this time period")
                    continue
                info_by_period(by_period)
            elif option == 2:
                if not data["receipts"]:
                    print(f"There are no receipts in this time period")
                    continue
                all_expenses(data["receipts"])

            else:
                break
        except cli.Cancelled:
            print("\nOperation cancelled by user.\n")
