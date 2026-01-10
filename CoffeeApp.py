class Coffee:

    # initialize coffee with name and price
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Order:
    # Initialize order with empty list
    def __init__(self):
        self.items = []

    # add coffee to order
    def add_item(self, coffee):
        self.items.append(coffee)
        print(f"Added {coffee.name} to order")

    # calculate total price of order
    def total(self):
        return sum(item.price for item in self.items)

    # show order summary
    def show_order(self):
        if not self.items:
            print("Your order is empty")
            return
        print("\nYour order:")

        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item.name} - ${item.price:.2f}")
        print(f"Total: ${self.total():.2f}\n")

    # handle check out process
    def checkout(self):
        if not self.items:
            print("Your order is empty")
            return
        self.show_order()

        confirm = input("Proceed to checkout? (y/n): ").strip().lower()

        if confirm == "y":
            print("Thank you! Your order has been placed.")
            self.items.clear()
        else:
            print("Order cancelled.")


# display menu and handle user input
def main():
    menu = [
        Coffee("Espresso", 2.99),
        Coffee("Latte", 2.49),
        Coffee("Cappuccino", 2.79),
        Coffee("Mocha", 4.99)
    ]

    order = Order()

    # User interaction
    while True:
        print("\nWhat would you like to drink?")
        for i, coffee in enumerate(menu, 1):
            print(f"{i}. {coffee.name} - ${coffee.price:.2f}")
        print("5. View Order")
        print("6. Checkout")
        print("7. Exit")

        try:
            choice = int(input("\nEnter your choice: "))

            if 1 <= choice <= 4:
                order.add_item(menu[choice - 1])
            elif choice == 5:
                order.show_order()
            elif choice == 6:
                order.checkout()
            elif choice == 7:
                print("Thank you for visiting! Goodbye.")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()