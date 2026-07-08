"""
main.py

CLI demo script for PawPal+. Creates an Owner with two Pets, adds several
Tasks out of order (including a daily-recurring task and a scheduling
conflict), then exercises the Scheduler's sorting, filtering,
conflict-detection, and recurrence logic end-to-end in the terminal.

Run with: python main.py
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(title, tasks):
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (no tasks)")
        return
    for t in tasks:
        print(f"  {t}")


def main():
    owner = Owner(name="Riddhi")

    biscuit = Pet(name="Biscuit", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    # Tasks are added out of order on purpose, to prove sort_by_time() works.
    biscuit.add_task(Task("Evening walk", "18:30", "Biscuit", priority="medium"))
    biscuit.add_task(Task("Morning walk", "07:00", "Biscuit", frequency="daily", priority="high"))
    biscuit.add_task(Task("Heartworm medication", "08:00", "Biscuit", frequency="daily", priority="high"))
    luna.add_task(Task("Breakfast", "08:00", "Luna", priority="high"))  # same time as meds -> conflict
    luna.add_task(Task("Litter box check", "12:00", "Luna", priority="low"))
    luna.add_task(Task("Vet appointment", "15:00", "Luna", priority="high", frequency="once"))

    print("=" * 60)
    print(f"PawPal+ demo for {owner.name}  ({date.today().isoformat()})")
    print("=" * 60)

    print_schedule("Today's Schedule (sorted by time)", scheduler.sort_by_time())
    print_schedule("Today's Schedule (priority, then time)", scheduler.sort_by_priority_then_time())

    print_schedule("Luna's tasks only (filter_by_pet)", scheduler.filter_by_pet("Luna"))
    print_schedule("Incomplete tasks (filter_by_status)", scheduler.filter_by_status(completed=False))

    print("\nConflict Check (detect_conflicts)")
    print("-" * 33)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  ! {w}")
    else:
        print("  No conflicts detected.")

    print("\nCompleting Biscuit's daily 'Morning walk'...")
    morning_walk = biscuit.tasks[1]
    next_task = scheduler.mark_task_complete(morning_walk)
    if next_task:
        print(f"  Recurrence handled -> new task scheduled: {next_task}")

    print_schedule("Full schedule after completing a recurring task", scheduler.sort_by_time())


if __name__ == "__main__":
    main()
