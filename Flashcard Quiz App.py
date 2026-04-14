"""
Flashcard Quiz App - Learn Anything with Spaced Repetition
Concepts covered:
- JSON file handling
- Object-oriented programming
- Random selection & shuffling
- Progress tracking
- User input validation
- Statistics & scoring
- Time tracking
"""

import json
import os
import random
import time
from datetime import datetime, timedelta

# File to store flashcard sets
FLASHCARDS_FILE = "flashcards.json"


class Flashcard:
    """Individual flashcard class"""

    def __init__(self, question, answer, category="General"):
        self.question = question
        self.answer = answer
        self.category = category
        self.correct_count = 0
        self.wrong_count = 0
        self.last_reviewed = None
        self.next_review = datetime.now().isoformat()

    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'last_reviewed': self.last_reviewed,
            'next_review': self.next_review
        }

    @classmethod
    def from_dict(cls, data):
        """Create flashcard from dictionary"""
        card = cls(data['question'], data['answer'], data['category'])
        card.correct_count = data.get('correct_count', 0)
        card.wrong_count = data.get('wrong_count', 0)
        card.last_reviewed = data.get('last_reviewed')
        card.next_review = data.get('next_review', datetime.now().isoformat())
        return card

    def get_accuracy(self):
        """Get accuracy percentage"""
        total = self.correct_count + self.wrong_count
        if total == 0:
            return 0
        return (self.correct_count / total) * 100

    def review(self, correct):
        """Update card statistics after review"""
        if correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1

        self.last_reviewed = datetime.now().isoformat()

        # Spaced repetition: schedule next review
        if correct:
            # If correct, schedule further in future
            days_to_add = min(30, (self.correct_count + 1) * 2)
        else:
            # If wrong, review sooner
            days_to_add = 1

        self.next_review = (datetime.now() + timedelta(days=days_to_add)).isoformat()


class FlashcardSet:
    """Collection of flashcards"""

    def __init__(self, name):
        self.name = name
        self.cards = []
        self.created_date = datetime.now().isoformat()

    def add_card(self, question, answer, category="General"):
        """Add a new flashcard"""
        card = Flashcard(question, answer, category)
        self.cards.append(card)
        return card

    def remove_card(self, index):
        """Remove a flashcard by index"""
        if 0 <= index < len(self.cards):
            return self.cards.pop(index)
        return None

    def get_card_count(self):
        """Get total number of cards"""
        return len(self.cards)

    def get_stats(self):
        """Get set statistics"""
        if not self.cards:
            return {
                'total': 0,
                'avg_accuracy': 0,
                'mastered': 0,
                'needs_review': 0
            }

        total = len(self.cards)
        avg_accuracy = sum(c.get_accuracy() for c in self.cards) / total
        mastered = sum(1 for c in self.cards if c.get_accuracy() >= 80)

        # Cards that need review (next_review <= now)
        now = datetime.now()
        needs_review = sum(1 for c in self.cards
                           if datetime.fromisoformat(c.next_review) <= now)

        return {
            'total': total,
            'avg_accuracy': avg_accuracy,
            'mastered': mastered,
            'needs_review': needs_review
        }

    def to_dict(self):
        """Convert entire set to dictionary"""
        return {
            'name': self.name,
            'created_date': self.created_date,
            'cards': [card.to_dict() for card in self.cards]
        }

    @classmethod
    def from_dict(cls, data):
        """Create flashcard set from dictionary"""
        set_obj = cls(data['name'])
        set_obj.created_date = data.get('created_date', datetime.now().isoformat())
        set_obj.cards = [Flashcard.from_dict(card_data) for card_data in data.get('cards', [])]
        return set_obj


class FlashcardApp:
    """Main application class"""

    def __init__(self):
        self.sets = []
        self.current_set = None
        self.load_data()

    def load_data(self):
        """Load flashcard sets from file"""
        if os.path.exists(FLASHCARDS_FILE):
            try:
                with open(FLASHCARDS_FILE, 'r') as f:
                    data = json.load(f)
                    self.sets = [FlashcardSet.from_dict(set_data) for set_data in data]
            except:
                self.sets = []
        else:
            self.sets = []

    def save_data(self):
        """Save flashcard sets to file"""
        try:
            data = [set_obj.to_dict() for set_obj in self.sets]
            with open(FLASHCARDS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except:
            return False

    def create_set(self):
        """Create a new flashcard set"""
        print("\n🃏 CREATE NEW FLASHCARD SET")
        print("-" * 30)

        name = input("Set name: ").strip()
        if not name:
            print("❌ Name cannot be empty!")
            return

        # Check if set already exists
        if any(s.name.lower() == name.lower() for s in self.sets):
            print("❌ A set with this name already exists!")
            return

        new_set = FlashcardSet(name)
        self.sets.append(new_set)
        self.save_data()
        print(f"✅ Set '{name}' created!")

        # Ask to add cards
        add_cards = input("Add cards now? (y/n): ").strip().lower()
        if add_cards == 'y':
            self.add_cards_to_set(new_set)

    def add_cards_to_set(self, flashcard_set):
        """Add multiple cards to a set"""
        print(f"\n📝 ADD CARDS TO '{flashcard_set.name}'")
        print("(Type 'done' when finished)")
        print("-" * 30)

        card_count = 0
        while True:
            print(f"\nCard #{card_count + 1}:")
            question = input("Question: ").strip()
            if question.lower() == 'done':
                break

            answer = input("Answer: ").strip()
            if answer.lower() == 'done':
                break

            category = input("Category (optional, press Enter for General): ").strip()
            if not category:
                category = "General"

            flashcard_set.add_card(question, answer, category)
            card_count += 1
            print(f"✅ Card added!")

        if card_count > 0:
            self.save_data()
            print(f"\n✅ Added {card_count} cards to '{flashcard_set.name}'!")

    def list_sets(self):
        """Display all flashcard sets"""
        if not self.sets:
            print("\n📭 No flashcard sets yet!")
            return

        print("\n🃏 YOUR FLASHCARD SETS")
        print("=" * 50)

        for i, set_obj in enumerate(self.sets, 1):
            stats = set_obj.get_stats()
            print(f"\n{i}. {set_obj.name}")
            print(f"   📊 {stats['total']} cards | 🎯 {stats['avg_accuracy']:.0f}% accuracy")
            print(f"   ✅ {stats['mastered']} mastered | ⏰ {stats['needs_review']} need review")

        print("\n" + "=" * 50)

    def select_set(self):
        """Select a flashcard set to work with"""
        self.list_sets()

        if not self.sets:
            return None

        try:
            choice = int(input("\nSelect set number (0 to cancel): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(self.sets):
                self.current_set = self.sets[choice - 1]
                print(f"\n✅ Selected: {self.current_set.name}")
                return self.current_set
            else:
                print("❌ Invalid selection!")
                return None
        except ValueError:
            print("❌ Please enter a valid number!")
            return None

    def study_session(self):
        """Start a study session"""
        if not self.select_set():
            return

        if not self.current_set.cards:
            print("📭 This set has no cards! Add some first.")
            return

        print(f"\n📚 STUDY SESSION: {self.current_set.name}")
        print("=" * 40)

        # Get cards due for review
        now = datetime.now()
        due_cards = [c for c in self.current_set.cards
                     if datetime.fromisoformat(c.next_review) <= now]

        if not due_cards:
            print("🎉 No cards due for review! Take a break or add more cards.")
            return

        print(f"📊 {len(due_cards)} cards due for review today")

        # Session stats
        correct_count = 0
        total_reviewed = 0

        # Shuffle cards for variety
        random.shuffle(due_cards)

        for card in due_cards:
            total_reviewed += 1
            print(f"\n{'=' * 50}")
            print(f"Card {total_reviewed}/{len(due_cards)}")
            print(f"Category: {card.category}")
            print(f"Accuracy: {card.get_accuracy():.0f}%")
            print(f"\n❓ {card.question}")

            # Show answer options
            print("\nOptions:")
            print("1. Show answer")
            print("2. Skip for now")

            choice = input("\nChoice (1-2): ").strip()

            if choice == '1':
                print(f"\n✅ Answer: {card.answer}")

                # Get feedback
                print("\nDid you get it right?")
                print("1. Yes, I knew it")
                print("2. No, I got it wrong")

                feedback = input("Choice (1-2): ").strip()

                correct = feedback == '1'
                card.review(correct)

                if correct:
                    correct_count += 1
                    print("🎉 Great! Keep it up!")
                else:
                    print("📝 Keep practicing! You'll get it next time.")

                self.save_data()

            else:
                print("⏭️ Skipped for now")

            # Small pause between cards
            if total_reviewed < len(due_cards):
                time.sleep(1)

        # Session summary
        print(f"\n{'=' * 50}")
        print("📊 SESSION SUMMARY")
        print(f"Cards reviewed: {total_reviewed}")
        print(f"Correct answers: {correct_count}")
        if total_reviewed > 0:
            print(f"Success rate: {(correct_count / total_reviewed) * 100:.0f}%")
        print("=" * 50)

    def quick_quiz(self):
        """Random quiz from all cards"""
        all_cards = []
        for set_obj in self.sets:
            all_cards.extend(set_obj.cards)

        if not all_cards:
            print("\n📭 No cards available! Create some first.")
            return

        print("\n🎯 QUICK QUIZ (Random 10 Questions)")
        print("=" * 40)

        # Select random cards
        quiz_cards = random.sample(all_cards, min(10, len(all_cards)))
        score = 0

        for i, card in enumerate(quiz_cards, 1):
            print(f"\nQ{i}. {card.question}")
            print("(Type 'answer' to reveal, 'skip' to move on)")

            choice = input("> ").strip().lower()

            if choice == 'answer':
                print(f"\n✅ Answer: {card.answer}")
                result = input("\nDid you get it right? (y/n): ").strip().lower()

                if result == 'y':
                    score += 1
                    print("🎉 Correct!\n")
                else:
                    print("📝 Keep practicing!\n")
            else:
                print("⏭️ Skipped\n")

            time.sleep(0.5)

        print(f"\n{'=' * 40}")
        print(f"🎯 QUIZ COMPLETE!")
        print(f"Score: {score}/{len(quiz_cards)} ({score / len(quiz_cards) * 100:.0f}%)")
        print("=" * 40)

    def manage_cards(self):
        """Add, edit, or remove cards from current set"""
        if not self.select_set():
            return

        while True:
            print(f"\n🃏 MANAGING: {self.current_set.name}")
            print("-" * 30)
            print("1. Add new card")
            print("2. View all cards")
            print("3. Edit card")
            print("4. Remove card")
            print("5. Back to main menu")

            choice = input("\nChoice (1-5): ").strip()

            if choice == '1':
                self.add_cards_to_set(self.current_set)

            elif choice == '2':
                self.view_cards(self.current_set)

            elif choice == '3':
                self.edit_card(self.current_set)

            elif choice == '4':
                self.remove_card(self.current_set)

            elif choice == '5':
                break
            else:
                print("❌ Invalid choice!")

    def view_cards(self, flashcard_set):
        """View all cards in a set"""
        if not flashcard_set.cards:
            print("\n📭 No cards in this set!")
            return

        print(f"\n📋 CARDS IN '{flashcard_set.name}'")
        print("=" * 60)

        for i, card in enumerate(flashcard_set.cards, 1):
            print(f"\n{i}. Q: {card.question}")
            print(f"   A: {card.answer}")
            print(f"   Category: {card.category}")
            print(f"   Stats: {card.correct_count} correct, {card.wrong_count} wrong")
            print(f"   Accuracy: {card.get_accuracy():.0f}%")

        print("\n" + "=" * 60)

    def edit_card(self, flashcard_set):
        """Edit a specific card"""
        self.view_cards(flashcard_set)

        if not flashcard_set.cards:
            return

        try:
            card_num = int(input("\nEnter card number to edit (0 to cancel): "))
            if card_num == 0:
                return
            if 1 <= card_num <= len(flashcard_set.cards):
                card = flashcard_set.cards[card_num - 1]

                print(f"\nEditing card #{card_num}")
                print("(Press Enter to keep current value)")

                new_question = input(f"Question [{card.question}]: ").strip()
                if new_question:
                    card.question = new_question

                new_answer = input(f"Answer [{card.answer}]: ").strip()
                if new_answer:
                    card.answer = new_answer

                new_category = input(f"Category [{card.category}]: ").strip()
                if new_category:
                    card.category = new_category

                self.save_data()
                print("✅ Card updated!")
            else:
                print("❌ Invalid card number!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def remove_card(self, flashcard_set):
        """Remove a card from set"""
        self.view_cards(flashcard_set)

        if not flashcard_set.cards:
            return

        try:
            card_num = int(input("\nEnter card number to remove (0 to cancel): "))
            if card_num == 0:
                return
            if 1 <= card_num <= len(flashcard_set.cards):
                card = flashcard_set.cards[card_num - 1]
                confirm = input(f"Remove card: '{card.question}'? (y/n): ")
                if confirm.lower() == 'y':
                    flashcard_set.remove_card(card_num - 1)
                    self.save_data()
                    print("✅ Card removed!")
            else:
                print("❌ Invalid card number!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def delete_set(self):
        """Delete a flashcard set"""
        self.list_sets()

        if not self.sets:
            return

        try:
            set_num = int(input("\nEnter set number to delete (0 to cancel): "))
            if set_num == 0:
                return
            if 1 <= set_num <= len(self.sets):
                set_obj = self.sets[set_num - 1]
                confirm = input(f"Delete set '{set_obj.name}' and all its cards? (y/n): ")
                if confirm.lower() == 'y':
                    self.sets.pop(set_num - 1)
                    self.save_data()
                    print(f"✅ Set deleted!")
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def overall_stats(self):
        """Display overall statistics"""
        if not self.sets:
            print("\n📊 No data to analyze!")
            return

        total_cards = sum(s.get_card_count() for s in self.sets)
        total_mastered = sum(s.get_stats()['mastered'] for s in self.sets)
        avg_accuracy = sum(s.get_stats()['avg_accuracy'] for s in self.sets) / len(self.sets)

        print("\n📊 OVERALL STATISTICS")
        print("=" * 40)
        print(f"\n📈 Overview:")
        print(f"   Total sets: {len(self.sets)}")
        print(f"   Total cards: {total_cards}")
        print(f"   Mastered cards: {total_mastered}")
        print(f"   Average accuracy: {avg_accuracy:.0f}%")
        print("=" * 40)


        # Best and worst sets
        if self.sets:
            best_set = max(self.sets, key=lambda s: s.get_stats()['avg_accuracy'])
            worst_set = min(self.sets, key=lambda s: s.get_stats()['avg_accuracy'])

            print(f"\n🏆 Best set: {best_set.name} ({best_set.get_stats()['avg_accuracy']:.0f}%)")
            print(f"📉 Needs work: {worst_set.name} ({worst_set.get_stats()['avg_accuracy']:.0f}%)")

        # Category breakdown
        all_categories = {}
        for set_obj in self.sets:
            for card in set_obj.cards:
                all_categories[card.category] = all_categories.get(card.category, 0) + 1

        if all_categories:
            print(f"\n📂 Cards by category:")
            for category, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count} cards")


def main():
    """Main program loop"""
    print("\n" + "=" * 50)
    print("🃏 FLASHCARD QUIZ APP")
    print("Learn with Spaced Repetition")
    print("=" * 50)

    app = FlashcardApp()

    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 📚 Study Session (Due Cards)")
        print("2. 🎯 Quick Quiz (Random)")
        print("3. 🃏 Create New Set")
        print("4. 📝 Manage Cards")
        print("5. 📋 View All Sets")
        print("6. 🗑️ Delete Set")
        print("7. 📊 Overall Statistics")
        print("8. 🚪 Exit")
        print("=" * 40)
        print()

        choice = input("\nYour choice (1-8): ").strip()

        if choice == '1':
            app.study_session()
        elif choice == '2':
            app.quick_quiz()
        elif choice == '3':
            app.create_set()
        elif choice == '4':
            app.manage_cards()
        elif choice == '5':
            app.list_sets()
        elif choice == '6':
            app.delete_set()
        elif choice == '7':
            app.overall_stats()
        elif choice == '8':
            print("\n👋 Goodbye! Keep learning! 🧠✨")
            break
        else:
            print("❌ Invalid choice! Please enter 1-8.")

        input("\nPress Enter to continue...")
        print("\n" + "=" * 40)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Keep learning!")
    except Exception as e:
        print(f"\n❌ Error: {e}")