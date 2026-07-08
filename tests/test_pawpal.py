"""
tests/test_pawpal.py

Automated test suite for PawPal+'s core logic layer (pawpal_system.py).
Covers task completion/addition, sorting, filtering, recurrence, conflict
detection, and a few edge cases (empty pet, invalid input).

Run with: python -m pytest
"""

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def owner_with_pets():
    owner = Owner(name="Riddhi")
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Luna", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat


# ---------------------------------------------------------------------------
# Task completion & addition
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:00", "Biscuit")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert pet.task_count == 0
    pet.add_task(Task("Morning walk", "07:00", "Biscuit"))
    assert pet.task_count == 1
    pet.add_task(Task("Evening walk", "18:00", "Biscuit"))
    assert pet.task_count == 2


def test_pet_with_no_tasks_has_zero_count():
    pet = Pet(name="Ghost", species="fish")
    assert pet.task_count == 0
    assert pet.tasks == []


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(owner_with_pets):
    owner, dog, cat = owner_with_pets
    dog.add_task(Task("Evening walk", "18:30", "Biscuit"))
    dog.add_task(Task("Morning walk", "07:00", "Biscuit"))
    cat.add_task(Task("Lunch", "12:00", "Luna"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == ["07:00", "12:00", "18:30"]


def test_sort_by_priority_then_time(owner_with_pets):
    owner, dog, cat = owner_with_pets
    dog.add_task(Task("Low task", "09:00", "Biscuit", priority="low"))
    dog.add_task(Task("High task late", "20:00", "Biscuit", priority="high"))
    cat.add_task(Task("High task early", "06:00", "Luna", priority="high"))

    scheduler = Scheduler(owner)
    ordered = scheduler.sort_by_priority_then_time()
    assert [t.description for t in ordered] == ["High task early", "High task late", "Low task"]


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet(owner_with_pets):
    owner, dog, cat = owner_with_pets
    dog.add_task(Task("Walk", "07:00", "Biscuit"))
    cat.add_task(Task("Feed", "08:00", "Luna"))

    scheduler = Scheduler(owner)
    luna_tasks = scheduler.filter_by_pet("Luna")
    assert len(luna_tasks) == 1
    assert luna_tasks[0].pet_name == "Luna"


def test_filter_by_status(owner_with_pets):
    owner, dog, cat = owner_with_pets
    t1 = Task("Walk", "07:00", "Biscuit")
    t2 = Task("Feed", "08:00", "Biscuit")
    t1.mark_complete()
    dog.add_task(t1)
    dog.add_task(t2)

    scheduler = Scheduler(owner)
    assert scheduler.filter_by_status(completed=True) == [t1]
    assert scheduler.filter_by_status(completed=False) == [t2]


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task(owner_with_pets):
    owner, dog, _ = owner_with_pets
    task = Task("Morning walk", "07:00", "Biscuit", frequency="daily")
    dog.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=1)
    assert next_task.completed is False
    assert dog.task_count == 2  # original + newly scheduled occurrence


def test_weekly_recurrence_creates_task_one_week_later(owner_with_pets):
    owner, dog, _ = owner_with_pets
    task = Task("Grooming", "10:00", "Biscuit", frequency="weekly")
    dog.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert next_task.due_date == task.due_date + timedelta(weeks=1)


def test_one_time_task_does_not_recur(owner_with_pets):
    owner, dog, _ = owner_with_pets
    task = Task("Vet visit", "15:00", "Biscuit", frequency="once")
    dog.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert next_task is None
    assert dog.task_count == 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_duplicate_times(owner_with_pets):
    owner, dog, cat = owner_with_pets
    dog.add_task(Task("Meds", "08:00", "Biscuit"))
    cat.add_task(Task("Breakfast", "08:00", "Luna"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflict_when_times_differ(owner_with_pets):
    owner, dog, cat = owner_with_pets
    dog.add_task(Task("Meds", "08:00", "Biscuit"))
    cat.add_task(Task("Breakfast", "09:00", "Luna"))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_completed_tasks_are_excluded_from_conflict_check(owner_with_pets):
    owner, dog, cat = owner_with_pets
    t1 = Task("Meds", "08:00", "Biscuit")
    t1.mark_complete()
    dog.add_task(t1)
    cat.add_task(Task("Breakfast", "08:00", "Luna"))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Validation edge cases
# ---------------------------------------------------------------------------

def test_invalid_time_format_raises():
    with pytest.raises(ValueError):
        Task("Bad task", "8am", "Biscuit")


def test_invalid_frequency_raises():
    with pytest.raises(ValueError):
        Task("Bad task", "08:00", "Biscuit", frequency="monthly")
