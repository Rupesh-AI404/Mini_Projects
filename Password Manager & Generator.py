"""
Password Manager & Generator - Fixed Version
Works reliably on Windows, Mac, and Linux
"""

import os
import csv
import random
import string
import hashlib
import sys
from datetime import datetime

# File to store passwords
PASSWORD_FILE = "passwords.csv"
MASTER_PASSWORD_FILE = "master.hash"

class PasswordManager:
    """A simple password manager"""

    def __init__(self):
        self.is_logged_in = False
        self.passwords = []

    def input_password(self, prompt):
        """Cross-platform password input"""
        try:
            # Try getpass first (works in most terminals)
            import getpass
            return getpass.getpass(prompt)
        except:
            # Fallback to regular input (password will be visible)
            print(prompt, end='', flush=True)
            return input()

    def create_master_password(self):
        """Create master password for first-time setup"""
        print("\n🔐 FIRST TIME SETUP")
        print("=" * 30)

        while True:
            password = self.input_password("Create master password: ")

            if len(password) < 4:
                print("❌ Password must be at least 4 characters!")
                continue

            confirm = self.input_password("Confirm master password: ")

            if password == confirm:
                # Hash the password
                hashed = hashlib.sha256(password.encode()).hexdigest()

                with open(MASTER_PASSWORD_FILE, 'w') as f:
                    f.write(hashed)

                print("✅ Master password created successfully!")
                return True
            else:
                print("❌ Passwords don't match!")

    def verify_master_password(self):
        """Verify master password during login"""
        if not os.path.exists(MASTER_PASSWORD_FILE):
            return self.create_master_password()

        attempts = 3
        while attempts > 0:
            password = self.input_password("Enter master password: ")
            hashed = hashlib.sha256(password.encode()).hexdigest()

            with open(MASTER_PASSWORD_FILE, 'r') as f:
                stored_hash = f.read().strip()

            if hashed == stored_hash:
                self.is_logged_in = True
                self.load_passwords()
                print("✅ Login successful!")
                return True
            else:
                attempts -= 1
                if attempts > 0:
                    print(f"❌ Wrong password! {attempts} attempts remaining.")
                else:
                    print("❌ Wrong password! No attempts left.")

        print("🔒 Too many failed attempts. Exiting.")
        return False

    def generate_password(self, length=12, use_symbols=True):
        """Generate a strong random password"""
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_symbols else ""

        # Ensure at least one of each type
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits)
        ]

        if use_symbols:
            password.append(random.choice(symbols))

        # Fill the rest
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - len(password)):
            password.append(random.choice(all_chars))

        random.shuffle(password)
        return ''.join(password)

    def add_password(self):
        """Add a new password entry"""
        print("\n➕ ADD NEW PASSWORD")
        print("-" * 30)

        service = input("Service name (e.g., Gmail, Facebook): ").strip()
        if not service:
            print("❌ Service name cannot be empty!")
            return

        username = input("Username/Email: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            return

        # Password options
        print("\nPassword options:")
        print("1. Generate strong password")
        print("2. Enter my own password")

        choice = input("Choose (1/2): ").strip()

        if choice == '1':
            length_input = input("Password length (default 12): ").strip()
            length = int(length_input) if length_input.isdigit() else 12
            use_symbols = input("Include symbols? (y/n, default y): ").strip().lower() != 'n'
            password = self.generate_password(length, use_symbols)
            print(f"\n🔑 Generated password: {password}")
        else:
            password = self.input_password("Enter password: ")

        notes = input("Notes (optional): ").strip()

        entry = {
            'service': service,
            'username': username,
            'password': password,
            'notes': notes,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.passwords.append(entry)
        self.save_passwords()
        print(f"✅ Password for '{service}' saved successfully!")

    def view_passwords(self):
        """View all saved passwords"""
        if not self.passwords:
            print("\n📭 No passwords saved yet!")
            return

        print("\n📋 YOUR SAVED PASSWORDS")
        print("=" * 60)

        for idx, entry in enumerate(self.passwords, 1):
            print(f"\n{idx}. {entry['service']}")
            print(f"   Username: {entry['username']}")
            print(f"   Password: {entry['password']}")
            if entry.get('notes'):
                print(f"   Notes: {entry['notes']}")
            print(f"   Created: {entry['created']}")

        print("\n" + "=" * 60)
        print(f"Total entries: {len(self.passwords)}")

    def search_password(self):
        """Search for a specific service"""
        if not self.passwords:
            print("\n📭 No passwords saved yet!")
            return

        search_term = input("\n🔍 Search for service: ").strip().lower()

        results = []
        for entry in self.passwords:
            if search_term in entry['service'].lower():
                results.append(entry)

        if results:
            print(f"\n📖 Found {len(results)} matching entry(s):")
            print("-" * 40)
            for entry in results:
                print(f"\nService: {entry['service']}")
                print(f"Username: {entry['username']}")
                print(f"Password: {entry['password']}")
                if entry.get('notes'):
                    print(f"Notes: {entry['notes']}")
        else:
            print(f"No entries found for '{search_term}'")

    def delete_password(self):
        """Delete a password entry"""
        if not self.passwords:
            print("\n📭 No passwords saved yet!")
            return

        self.view_passwords()

        try:
            choice = int(input("\n🗑️ Enter number to delete (0 to cancel): "))
            if 1 <= choice <= len(self.passwords):
                confirm = input(f"Delete '{self.passwords[choice-1]['service']}'? (y/n): ")
                if confirm.lower() == 'y':
                    deleted = self.passwords.pop(choice-1)
                    self.save_passwords()
                    print(f"✅ '{deleted['service']}' deleted successfully!")
                else:
                    print("Cancelled.")
            elif choice != 0:
                print("Invalid number!")
        except ValueError:
            print("Please enter a valid number!")

    def export_passwords(self):
        """Export passwords to a text file"""
        if not self.passwords:
            print("\n📭 No passwords to export!")
            return

        filename = f"password_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, 'w') as f:
                f.write("PASSWORD EXPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for entry in self.passwords:
                    f.write(f"Service: {entry['service']}\n")
                    f.write(f"Username: {entry['username']}\n")
                    f.write(f"Password: {entry['password']}\n")
                    if entry.get('notes'):
                        f.write(f"Notes: {entry['notes']}\n")
                    f.write(f"Created: {entry['created']}\n")
                    f.write("-" * 30 + "\n")

            print(f"✅ Passwords exported to: {filename}")
            print("⚠️  WARNING: This file is NOT encrypted!")

        except IOError as e:
            print(f"❌ Error exporting: {e}")

    def password_strength_checker(self):
        """Check password strength"""
        password = self.input_password("Enter password to check: ")

        score = 0
        feedback = []

        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
            feedback.append("⚠️ Consider making password at least 12 characters")
        else:
            feedback.append("❌ Password too short (minimum 8 characters)")

        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)

        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_symbol:
            score += 2

        # Feedback
        if not has_upper:
            feedback.append("Add uppercase letters")
        if not has_lower:
            feedback.append("Add lowercase letters")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_symbol:
            feedback.append("Add special characters (!@#$% etc.)")

        # Determine strength
        print("\n🔐 PASSWORD STRENGTH ANALYSIS")
        print("=" * 35)

        if score >= 7:
            strength = "🟢 STRONG"
            emoji = "💪"
        elif score >= 4:
            strength = "🟡 MEDIUM"
            emoji = "⚠️"
        else:
            strength = "🔴 WEAK"
            emoji = "❌"

        print(f"Strength: {strength} {emoji}")
        print(f"Score: {score}/7")

        if feedback:
            print("\nSuggestions:")
            for tip in feedback:
                print(f"  • {tip}")

    def save_passwords(self):
        """Save passwords to CSV file"""
        try:
            with open(PASSWORD_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['service', 'username', 'password', 'notes', 'created'])
                writer.writeheader()
                writer.writerows(self.passwords)
            return True
        except IOError as e:
            print(f"❌ Error saving passwords: {e}")
            return False

    def load_passwords(self):
        """Load passwords from CSV file"""
        if not os.path.exists(PASSWORD_FILE):
            self.passwords = []
            return

        try:
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.passwords = list(reader)
        except Exception as e:
            print(f"⚠️ Error loading passwords: {e}")
            self.passwords = []

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main program loop"""
    print("\n" + "=" * 50)
    print("🔐 PASSWORD MANAGER & GENERATOR")
    print("=" * 50)

    manager = PasswordManager()

    # Login or setup
    if not manager.verify_master_password():
        return

    # Main menu
    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 🔑 Generate Password")
        print("2. ➕ Add New Password")
        print("3. 📋 View All Passwords")
        print("4. 🔍 Search Password")
        print("5. 🗑️ Delete Password")
        print("6. 📤 Export Passwords")
        print("7. 🔒 Check Password Strength")
        print("8. 🚪 Exit")
        print("=" * 40)


        choice = input("\nEnter your choice (1-8): ").strip()

        if choice == '1':
            length_input = input("Password length (default 12): ").strip()
            length = int(length_input) if length_input.isdigit() else 12
            use_symbols = input("Include symbols? (y/n, default y): ").strip().lower() != 'n'
            password = manager.generate_password(length, use_symbols)
            print(f"\n🔑 Generated Password: {password}")

        elif choice == '2':
            manager.add_password()

        elif choice == '3':
            manager.view_passwords()

        elif choice == '4':
            manager.search_password()

        elif choice == '5':
            manager.delete_password()

        elif choice == '6':
            manager.export_passwords()

        elif choice == '7':
            manager.password_strength_checker()

        elif choice == '8':
            print("\n👋 Goodbye! Stay secure!")
            break

        else:
            print("❌ Invalid choice! Please enter 1-8.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()