import cli
import storage
import tracker


def main():
    """Load the stored data and run the main menu loop.
    Repeatedly shows the Add/Log/Expenses/Quit menu and dispatches to the
    matching tracker function until the user selects Quit or cancels.
    """
    data = storage.load_json({"receipts": []})
    if not isinstance(data, dict) or "receipts" not in data:
        print(
            "Warning: expenses.json doesn't match the expected format, starting empty."
        )
        data = {"receipts": []}
    while True:
        try:
            print(
                "Menu:\n1. Add (enter new purchase)\n2. Log (Delete and view your data)\n3. Expenses (show your expenses)\n4. Quit"
            )
            option = cli.read_int("Enter your choice: ")
            print()
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
