"""
Digital Diary & Mood Tracker
Concepts covered:
- File handling (JSON)
- Date & time manipulation
- Data visualization
- Sentiment tracking
- Search & filter
- Statistics

"""

import json
import os
from datetime import datetime, timedelta
import numpy as np
import random

# File to store diary entries
DIARY_FILE = "diary_entries.json"


class DigitalDiary:
    """A personal diary with mood tracking"""

    def __init__(self):
        self.entries = []
        self.load_entries()
        self.mood_icons = {
            "happy": "😊",
            "sad": "😢",
            "excited": "🤩",
            "stressed": "😫",
            "calm": "😌",
            "angry": "😠",
            "tired": "😴",
            "grateful": "🙏"
        }

    def load_entries(self):
        """Load diary entries from file"""
        if os.path.exists(DIARY_FILE):
            try:
                with open(DIARY_FILE, 'r') as f:
                    self.entries = json.load(f)
            except:
                self.entries = []
        else:
            self.entries = []

    def save_entries(self):
        """Save diary entries to file"""
        try:
            with open(DIARY_FILE, 'w') as f:
                json.dump(self.entries, f, indent=4)
            return True
        except:
            return False

    def write_entry(self):
        """Write a new diary entry"""
        print("\n📝 WRITE NEW ENTRY")
        print("-" * 30)

        # Get date
        date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if date_input:
            try:
                entry_date = datetime.strptime(date_input, '%Y-%m-%d').date()
            except:
                print("Invalid date! Using today's date.")
                entry_date = datetime.now().date()
        else:
            entry_date = datetime.now().date()

        # Check if entry exists for this date
        existing = [e for e in self.entries if e['date'] == entry_date.isoformat()]
        if existing:
            overwrite = input("Entry already exists for this date. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return

        # Get mood
        print("\nHow are you feeling today?")
        moods = list(self.mood_icons.keys())
        for i, mood in enumerate(moods, 1):
            print(f"{i}. {self.mood_icons[mood]} {mood.capitalize()}")

        while True:
            mood_choice = input("\nChoose mood (1-8): ").strip()
            if mood_choice.isdigit() and 1 <= int(mood_choice) <= 8:
                mood = moods[int(mood_choice) - 1]
                break
            print("Invalid choice! Please choose 1-8.")

        # Get title
        title = input("\nEntry title: ").strip()
        if not title:
            title = f"Entry for {entry_date}"

        # Get content
        print("\nWrite your entry (type 'END' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)

        content = '\n'.join(lines)

        if not content.strip():
            print("Empty entry not saved!")
            return

        # Get rating (1-5)
        rating = input("\nRate your day (1-5, 5 being best): ").strip()
        rating = int(rating) if rating.isdigit() and 1 <= int(rating) <= 5 else 3

        # Create entry
        entry = {
            'date': entry_date.isoformat(),
            'title': title,
            'content': content,
            'mood': mood,
            'rating': rating,
            'created_at': datetime.now().isoformat()
        }

        # Remove existing entry for this date if any
        self.entries = [e for e in self.entries if e['date'] != entry['date']]

        self.entries.append(entry)
        self.entries.sort(key=lambda x: x['date'])
        self.save_entries()

        print(f"\n✅ Entry saved! {self.mood_icons[mood]} Have a great day!")

    def view_entries(self):
        """View all diary entries"""
        if not self.entries:
            print("\n📭 No diary entries yet! Write your first entry.")
            return

        print("\n📖 YOUR DIARY ENTRIES")
        print("=" * 60)

        for entry in self.entries:
            date_obj = datetime.fromisoformat(entry['date']).date()
            mood_icon = self.mood_icons.get(entry['mood'], '📝')
            stars = '★' * entry['rating'] + '☆' * (5 - entry['rating'])

            print(f"\n📅 {date_obj.strftime('%B %d, %Y')} {mood_icon}")
            print(f"📌 {entry['title']}")
            print(f"⭐ {stars}")
            print(f"📝 {entry['content'][:100]}..." if len(entry['content']) > 100 else f"📝 {entry['content']}")

        print("\n" + "=" * 60)
        print(f"Total entries: {len(self.entries)}")

    def view_entry_by_date(self):
        """View a specific entry by date"""
        if not self.entries:
            print("\n📭 No entries yet!")
            return

        date_str = input("\n📅 Enter date (YYYY-MM-DD): ").strip()

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            entry = next((e for e in self.entries if e['date'] == target_date.isoformat()), None)

            if entry:
                self.display_single_entry(entry)
            else:
                print(f"No entry found for {date_str}")
        except:
            print("Invalid date format! Use YYYY-MM-DD")

    def display_single_entry(self, entry):
        """Display a single entry in detail"""
        date_obj = datetime.fromisoformat(entry['date']).date()
        mood_icon = self.mood_icons.get(entry['mood'], '📝')
        stars = '★' * entry['rating'] + '☆' * (5 - entry['rating'])

        print("\n" + "=" * 60)
        print(f"📅 {date_obj.strftime('%B %d, %Y')} {mood_icon}")
        print(f"📌 {entry['title']}")
        print(f"⭐ {stars}")
        print("=" * 60)
        print(f"\n{entry['content']}")
        print("\n" + "=" * 60)

        # Options
        print("\nOptions:")
        print("1. Edit this entry")
        print("2. Delete this entry")
        print("3. Back to menu")

        choice = input("\nChoose (1-3): ").strip()

        if choice == '1':
            self.edit_entry(entry['date'])
        elif choice == '2':
            self.delete_entry(entry['date'])

    def edit_entry(self, date=None):
        """Edit an existing entry"""
        if not date:
            date_str = input("\n📅 Enter date of entry to edit (YYYY-MM-DD): ").strip()
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()
            except:
                print("Invalid date!")
                return

        entry = next((e for e in self.entries if e['date'] == date), None)

        if not entry:
            print("Entry not found!")
            return

        print(f"\n✏️ Editing entry for {date}")
        print("(Press Enter to keep current value)")

        # Edit title
        new_title = input(f"Title [{entry['title']}]: ").strip()
        if new_title:
            entry['title'] = new_title

        # Edit content
        print(f"\nCurrent content:\n{entry['content']}")
        print("\nEnter new content (type 'END' on a new line to finish, or press Enter to keep):")
        lines = []
        first_line = input()
        if first_line.strip() == 'END' or not first_line:
            # Keep existing content
            pass
        else:
            lines.append(first_line)
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            if lines:
                entry['content'] = '\n'.join(lines)

        # Edit rating
        new_rating = input(f"Rating (1-5) [{entry['rating']}]: ").strip()
        if new_rating.isdigit() and 1 <= int(new_rating) <= 5:
            entry['rating'] = int(new_rating)

        # Edit mood
        print("\nMood options:")
        moods = list(self.mood_icons.keys())
        for i, mood in enumerate(moods, 1):
            print(f"{i}. {self.mood_icons[mood]} {mood.capitalize()}")
        new_mood = input(f"Mood choice (1-8) [{moods.index(entry['mood']) + 1}]: ").strip()
        if new_mood.isdigit() and 1 <= int(new_mood) <= 8:
            entry['mood'] = moods[int(new_mood) - 1]

        self.save_entries()
        print("✅ Entry updated!")

    def delete_entry(self, date=None):
        """Delete an entry"""
        if not date:
            date_str = input("\n📅 Enter date of entry to delete (YYYY-MM-DD): ").strip()
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()
            except:
                print("Invalid date!")
                return

        entry = next((e for e in self.entries if e['date'] == date), None)

        if entry:
            confirm = input(f"Delete entry for {date}? (y/n): ")
            if confirm.lower() == 'y':
                self.entries = [e for e in self.entries if e['date'] != date]
                self.save_entries()
                print("✅ Entry deleted!")
        else:
            print("Entry not found!")

    def search_entries(self):
        """Search entries by keyword"""
        if not self.entries:
            print("\n📭 No entries to search!")
            return

        keyword = input("\n🔍 Search keyword: ").strip().lower()

        if not keyword:
            return

        results = []
        for entry in self.entries:
            if (keyword in entry['title'].lower() or
                    keyword in entry['content'].lower()):
                results.append(entry)

        if results:
            print(f"\n📖 Found {len(results)} matching entry(s):")
            print("-" * 50)
            for entry in results:
                date_obj = datetime.fromisoformat(entry['date']).date()
                mood_icon = self.mood_icons.get(entry['mood'], '📝')
                print(f"{mood_icon} {date_obj.strftime('%Y-%m-%d')} - {entry['title']}")
        else:
            print(f"No entries found matching '{keyword}'")

    def mood_statistics(self):
        """Display mood statistics"""
        if not self.entries:
            print("\n📊 No data to analyze!")
            return

        # Count moods
        mood_counts = {}
        for entry in self.entries:
            mood = entry['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Average rating
        avg_rating = sum(e['rating'] for e in self.entries) / len(self.entries)

        # Most common mood
        most_common = max(mood_counts.items(), key=lambda x: x[1]) if mood_counts else None

        print("\n📊 MOOD STATISTICS")
        print("=" * 40)

        print(f"\n📈 Overview:")
        print(f"   Total entries: {len(self.entries)}")
        print(f"   Average rating: {avg_rating:.1f}/5 ⭐")
        if most_common:
            mood_icon = self.mood_icons.get(most_common[0], '📝')
            print(f"   Most common mood: {mood_icon} {most_common[0].capitalize()} ({most_common[1]} times)")

        print(f"\n🎭 Mood Distribution:")
        for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
            mood_icon = self.mood_icons.get(mood, '📝')
            percentage = (count / len(self.entries)) * 100
            bar = '█' * int(percentage / 5)  # 20 chars max
            print(f"   {mood_icon} {mood.capitalize():10} {bar} {count} ({percentage:.0f}%)")

        # Weekly trend
        print(f"\n📅 Last 7 Days Mood Trend:")
        today = datetime.now().date()
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            entry = next((e for e in self.entries if e['date'] == date.isoformat()), None)
            if entry:
                mood_icon = self.mood_icons.get(entry['mood'], '📝')
                rating_stars = '★' * entry['rating']
                print(f"   {date.strftime('%a')}: {mood_icon} {rating_stars}")
            else:
                print(f"   {date.strftime('%a')}: 📭 No entry")

    def get_inspiration(self):
        """Get a random writing prompt"""
        prompts = [
            "What made you smile today?",
            "What was the best part of your day?",
            "What's something you learned today?",
            "What are you grateful for right now?",
            "What challenge did you face today?",
            "What's something you're looking forward to?",
            "Describe a moment of peace today.",
            "What would make tomorrow better than today?",
            "Who made a difference in your day?",
            "What's something beautiful you noticed today?",
            "What did you do for yourself today?",
            "What's a small victory you had today?"
        ]

        print("\n💡 WRITING INSPIRATION")
        print("=" * 40)
        print(f"\n{random.choice(prompts)}")
        print("\n✨ Start writing in the main menu!")

    def export_diary(self):
        """Export diary to text file"""
        if not self.entries:
            print("\n📭 No entries to export!")
            return

        filename = f"diary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("MY PERSONAL DIARY\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for entry in self.entries:
                    date_obj = datetime.fromisoformat(entry['date']).date()
                    mood_icon = self.mood_icons.get(entry['mood'], '📝')
                    stars = '★' * entry['rating'] + '☆' * (5 - entry['rating'])

                    f.write(f"\n{'=' * 50}\n")
                    f.write(f"Date: {date_obj.strftime('%B %d, %Y')} {mood_icon}\n")
                    f.write(f"Title: {entry['title']}\n")
                    f.write(f"Rating: {stars}\n")
                    f.write(f"\n{entry['content']}\n")

                f.write(f"\n{'=' * 50}\n")
                f.write(f"Total entries: {len(self.entries)}\n")

            print(f"✅ Diary exported to: {filename}")
        except Exception as e:
            print(f"❌ Error exporting: {e}")


def main():
    """Main program loop"""
    print("\n" + "=" * 50)
    print("📔 DIGITAL DIARY & MOOD TRACKER")
    print("=" * 50)
    print("\n✨ Your safe space to write, reflect, and grow ✨")

    diary = DigitalDiary()

    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 📝 Write New Entry")
        print("2. 📖 View All Entries")
        print("3. 🔍 View Entry by Date")
        print("4. ✏️ Edit Entry")
        print("5. 🗑️ Delete Entry")
        print("6. 🔎 Search Entries")
        print("7. 📊 Mood Statistics")
        print("8. 💡 Get Writing Inspiration")
        print("9. 📤 Export Diary")
        print("10. 🚪 Exit")
        print("=" * 40)

        choice = input("\nYour choice (1-10): ").strip()

        if choice == '1':
            diary.write_entry()
        elif choice == '2':
            diary.view_entries()
        elif choice == '3':
            diary.view_entry_by_date()
        elif choice == '4':
            diary.edit_entry()
        elif choice == '5':
            diary.delete_entry()
        elif choice == '6':
            diary.search_entries()
        elif choice == '7':
            diary.mood_statistics()
        elif choice == '8':
            diary.get_inspiration()
        elif choice == '9':
            diary.export_diary()
        elif choice == '10':
            print("\n👋 Goodbye! Keep writing and growing! 📔✨")
            break
        else:
            print("❌ Invalid choice! Please enter 1-10.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Take care! 📔")
    except Exception as e:
        print(f"\n❌ Error: {e}")