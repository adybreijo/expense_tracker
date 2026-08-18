import helpers
import tracker

def main():
    """Run the main menu loop, handling Add/Log/Quit until the user exits or cancels."""
    while True:
        try:
            print("Menu:\n1. Add\n2. Log\n3. Quit")
            option = helpers.read_int('Enter your choice: ')
            valid_option = helpers.value_in_options(option,1,2,3)
            if valid_option:
                if option == 1:
                    tracker.add_complete_purchase()
                elif option == 2:
                    tracker.log()
                else:
                    print('Program finished')
                    break
            else:
                print("Enter a valid option")
        except helpers.Cancelled:
            print('Program finished')
            break

if __name__ == '__main__': 
    main()



