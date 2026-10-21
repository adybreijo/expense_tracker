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
    if not products:
        print("There are no products in this store")
        return
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


def stats_product_filter(receipts, product):
    total = 0
    for receipt in receipts:
        for prod in receipt["products"]:
            if prod["product"] == product:
                total += prod["paid_product"]
    return total


def main_products_filter(receipts):
    products = queries.values_for_field(receipts, "product")
    if not products:
        print(f"There are no receipts in this time period")
        return
    product = cli.chose_from_list(products)
    stats = stats_product_filter(receipts, product)
    print(f"{product.capitalize()}: ${stats:.2f}")


def main_category_filter(receipts):
    pass


def info_by_period(receipts_by_period):
    print("Choose the filter you wan to use: ")
    while True:
        try:
            option = cli.valid_option("Menu:\n1. Store\n2. Product\n3. Category\n4. Notes\n5. Go back\n>>:", 1, 2, 3, 4, 5)
        except cli.Cancelled:
            return

        try:
            if option == 1:
                print("-- Stores --")
                main_store_filter(receipts_by_period)

            elif option == 2:
                print("-- Products --")
                main_products_filter(receipts_by_period)

                pass
            elif option == 3:
                pass
            elif option == 4:
                pass
            else:
                break
        except cli.Cancelled:
            print("\nOperation cancelled by user.\n")


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
                # should print: 1. total expent, 2. top 3 more buyed products and its costs, 3. the same but for category
                print("not implemented")
            else:
                break
        except cli.Cancelled:
            print("\nOperation cancelled by user.\n")


# see total paid
# see total paid by notes, by category, by product, by store
# see total of times purshed each prodcut
# see more detailed info
