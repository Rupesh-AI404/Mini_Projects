"""
Personal Library Manager - A small project covering Python fundamentals
Concepts covered:
- Variables and data types
- Lists and dictionaries
- Functions
- File I/O
- User input handling
- Conditional statements
- Loops
- Error handlin
"""

import json
import os
from datetime import datetime

# File to store library data
LIBRARY_FILE = "library.json"


def load_library():
    """Load library data from file"""
    if os.path.exists(LIBRARY_FILE):
        try:
            with open(LIBRARY_FILE, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            print("Error loading library file. Starting with empty library.")
            return []
    return []


def save_library(library):
    """Save library data to file"""
    try:
        with open(LIBRARY_FILE, 'w') as file:
            json.dump(library, file, indent=4)
        return True
    except IOError:
        print("Error saving library!")
        return False


def add_book(library):
    """Add a new book to the library"""
    print("\n📚 Add New Book")
    print("-" * 30)

    # Get book details
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ Title cannot be empty!")
        return library

    author = input("Enter author name: ").strip()
    if not author:
        print("❌ Author name cannot be empty!")
        return library

    # Validate year
    while True:
        try:
            year = int(input("Enter publication year: "))
            if 1000 <= year <= datetime.now().year:
                break
            else:
                print(f"Please enter a valid year (1000-{datetime.now().year})")
        except ValueError:
            print("Please enter a valid number!")

    genre = input("Enter genre: ").strip()
    if not genre:
        genre = "Unknown"

    # Create book dictionary
    book = {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "read": False
    }

    library.append(book)
    print(f"✅ '{title}' has been added to your library!")
    return library


def view_books(library):
    """Display all books in the library"""
    if not library:
        print("\n📚 Your library is empty!")
        return

    print("\n📚 Your Library Collection")
    print("=" * 60)

    for idx, book in enumerate(library, 1):
        read_status = "✓ Read" if book["read"] else "○ Unread"
        print(f"\n{idx}. {book['title']}")
        print(f"   Author: {book['author']}")
        print(f"   Year: {book['year']} | Genre: {book['genre']}")
        print(f"   Status: {read_status}")

    print("\n" + "=" * 60)
    print(f"Total books: {len(library)}")


def search_books(library):
    """Search for books by title or author"""
    if not library:
        print("\n📚 Your library is empty! Add some books first.")
        return

    print("\n🔍 Search Books")
    print("-" * 30)
    search_term = input("Enter title or author to search: ").strip().lower()

    if not search_term:
        print("Please enter a search term!")
        return

    results = []
    for book in library:
        if (search_term in book["title"].lower() or
                search_term in book["author"].lower()):
            results.append(book)

    if results:
        print(f"\n📖 Found {len(results)} book(s):")
        print("-" * 40)
        for idx, book in enumerate(results, 1):
            read_status = "✓ Read" if book["read"] else "○ Unread"
            print(f"{idx}. {book['title']} by {book['author']} ({book['year']}) - {read_status}")
    else:
        print(f"No books found matching '{search_term}'")


def mark_as_read(library):
    """Mark a book as read"""
    if not library:
        print("\n📚 Your library is empty!")
        return

    view_books(library)

    try:
        choice = int(input("\nEnter book number to mark as read: "))
        if 1 <= choice <= len(library):
            if not library[choice - 1]["read"]:
                library[choice - 1]["read"] = True
                print(f"✅ '{library[choice - 1]['title']}' marked as read!")
            else:
                print(f"'{library[choice - 1]['title']}' is already marked as read!")
        else:
            print("Invalid book number!")
    except ValueError:
        print("Please enter a valid number!")


def remove_book(library):
    """Remove a book from the library"""
    if not library:
        print("\n📚 Your library is empty!")
        return

    view_books(library)

    try:
        choice = int(input("\nEnter book number to remove: "))
        if 1 <= choice <= len(library):
            removed_book = library.pop(choice - 1)
            print(f"🗑️ '{removed_book['title']}' has been removed from your library!")
        else:
            print("Invalid book number!")
    except ValueError:
        print("Please enter a valid number!")


def display_statistics(library):
    """Display library statistics"""
    if not library:
        print("\n📚 Your library is empty!")
        return

    total_books = len(library)
    read_books = sum(1 for book in library if book["read"])
    unread_books = total_books - read_books
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0

    # Get unique authors and genres
    unique_authors = len(set(book["author"] for book in library))
    unique_genres = len(set(book["genre"] for book in library))

    print("\n📊 Library Statistics")
    print("=" * 40)
    print(f"Total books: {total_books}")
    print(f"Books read: {read_books} ({read_percentage:.1f}%)")
    print(f"Books unread: {unread_books}")
    print(f"Unique authors: {unique_authors}")
    print(f"Unique genres: {unique_genres}")


def main():
    """Main program loop"""
    library = load_library()

    while True:
        print("\n" + "=" * 40)
        print("📚 PERSONAL LIBRARY MANAGER")
        print("=" * 40)
        print("1. 📖 Add Book")
        print("2. 👁️ View All Books")
        print("3. 🔍 Search Books")
        print("4. ✅ Mark Book as Read")
        print("5. 🗑️ Remove Book")
        print("6. 📊 View Statistics")
        print("7. 💾 Save & Exit")
        print("=" * 40)

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == '1':
            library = add_book(library)
        elif choice == '2':
            view_books(library)
        elif choice == '3':
            search_books(library)
        elif choice == '4':
            mark_as_read(library)
        elif choice == '5':
            remove_book(library)
        elif choice == '6':
            display_statistics(library)
        elif choice == '7':
            if save_library(library):
                print("💾 Library saved! Goodbye! 👋")
            break
        else:
            print("❌ Invalid choice! Please enter 1-7.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()