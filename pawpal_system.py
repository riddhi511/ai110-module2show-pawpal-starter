"""
pawpal_system.py

Core logic layer for PawPal+, a smart pet care management system.

This module defines the domain model (Task, Pet, Owner) and the Scheduler
"brain" that sorts, filters, detects conflicts between, and manages
recurrence for pet care tasks. It has no UI dependencies -- app.py and
main.py both build on top of it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

VALID_FREQUENCIES = ("once", "daily", "weekly")
VALID_PRIORITIES = ("low", "medium", "high")
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity (e.g. a walk, feeding, or vet visit)."""

    description: str
    time: str  # "HH:MM" in 24-hour format
    pet_name: str
    frequency: str = "once"  # "once" | "daily" | "weekly"
    priority: str = "medium"  # "low" | "medium" | "high"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate frequency, priority, and time format after construction."""
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}, got {self.frequency!r}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")
        hh, sep, mm = self.time.partition(":")
        valid_time = sep == ":" and hh.isdigit() and mm.isdigit() and 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59
        if not valid_time:
            raise ValueError(f"time must be in 'HH:MM' 24-hour format, got {self.time!r}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """
        Build the next Task instance for a recurring task (daily/weekly).
        Returns None for one-time ("once") tasks.
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            pet_name=self.pet_name,
            frequency=self.frequency,
            priority=self.priority,
            due_date=self.due_date + delta,
            completed=False,
        )

    def __str__(self) -> str:
        """Human-readable one-line summary, used by the CLI demo."""
        status = "[x]" if self.completed else "[ ]"
        return f"{status} {self.time}  {self.description:<28} pet={self.pet_name:<10} priority={self.priority:<6} freq={self.frequency}"


@dataclass
class Pet:
    """A pet belonging to an Owner, with its own list of care tasks."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    @property
    def task_count(self) -> int:
        """Number of tasks currently tracked for this pet."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Look up one of this owner's pets by name, or return None."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Flatten and return every task across all of this owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """The 'brain' of PawPal+: sorts, filters, and manages tasks across an Owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # -- retrieval -----------------------------------------------------------
    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task across all of the owner's pets."""
        return self.owner.get_all_tasks()

    # -- sorting ---------------------------------------------------------------
    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted chronologically by their 'HH:MM' time string."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority_then_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (high -> low), then chronologically within each priority."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (_PRIORITY_RANK[t.priority], t.time))

    # -- filtering ----------------------------------------------------------------
    def filter_by_status(self, completed: bool, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return only tasks matching the given completion status."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return only tasks belonging to the named pet."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return [t for t in tasks if t.pet_name == pet_name]

    # -- recurrence --------------------------------------------------------------
    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete. If it recurs (daily/weekly), automatically create
        and schedule its next occurrence on the owning pet. Returns the newly
        created Task, or None if the task was one-time.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    # -- conflict detection ---------------------------------------------------------
    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """
        Lightweight conflict check: flags any pair of *incomplete* tasks that
        share the same due_date and time, whether they belong to the same pet
        or different pets. Returns human-readable warning strings instead of
        raising, so the caller can display them safely.

        Tradeoff: this only catches exact HH:MM matches, not overlapping
        durations (tasks have no end time in this model). See reflection.md.
        """
        tasks = self.get_all_tasks() if tasks is None else tasks
        warnings: List[str] = []
        active = [t for t in tasks if not t.completed]
        seen: dict = {}
        for t in active:
            key = (t.due_date, t.time)
            if key in seen:
                other = seen[key]
                warnings.append(
                    f"Conflict at {t.time} on {t.due_date}: "
                    f"'{other.description}' ({other.pet_name}) overlaps with "
                    f"'{t.description}' ({t.pet_name})"
                )
            else:
                seen[key] = t
        return warnings

    # -- convenience ------------------------------------------------------------------
    def today_schedule(self) -> List[Task]:
        """Return today's tasks, sorted by time."""
        today = date.today()
        todays = [t for t in self.get_all_tasks() if t.due_date == today]
        return self.sort_by_time(todays)
