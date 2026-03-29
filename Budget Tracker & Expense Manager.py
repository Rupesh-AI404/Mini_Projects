"""
Budget Tracker & Expense Manager
Concepts covered:
- JSON file handling
- Data validation
- Sorting & filtering
- Date manipulation
- Category analysis
- Budget calculations
- Export functionality
"""
import json
import os
from datetime import datetime, timedelta
import calendar

# File to store expenses
EXPENSES_FILE = "expenses.json"
BUDGET_FILE = "budget.json"


class Expense:
    """Individual expense class"""

    def __init__(self, amount, category, description, date=None):
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date if date else datetime.now().strftime('%Y-%m-%d')
        self.id = None

    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data):
        """Create expense from dictionary"""
        expense = cls(data['amount'], data['category'], data['description'], data['date'])
        expense.id = data['id']
        return expense


class BudgetTracker:
    """Main budget tracking application"""

    def __init__(self):
        self.expenses = []
        self.budget = {}
        self.load_data()
        self.categories = [
            "🍔 Food & Dining",
            "🚗 Transportation",
            "🏠 Rent & Utilities",
            "🛍️ Shopping",
            "🎬 Entertainment",
            "💊 Healthcare",
            "📚 Education",
            "✈️ Travel",
            "💼 Insurance",
            "📱 Subscriptions",
            "🎁 Gifts & Donations",
            "💰 Savings",
            "📝 Other"
        ]

    def load_data(self):
        """Load expenses and budget from files"""
        # Load expenses
        if os.path.exists(EXPENSES_FILE):
            try:
                with open(EXPENSES_FILE, 'r') as f:
                    data = json.load(f)
                    self.expenses = [Expense.from_dict(exp) for exp in data]
            except:
                self.expenses = []
        else:
            self.expenses = []

        # Load budget
        if os.path.exists(BUDGET_FILE):
            try:
                with open(BUDGET_FILE, 'r') as f:
                    self.budget = json.load(f)
            except:
                self.budget = {}
        else:
            self.budget = {}

        # Assign IDs if missing
        for i, expense in enumerate(self.expenses):
            if expense.id is None:
                expense.id = i + 1

    def save_data(self):
        """Save expenses and budget to files"""
        try:
            # Save expenses
            with open(EXPENSES_FILE, 'w') as f:
                json.dump([exp.to_dict() for exp in self.expenses], f, indent=4)

            # Save budget
            with open(BUDGET_FILE, 'w') as f:
                json.dump(self.budget, f, indent=4)

            return True
        except:
            return False

    def add_expense(self):
        """Add a new expense"""
        print("\n💰 ADD NEW EXPENSE")
        print("-" * 30)

        # Get amount
        while True:
            try:
                amount = float(input("Amount (₹): "))
                if amount > 0:
                    break
                print("Amount must be positive!")
            except ValueError:
                print("Please enter a valid number!")

        # Get category
        print("\nCategories:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category}")

        while True:
            try:
                cat_choice = int(input("\nChoose category (1-13): "))
                if 1 <= cat_choice <= len(self.categories):
                    category = self.categories[cat_choice - 1]
                    break
                print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")

        # Get description
        description = input("Description: ").strip()
        if not description:
            description = "No description"

        # Get date
        date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if date_input:
            try:
                datetime.strptime(date_input, '%Y-%m-%d')
                date = date_input
            except:
                print("Invalid date! Using today's date.")
                date = datetime.now().strftime('%Y-%m-%d')
        else:
            date = datetime.now().strftime('%Y-%m-%d')

        # Create expense
        expense = Expense(amount, category, description, date)
        expense.id = len(self.expenses) + 1
        self.expenses.append(expense)
        self.save_data()

        print(f"\n✅ Expense added: ₹{amount:.2f} for {category[2:]}")

    def view_expenses(self, filter_by=None):
        """View expenses with optional filtering"""
        if not self.expenses:
            print("\n📭 No expenses recorded yet!")
            return

        filtered = self.expenses.copy()

        # Apply filters
        if filter_by == 'month':
            current_month = datetime.now().strftime('%Y-%m')
            filtered = [e for e in filtered if e.date.startswith(current_month)]
            title = "THIS MONTH"
        elif filter_by == 'week':
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            filtered = [e for e in filtered if e.date >= week_ago]
            title = "LAST 7 DAYS"
        elif filter_by and filter_by.startswith('category:'):
            category = filter_by.split(':')[1]
            filtered = [e for e in filtered if e.category == category]
            title = f"CATEGORY: {category[2:]}"
        else:
            title = "ALL EXPENSES"

        if not filtered:
            print(f"\n📭 No expenses found for {title}")
            return

        # Sort by date (newest first)
        filtered.sort(key=lambda x: x.date, reverse=True)

        print(f"\n📋 {title}")
        print("=" * 70)

        total = 0
        for expense in filtered:
            total += expense.amount
            date_obj = datetime.strptime(expense.date, '%Y-%m-%d')
            print(f"\n[{expense.id}] {date_obj.strftime('%b %d, %Y')}")
            print(f"   {expense.category}")
            print(f"   ₹{expense.amount:.2f}")
            print(f"   📝 {expense.description}")

        print("\n" + "=" * 70)
        print(f"📊 TOTAL: ₹{total:.2f}")
        print(f"📊 COUNT: {len(filtered)} expenses")

    def view_by_category(self):
        """View expenses grouped by category"""
        if not self.expenses:
            print("\n📭 No expenses recorded yet!")
            return

        # Group by category
        category_totals = {}
        for expense in self.expenses:
            category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount

        print("\n📊 EXPENSES BY CATEGORY")
        print("=" * 50)

        total = sum(category_totals.values())

        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100 if total > 0 else 0
            bar_length = int(percentage / 2)  # 50 chars max
            bar = '█' * bar_length + '░' * (50 - bar_length)
            print(f"\n{category}")
            print(f"   ₹{amount:.2f} ({percentage:.1f}%)")
            print(f"   {bar}")

        print("\n" + "=" * 50)
        print(f"📊 GRAND TOTAL: ₹{total:.2f}")

    def set_budget(self):
        """Set monthly budget for categories"""
        print("\n🎯 SET MONTHLY BUDGET")
        print("-" * 50)

        month = input("Month (YYYY-MM, press Enter for current month): ").strip()
        if not month:
            month = datetime.now().strftime('%Y-%m')

        if month not in self.budget:
            self.budget[month] = {}

        print(f"\nSetting budget for {month}")
        print("(Enter 0 or leave blank to skip a category)")

        total_budget = 0

        for category in self.categories:
            current = self.budget[month].get(category, 0)
            prompt = f"{category} [current: ₹{current:.2f}]: "
            value = input(prompt).strip()

            if value:
                try:
                    budget_amt = float(value)
                    if budget_amt > 0:
                        self.budget[month][category] = budget_amt
                        total_budget += budget_amt
                    elif budget_amt == 0 and category in self.budget[month]:
                        del self.budget[month][category]
                except ValueError:
                    print("Invalid number! Skipping...")

        self.save_data()
        print(f"\n✅ Budget set for {month}!")
        print(f"📊 Total monthly budget: ₹{total_budget:.2f}")

    def check_budget(self):
        """Check budget vs actual spending"""
        if not self.budget:
            print("\n📭 No budget set! Use option 5 to set a budget first.")
            return

        month = input("\nMonth (YYYY-MM, press Enter for current month): ").strip()
        if not month:
            month = datetime.now().strftime('%Y-%m')

        if month not in self.budget:
            print(f"\n📭 No budget found for {month}")
            return

        # Calculate actual spending for the month
        actual_spending = {}
        for expense in self.expenses:
            if expense.date.startswith(month):
                actual_spending[expense.category] = actual_spending.get(expense.category, 0) + expense.amount

        print(f"\n📊 BUDGET REPORT - {month}")
        print("=" * 60)

        total_budget = 0
        total_actual = 0
        over_budget = []

        for category, budget_amt in self.budget[month].items():
            actual = actual_spending.get(category, 0)
            total_budget += budget_amt
            total_actual += actual

            difference = budget_amt - actual
            status = "✅" if difference >= 0 else "⚠️"

            print(f"\n{status} {category}")
            print(f"   Budget: ₹{budget_amt:.2f}")
            print(f"   Spent:  ₹{actual:.2f}")
            print(f"   Left:   ₹{difference:.2f}")

            if difference < 0:
                over_budget.append((category, abs(difference)))

        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print(f"Total Budget: ₹{total_budget:.2f}")
        print(f"Total Spent:  ₹{total_actual:.2f}")
        print(f"Remaining:    ₹{total_budget - total_actual:.2f}")

        if over_budget:
            print("\n⚠️ OVER BUDGET CATEGORIES:")
            for category, amount in over_budget:
                print(f"   {category}: ₹{amount:.2f} over")

        # Calculate if overall under/over budget
        if total_actual > total_budget:
            print(f"\n⚠️ You're ₹{total_actual - total_budget:.2f} OVER your total budget!")
        else:
            print(f"\n✅ You're ₹{total_budget - total_actual:.2f} UNDER your total budget!")

    def monthly_report(self):
        """Generate monthly expense report"""
        if not self.expenses:
            print("\n📭 No expenses recorded yet!")
            return

        year = input("\nYear (YYYY, press Enter for current): ").strip()
        if not year:
            year = datetime.now().strftime('%Y')

        month = input("Month (1-12, press Enter for all months): ").strip()

        print(f"\n📊 EXPENSE REPORT - {year}" + (f" {calendar.month_name[int(month)]}" if month else ""))
        print("=" * 60)

        monthly_totals = {}
        category_yearly = {}

        for expense in self.expenses:
            exp_year = expense.date[:4]
            if exp_year != year:
                continue

            if month:
                exp_month = expense.date[5:7]
                if exp_month != month.zfill(2):
                    continue

            # Monthly totals
            month_key = expense.date[5:7]
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + expense.amount

            # Category totals
            category_yearly[expense.category] = category_yearly.get(expense.category, 0) + expense.amount

        if not monthly_totals:
            print(f"No expenses found for {year}" + (f" {calendar.month_name[int(month)]}" if month else ""))
            return

        # Display monthly breakdown
        if month:
            total = monthly_totals[month.zfill(2)]
            print(f"\n📅 {calendar.month_name[int(month)]} {year}")
            print(f"   Total: ₹{total:.2f}")
        else:
            print("\n📅 MONTHLY BREAKDOWN:")
            for m in sorted(monthly_totals.keys()):
                month_name = calendar.month_name[int(m)]
                total = monthly_totals[m]
                print(f"   {month_name}: ₹{total:.2f}")

            yearly_total = sum(monthly_totals.values())
            print(f"\n📊 YEARLY TOTAL: ₹{yearly_total:.2f}")
            print(f"📊 MONTHLY AVERAGE: ₹{yearly_total / 12:.2f}")

        # Display top categories
        print("\n📂 TOP CATEGORIES:")
        for category, amount in sorted(category_yearly.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {category}: ₹{amount:.2f}")

    def delete_expense(self):
        """Delete an expense"""
        self.view_expenses()

        if not self.expenses:
            return

        try:
            exp_id = int(input("\n🗑️ Enter expense ID to delete (0 to cancel): "))
            if exp_id == 0:
                return

            expense = next((e for e in self.expenses if e.id == exp_id), None)
            if expense:
                confirm = input(f"Delete expense: ₹{expense.amount:.2f} for {expense.category[2:]}? (y/n): ")
                if confirm.lower() == 'y':
                    self.expenses.remove(expense)
                    # Reassign IDs
                    for i, e in enumerate(self.expenses, 1):
                        e.id = i
                    self.save_data()
                    print("✅ Expense deleted!")
            else:
                print("❌ Expense not found!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def edit_expense(self):
        """Edit an existing expense"""
        self.view_expenses()

        if not self.expenses:
            return

        try:
            exp_id = int(input("\n✏️ Enter expense ID to edit (0 to cancel): "))
            if exp_id == 0:
                return

            expense = next((e for e in self.expenses if e.id == exp_id), None)
            if expense:
                print(f"\nEditing expense #{exp_id}")
                print("(Press Enter to keep current value)")

                # Edit amount
                new_amount = input(f"Amount [₹{expense.amount:.2f}]: ").strip()
                if new_amount:
                    try:
                        expense.amount = float(new_amount)
                    except ValueError:
                        print("Invalid amount! Keeping current.")

                # Edit category
                print("\nCategories:")
                for i, cat in enumerate(self.categories, 1):
                    current_marker = " ✓" if cat == expense.category else ""
                    print(f"{i}. {cat}{current_marker}")

                cat_choice = input(f"\nCategory (1-13): ").strip()
                if cat_choice and cat_choice.isdigit():
                    idx = int(cat_choice) - 1
                    if 0 <= idx < len(self.categories):
                        expense.category = self.categories[idx]

                # Edit description
                new_desc = input(f"Description [{expense.description}]: ").strip()
                if new_desc:
                    expense.description = new_desc

                # Edit date
                new_date = input(f"Date [{expense.date}]: ").strip()
                if new_date:
                    try:
                        datetime.strptime(new_date, '%Y-%m-%d')
                        expense.date = new_date
                    except:
                        print("Invalid date format! Keeping current.")

                self.save_data()
                print("✅ Expense updated!")
            else:
                print("❌ Expense not found!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def savings_goal(self):
        """Track savings goals"""
        print("\n💰 SAVINGS GOAL TRACKER")
        print("-" * 30)

        goal_name = input("Goal name (e.g., Vacation, New Laptop): ").strip()
        if not goal_name:
            print("Goal name cannot be empty!")
            return

        try:
            target_amount = float(input("Target amount (₹): "))
            if target_amount <= 0:
                print("Target must be positive!")
                return
        except ValueError:
            print("Invalid amount!")
            return

        # Calculate current savings (from savings category)
        saved_so_far = sum(e.amount for e in self.expenses
                           if e.category == "💰 Savings")

        remaining = target_amount - saved_so_far

        print(f"\n🎯 GOAL: {goal_name}")
        print(f"Target: ₹{target_amount:.2f}")
        print(f"Saved:  ₹{saved_so_far:.2f}")
        print(f"Remaining: ₹{remaining:.2f}")

        if remaining <= 0:
            print("\n🎉 CONGRATULATIONS! You've reached your goal! 🎉")
        else:
            # Estimate time to reach goal
            avg_monthly_savings = 0
            # Get last 3 months of savings
            recent_savings = []
            current_month = datetime.now().strftime('%Y-%m')
            for i in range(3):
                month = (datetime.now() - timedelta(days=30 * i)).strftime('%Y-%m')
                monthly_savings = sum(e.amount for e in self.expenses
                                      if e.category == "💰 Savings" and e.date.startswith(month))
                recent_savings.append(monthly_savings)

            if recent_savings:
                avg_monthly_savings = sum(recent_savings) / len(recent_savings)

            if avg_monthly_savings > 0:
                months_needed = remaining / avg_monthly_savings
                print(f"\nAt current savings rate (₹{avg_monthly_savings:.2f}/month):")
                print(f"Estimated time: {months_needed:.1f} months")
            else:
                print("\nStart saving! Add expenses in the '💰 Savings' category.")

    def export_data(self):
        """Export expenses to CSV"""
        if not self.expenses:
            print("\n📭 No data to export!")
            return

        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ID,Date,Category,Amount,Description\n")
                for expense in self.expenses:
                    f.write(
                        f"{expense.id},{expense.date},{expense.category[2:]},{expense.amount:.2f},{expense.description}\n")

            print(f"✅ Data exported to: {filename}")
        except Exception as e:
            print(f"❌ Error exporting: {e}")


def main():
    """Main program loop"""
    print("\n" + "=" * 50)
    print("💰 BUDGET TRACKER & EXPENSE MANAGER")
    print("Take control of your finances")
    print("=" * 50)

    tracker = BudgetTracker()

    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 💰 Add Expense")
        print("2. 📋 View All Expenses")
        print("3. 📊 View by Category")
        print("4. 📅 View This Month")
        print("5. 🎯 Set Monthly Budget")
        print("6. 📈 Check Budget vs Spending")
        print("7. 📑 Monthly Report")
        print("8. ✏️ Edit Expense")
        print("9. 🗑️ Delete Expense")
        print("10. 🎯 Savings Goal Tracker")
        print("11. 📤 Export Data")
        print("12. 🚪 Exit")
        print("=" * 40)

        choice = input("\nYour choice (1-12): ").strip()

        if choice == '1':
            tracker.add_expense()
        elif choice == '2':
            tracker.view_expenses()
        elif choice == '3':
            tracker.view_by_category()
        elif choice == '4':
            tracker.view_expenses('month')
        elif choice == '5':
            tracker.set_budget()
        elif choice == '6':
            tracker.check_budget()
        elif choice == '7':
            tracker.monthly_report()
        elif choice == '8':
            tracker.edit_expense()
        elif choice == '9':
            tracker.delete_expense()
        elif choice == '10':
            tracker.savings_goal()
        elif choice == '11':
            tracker.export_data()
        elif choice == '12':
            print("\n👋 Goodbye! Stay financially smart! 💰")
            break
        else:
            print("❌ Invalid choice!")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")