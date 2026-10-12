import cli
from . import log_info
from . import queries


def info_by_categories(receipts_by_period):
    print("Choose the filter you wan to use: ")
    option = cli.valid_option("Menu:\n1. Store\n2. Product\n3. Category\n4. Notes\n>>:", 1, 2, 3, 4)
    if option == 1:
        print("-- Stores --")
        store = queries.values_for_field(receipts_by_period, "store")
        pass
    elif option == 2:
        pass
    elif option == 3:
        pass
    elif option == 4:
        pass
    return


def expenses_by_filter(data):
    """Ask for a time period and show the expenses inside it.
    A cancel word at this menu or inside an option returns to the main menu.
    Args:
        data: The full data dict ({"receipts": [], "catalog": {}, "next_receipt_id": 1}).
    """
    print("--Expenses--")
    try:
        option = cli.valid_option("Choose the time period you want to use: \n1. By period\n2. All expenses\n>>: ", 1, 2)
        if option == 1:
            by_period = log_info.purchase_for_period(data)
            info_by_categories(by_period)
        elif option == 2:
            print("not implemented")
    except cli.Cancelled:
        print("\nOperation cancelled by user.\n")


def total(expenses):
    pass


#  add new index to menu to see a complete info data: total purchases, stores, dates, categories,....
# see total paid
# see total paid by notes, by category, by product, by store
# see total of times purshed each prodcut
# see more detailed info
