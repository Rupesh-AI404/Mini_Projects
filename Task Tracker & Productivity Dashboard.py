"""
Task Tracker & Productivity Dashboard
Concepts covered:
- JSON file handling
- Data visualization with matplotlib
- Time tracking
- Statistics & analytics
- Date manipulation
- Progress bars
- Sorting & filtering
"""

import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np


# File to store tasks
TASKS_FILE = "tasks.json"


class TaskTracker:
    """A comprehensive task management system"""

    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(TASKS_FILE, 'w') as f:
                json.dump(self.tasks, f, indent=4)
            return True
        except:
            return False

    def add_task(self):
        """Add a new task"""
        print("\n📝 ADD NEW TASK")
        print("-" * 30)

        title = input("Task title: ").strip()
        if not title:
            print("❌ Title cannot be empty!")
            return

        description = input("Description (optional): ").strip()

        # Priority
        print("\nPriority levels:")
        print("1. 🔴 High")
        print("2. 🟡 Medium")
        print("3. 🟢 Low")
        priority_choice = input("Choose priority (1-3, default 2): ").strip()
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice, 'medium')

        # Category
        categories = ['Work', 'Personal', 'Study', 'Health', 'Shopping', 'Other']
        print("\nCategories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        cat_choice = input("Choose category (1-6, default Other): ").strip()
        category = categories[int(cat_choice) - 1] if cat_choice.isdigit() and 1 <= int(cat_choice) <= 6 else 'Other'

        # Due date
        due_date = input("Due date (YYYY-MM-DD, optional): ").strip()
        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except:
                print("Invalid date format! Using no due date.")
                due_date = ""

        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'description': description,
            'priority': priority,
            'category': category,
            'due_date': due_date,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'time_spent': 0  # minutes
        }

        self.tasks.append(task)
        self.save_tasks()
        print(f"✅ Task '{title}' added successfully!")

    def view_tasks(self, filter_by=None):
        """View tasks with optional filtering"""
        if not self.tasks:
            print("\n📭 No tasks found!")
            return

        filtered_tasks = self.tasks.copy()

        # Apply filters
        if filter_by == 'pending':
            filtered_tasks = [t for t in filtered_tasks if t['status'] == 'pending']
        elif filter_by == 'completed':
            filtered_tasks = [t for t in filtered_tasks if t['status'] == 'completed']
        elif filter_by == 'high':
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == 'high' and t['status'] == 'pending']

        if not filtered_tasks:
            print(f"\n📭 No {filter_by if filter_by else ''} tasks found!")
            return

        print(f"\n📋 YOUR TASKS {'(' + filter_by.upper() + ')' if filter_by else ''}")
        print("=" * 70)

        for task in filtered_tasks:
            # Status icon
            status_icon = "✅" if task['status'] == 'completed' else "⏳"

            # Priority color
            priority_colors = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }
            priority_icon = priority_colors.get(task['priority'], '⚪')

            # Due date warning
            due_warning = ""
            if task['due_date'] and task['status'] == 'pending':
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
                days_left = (due_date - datetime.now()).days
                if days_left < 0:
                    due_warning = " ⚠️ OVERDUE!"
                elif days_left == 0:
                    due_warning = " ⚠️ DUE TODAY!"
                elif days_left <= 3:
                    due_warning = f" ⚠️ {days_left} days left!"

            print(f"\n{status_icon} [{task['id']}] {task['title']} {due_warning}")
            print(f"   {priority_icon} Priority: {task['priority'].upper()}")
            print(f"   📂 Category: {task['category']}")
            if task['description']:
                print(f"   📝 {task['description']}")
            if task['due_date']:
                print(f"   📅 Due: {task['due_date']}")
            if task['time_spent'] > 0:
                hours = task['time_spent'] // 60
                minutes = task['time_spent'] % 60
                print(f"   ⏱️ Time spent: {hours}h {minutes}m")

        print("\n" + "=" * 70)
        total = len(filtered_tasks)
        completed = sum(1 for t in filtered_tasks if t['status'] == 'completed')
        pending = total - completed
        print(f"📊 Total: {total} | ✅ Completed: {completed} | ⏳ Pending: {pending}")

    def complete_task(self):
        """Mark a task as completed"""
        self.view_tasks('pending')

        if not [t for t in self.tasks if t['status'] == 'pending']:
            return

        try:
            task_id = int(input("\n✅ Enter task ID to mark as complete: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task and task['status'] == 'pending':
                # Ask for time spent
                time_input = input("Time spent (minutes, optional): ").strip()
                if time_input.isdigit():
                    task['time_spent'] = int(time_input)

                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                print(f"✅ '{task['title']}' marked as completed!")
            else:
                print("❌ Invalid task ID or task already completed!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def delete_task(self):
        """Delete a task"""
        self.view_tasks()

        if not self.tasks:
            return

        try:
            task_id = int(input("\n🗑️ Enter task ID to delete: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task:
                confirm = input(f"Delete '{task['title']}'? (y/n): ")
                if confirm.lower() == 'y':
                    self.tasks.remove(task)
                    # Re-number IDs
                    for i, t in enumerate(self.tasks, 1):
                        t['id'] = i
                    self.save_tasks()
                    print(f"✅ Task deleted!")
            else:
                print("❌ Invalid task ID!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def edit_task(self):
        """Edit an existing task"""
        self.view_tasks()

        if not self.tasks:
            return

        try:
            task_id = int(input("\n✏️ Enter task ID to edit: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task:
                print(f"\nEditing: {task['title']}")
                print("(Press Enter to keep current value)")

                new_title = input(f"New title [{task['title']}]: ").strip()
                if new_title:
                    task['title'] = new_title

                new_desc = input(f"New description [{task['description']}]: ").strip()
                if new_desc:
                    task['description'] = new_desc

                new_priority = input(f"New priority (high/medium/low) [{task['priority']}]: ").strip()
                if new_priority in ['high', 'medium', 'low']:
                    task['priority'] = new_priority

                new_category = input(f"New category [{task['category']}]: ").strip()
                if new_category:
                    task['category'] = new_category

                self.save_tasks()
                print(f"✅ Task updated!")
            else:
                print("❌ Invalid task ID!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def start_timer(self):
        """Start a pomodoro-style timer for a task"""
        self.view_tasks('pending')

        pending_tasks = [t for t in self.tasks if t['status'] == 'pending']
        if not pending_tasks:
            print("No pending tasks to work on!")
            return

        try:
            task_id = int(input("\n⏱️ Enter task ID to start timer: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task and task['status'] == 'pending':
                print(f"\n🎯 Working on: {task['title']}")
                print("Timer started! Press Ctrl+C to stop...")

                import time
                minutes = 0
                try:
                    while True:
                        time.sleep(60)  # Wait 1 minute
                        minutes += 1
                        print(f"   ⏱️ {minutes} minute(s) elapsed...")
                except KeyboardInterrupt:
                    print(f"\n⏸️ Timer stopped at {minutes} minutes")
                    if minutes > 0:
                        task['time_spent'] += minutes
                        self.save_tasks()
                        print(f"✅ Added {minutes} minutes to '{task['title']}'")
            else:
                print("❌ Invalid task ID!")
        except ValueError:
            print("❌ Please enter a valid number!")

    def get_statistics(self):
        """Generate productivity statistics"""
        if not self.tasks:
            print("\n📊 No data to analyze!")
            return

        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks if t['status'] == 'completed')
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Statistics by priority
        priority_stats = {}
        for priority in ['high', 'medium', 'low']:
            priority_tasks = [t for t in self.tasks if t['priority'] == priority]
            priority_completed = sum(1 for t in priority_tasks if t['status'] == 'completed')
            priority_stats[priority] = {
                'total': len(priority_tasks),
                'completed': priority_completed,
                'rate': (priority_completed / len(priority_tasks) * 100) if priority_tasks else 0
            }

        # Statistics by category
        category_stats = defaultdict(lambda: {'total': 0, 'completed': 0})
        for task in self.tasks:
            category_stats[task['category']]['total'] += 1
            if task['status'] == 'completed':
                category_stats[task['category']]['completed'] += 1

        # Total time spent
        total_time = sum(t['time_spent'] for t in self.tasks)
        total_hours = total_time // 60
        total_minutes = total_time % 60

        # Print statistics
        print("\n📊 PRODUCTIVITY DASHBOARD")
        print("=" * 50)

        print(f"\n📈 OVERVIEW")
        print(f"   Total tasks: {total_tasks}")
        print(f"   Completed: {completed_tasks} ({completion_rate:.1f}%)")
        print(f"   Pending: {pending_tasks}")
        print(f"   ⏱️ Total time spent: {total_hours}h {total_minutes}m")

        print(f"\n🎯 BY PRIORITY")
        for priority, stats in priority_stats.items():
            icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[priority]
            print(f"   {icon} {priority.upper()}: {stats['completed']}/{stats['total']} ({stats['rate']:.1f}%)")

        print(f"\n📂 BY CATEGORY")
        for category, stats in sorted(category_stats.items()):
            rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            bar_length = int(rate / 5)  # 20 chars max
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"   {category}: {bar} {rate:.0f}% ({stats['completed']}/{stats['total']})")

        # Productivity trend (last 7 days)
        print(f"\n📅 RECENT ACTIVITY (Last 7 days)")
        today = datetime.now()
        completed_by_day = defaultdict(int)

        for task in self.tasks:
            if task['completed_at']:
                completed_date = datetime.fromisoformat(task['completed_at']).date()
                days_ago = (today.date() - completed_date).days
                if 0 <= days_ago <= 6:
                    completed_by_day[days_ago] += 1

        for days_ago in range(6, -1, -1):
            date = today - timedelta(days=days_ago)
            count = completed_by_day[days_ago]
            bar = '█' * min(count, 10)
            print(f"   {date.strftime('%a')}: {bar} ({count})")

    def visualize_data(self):
        """Create visual charts of task data"""
        if not self.tasks:
            print("\n📊 No data to visualize!")
            return

        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Task Analytics Dashboard', fontsize=16, fontweight='bold')

            # 1. Task completion status
            status_counts = [
                len([t for t in self.tasks if t['status'] == 'completed']),
                len([t for t in self.tasks if t['status'] == 'pending'])
            ]
            axes[0, 0].pie(status_counts, labels=['Completed', 'Pending'], autopct='%1.1f%%',
                           colors=['#2ecc71', '#e74c3c'], startangle=90)
            axes[0, 0].set_title('Task Completion Status')

            # 2. Tasks by priority
            priority_counts = [
                len([t for t in self.tasks if t['priority'] == 'high']),
                len([t for t in self.tasks if t['priority'] == 'medium']),
                len([t for t in self.tasks if t['priority'] == 'low'])
            ]
            axes[0, 1].bar(['High', 'Medium', 'Low'], priority_counts,
                           color=['#e74c3c', '#f39c12', '#2ecc71'])
            axes[0, 1].set_title('Tasks by Priority')
            axes[0, 1].set_ylabel('Number of Tasks')

            # 3. Tasks by category
            categories = list(set(t['category'] for t in self.tasks))
            category_counts = [len([t for t in self.tasks if t['category'] == cat]) for cat in categories]
            axes[1, 0].barh(categories, category_counts, color='#3498db')
            axes[1, 0].set_title('Tasks by Category')
            axes[1, 0].set_xlabel('Number of Tasks')

            # 4. Completion rate by priority
            priorities = ['high', 'medium', 'low']
            completion_rates = []
            for priority in priorities:
                priority_tasks = [t for t in self.tasks if t['priority'] == priority]
                if priority_tasks:
                    completed = len([t for t in priority_tasks if t['status'] == 'completed'])
                    completion_rates.append(completed / len(priority_tasks) * 100)
                else:
                    completion_rates.append(0)

            axes[1, 1].bar(['High', 'Medium', 'Low'], completion_rates,
                           color=['#e74c3c', '#f39c12', '#2ecc71'])
            axes[1, 1].set_title('Completion Rate by Priority (%)')
            axes[1, 1].set_ylabel('Completion Rate (%)')
            axes[1, 1].set_ylim(0, 100)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            print("Make sure matplotlib is installed: pip install matplotlib")

    def search_tasks(self):
        """Search tasks by keyword"""
        keyword = input("\n🔍 Search keyword: ").strip().lower()

        if not keyword:
            return

        results = []
        for task in self.tasks:
            if (keyword in task['title'].lower() or
                    keyword in task['description'].lower() or
                    keyword in task['category'].lower()):
                results.append(task)

        if results:
            print(f"\n📖 Found {len(results)} matching task(s):")
            print("-" * 50)
            for task in results:
                status = "✅" if task['status'] == 'completed' else "⏳"
                print(f"{status} {task['title']} - {task['category']} ({task['priority']})")
        else:
            print(f"No tasks found matching '{keyword}'")


def main():
    """Main program loop"""
    print("\n" + "=" * 50)
    print("🎯 TASK TRACKER & PRODUCTIVITY DASHBOARD")
    print("=" * 50)

    tracker = TaskTracker()

    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. 📝 Add Task")
        print("2. 👁️ View All Tasks")
        print("3. ⏳ View Pending Tasks")
        print("4. ✅ Complete Task")
        print("5. ✏️ Edit Task")
        print("6. 🗑️ Delete Task")
        print("7. ⏱️ Start Timer")
        print("8. 📊 View Statistics")
        print("9. 📈 Visualize Data")
        print("10. 🔍 Search Tasks")
        print("11. 🚪 Exit")
        print("=" * 40)

        choice = input("\nEnter your choice (1-11): ").strip()

        if choice == '1':
            tracker.add_task()
        elif choice == '2':
            tracker.view_tasks()
        elif choice == '3':
            tracker.view_tasks('pending')
        elif choice == '4':
            tracker.complete_task()
        elif choice == '5':
            tracker.edit_task()
        elif choice == '6':
            tracker.delete_task()
        elif choice == '7':
            tracker.start_timer()
        elif choice == '8':
            tracker.get_statistics()
        elif choice == '9':
            tracker.visualize_data()
        elif choice == '10':
            tracker.search_tasks()
        elif choice == '11':
            print("\n👋 Goodbye! Stay productive!")
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
        print(f"\n❌ Unexpected error: {e}")