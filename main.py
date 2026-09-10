import cli
import storage
import tracker


def main():
    """Load the stored data and run the main menu loop.
    Repeatedly shows the Add/Log/Expenses/Quit menu and dispatches to the
    matching tracker function until the user selects Quit or cancels.
    """
    data = storage.load_json({"receipts": []})
    if "receipts" not in data:
        data = {"receipts": []}
    while True:
        try:
            print(
                "Menu:\n1. Add (enter new purchase)\n2. Log (modify or delete your data)\n3. Expenses (show your expenses)\n4. Quit"
            )
            option = cli.read_int("Enter your choice: ")
            valid_option = cli.value_in_options(option, 1, 2, 3, 4)
            if valid_option:
                if option == 1:
                    tracker.add_complete_purchase(data)
                elif option == 2:
                    tracker.manage_expenses(data)
                elif option == 3:
                    tracker.expenses_by_filter(data)
                else:
                    print("Program finished")
                    break
            else:
                print("Enter a valid option")
        except cli.Cancelled:
            print("Program finished")
            break


if __name__ == "__main__":
    main()
