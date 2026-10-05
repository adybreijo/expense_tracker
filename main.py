import cli
import storage
import tracker
from tracker import queries


def main():
    """Load the stored data and run the main menu loop.
    Repeatedly shows the Add/Log/Expenses/Quit menu and dispatches to the
    matching tracker function until the user selects Quit or cancels.
    """
    data = storage.load_json({"receipts": [], "catalog": {}, "next_receipt_id": 1})
    if not isinstance(data, dict) or not all(key in data for key in ("receipts", "catalog")):
        print("Error: expenses.json doesn't match the expected format.")
        print("Fix or move the file and run the program again. Nothing was changed.")
        return
    if "next_receipt_id" not in data:
        data["next_receipt_id"] = queries.generate_id(data["receipts"], "receipt_id")
    while True:
        try:
            print("\nMenu:\n1. Add (Enter new receipts, modify information...)")
            print("2. Log (View or delete your receipts)")
            print("3. Expenses (Show your expenses)")
            print("4. Quit")
            option = cli.read_int(">>: ")
            print()
            valid_option = cli.value_in_options(option, 1, 2, 3, 4)
            if valid_option:
                if option == 1:
                    tracker.add_purchase_menu(data)
                elif option == 2:
                    tracker.manage_expenses_menu(data)
                elif option == 3:
                    tracker.expenses_by_filter(data)
                else:
                    print("Program finished")
                    break
            else:
                print("Enter a valid option")

        except (cli.Cancelled, KeyboardInterrupt, EOFError):
            print("Program finished")
            break


if __name__ == "__main__":
    main()
