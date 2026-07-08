# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. PawPal+ helps them:

- Track pet care tasks (walks, feeding, meds, appointments, grooming, etc.)
- Consider constraints (time, priority, recurrence)
- Produce a daily plan and flag scheduling conflicts

## What this app does

- Lets a user enter owner + pet info and add multiple pets
- Lets a user add tasks with a time, priority, and frequency (once/daily/weekly)
- Generates a sorted daily schedule (by time, or by priority-then-time)
- Automatically reschedules recurring tasks when they're completed
- Flags scheduling conflicts (two tasks at the same time) with a warning instead of crashing
- Is verified by a CLI demo (`main.py`) and an automated `pytest` suite

## Getting started

### Setup

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI demo

```
python main.py
```

### Run the app

```
streamlit run app.py
```

### Run the tests

```
python -m pytest
```

## Features

| Class | Responsibility |
|---|---|
| `Task` | A single activity: description, `time` (HH:MM), `pet_name`, `frequency` (once/daily/weekly), `priority` (low/medium/high), `due_date`, `completed`. Validates its own time/frequency/priority on creation. |
| `Pet` | Holds a name, species, and its own list of `Task`s. |
| `Owner` | Holds multiple `Pet`s and can flatten all of their tasks into one list. |
| `Scheduler` | The "brain" -- sorts, filters, detects conflicts, and manages recurrence across an `Owner`'s pets. |

## 🖥️ Sample Output

Output from `python main.py`:

```
============================================================
PawPal+ demo for Riddhi  (2026-07-07)
============================================================

Today's Schedule (sorted by time)
---------------------------------
  [ ] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Heartworm medication         pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Breakfast                    pet=Luna       priority=high   freq=once
  [ ] 12:00  Litter box check             pet=Luna       priority=low    freq=once
  [ ] 15:00  Vet appointment              pet=Luna       priority=high   freq=once
  [ ] 18:30  Evening walk                 pet=Biscuit    priority=medium freq=once

Today's Schedule (priority, then time)
--------------------------------------
  [ ] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Heartworm medication         pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Breakfast                    pet=Luna       priority=high   freq=once
  [ ] 15:00  Vet appointment              pet=Luna       priority=high   freq=once
  [ ] 18:30  Evening walk                 pet=Biscuit    priority=medium freq=once
  [ ] 12:00  Litter box check             pet=Luna       priority=low    freq=once

Luna's tasks only (filter_by_pet)
---------------------------------
  [ ] 08:00  Breakfast                    pet=Luna       priority=high   freq=once
  [ ] 12:00  Litter box check             pet=Luna       priority=low    freq=once
  [ ] 15:00  Vet appointment              pet=Luna       priority=high   freq=once

Incomplete tasks (filter_by_status)
-----------------------------------
  [ ] 18:30  Evening walk                 pet=Biscuit    priority=medium freq=once
  [ ] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Heartworm medication         pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Breakfast                    pet=Luna       priority=high   freq=once
  [ ] 12:00  Litter box check             pet=Luna       priority=low    freq=once
  [ ] 15:00  Vet appointment              pet=Luna       priority=high   freq=once

Conflict Check (detect_conflicts)
---------------------------------
  ! Conflict at 08:00 on 2026-07-07: 'Heartworm medication' (Biscuit) overlaps with 'Breakfast' (Luna)

Completing Biscuit's daily 'Morning walk'...
  Recurrence handled -> new task scheduled: [ ] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily

Full schedule after completing a recurring task
-----------------------------------------------
  [x] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily
  [ ] 07:00  Morning walk                 pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Heartworm medication         pet=Biscuit    priority=high   freq=daily
  [ ] 08:00  Breakfast                    pet=Luna       priority=high   freq=once
  [ ] 12:00  Litter box check             pet=Luna       priority=low    freq=once
  [ ] 15:00  Vet appointment              pet=Luna       priority=high   freq=once
  [ ] 18:30  Evening walk                 pet=Biscuit    priority=medium freq=once
```

## 🧪 Testing PawPal+

```
# Run the full test suite:
python -m pytest
```

The suite covers: task completion, task addition/count, chronological sorting, priority-then-time sorting, filtering by pet, filtering by status, daily recurrence, weekly recurrence, one-time tasks not recurring, conflict detection (positive and negative cases), completed tasks being excluded from conflict checks, and invalid input (bad time format, bad frequency).

Sample test output:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: pawpal-plus
collecting ... collected 15 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  6%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 13%]
tests/test_pawpal.py::test_pet_with_no_tasks_has_zero_count PASSED       [ 20%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 26%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED             [ 33%]
tests/test_pawpal.py::test_filter_by_pet PASSED                          [ 40%]
tests/test_pawpal.py::test_filter_by_status PASSED                       [ 46%]
tests/test_pawpal.py::test_daily_recurrence_creates_next_day_task PASSED [ 53%]
tests/test_pawpal.py::test_weekly_recurrence_creates_task_one_week_later PASSED [ 60%]
tests/test_pawpal.py::test_one_time_task_does_not_recur PASSED           [ 66%]
tests/test_pawpal.py::test_conflict_detection_flags_duplicate_times PASSED [ 73%]
tests/test_pawpal.py::test_no_conflict_when_times_differ PASSED          [ 80%]
tests/test_pawpal.py::test_completed_tasks_are_excluded_from_conflict_check PASSED [ 86%]
tests/test_pawpal.py::test_invalid_time_format_raises PASSED             [ 93%]
tests/test_pawpal.py::test_invalid_frequency_raises PASSED               [100%]

============================== 15 passed in 0.22s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) -- core sorting, filtering, recurrence, and conflict detection are all covered and passing. What would push this to 5/5: tests for multi-week recurrence chains and for conflict detection across daylight-saving/timezone edge cases, neither of which this scenario currently needs.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---|---|---|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority_then_time()` | Time sort uses `sorted()` with a lambda key on the `"HH:MM"` string (zero-padded, so lexicographic order = chronological order). Priority sort uses a `(priority_rank, time)` tuple key. |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filters the flattened task list by pet name or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags any two *incomplete* tasks sharing the same `due_date` + `time`, across any pet. Returns warning strings rather than raising, so the UI/CLI can display them without crashing. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | On completion, a `daily` task spawns a new one at `due_date + 1 day`; `weekly` spawns one at `due_date + 7 days`, using `datetime.timedelta`. |

## 📸 Demo Walkthrough

1. **Add pets.** Enter a pet name and species and click "Add Pet." Repeat for each pet (e.g., Biscuit the dog, Luna the cat). Pets persist in `st.session_state.owner` across reruns.
2. **Schedule tasks.** For each pet, add a task with a description, time, frequency (once/daily/weekly), and priority (low/medium/high).
3. **View today's schedule.** The schedule table updates live, sortable by time or by priority-then-time, and filterable by pet or completion status.
4. **See conflict warnings.** If two tasks land on the same time (e.g., an 8:00 AM medication for one pet and an 8:00 AM breakfast for another), a warning banner appears above the table.
5. **Complete a task.** Select a task and click "Mark Complete." One-time tasks simply get checked off; daily/weekly tasks automatically spawn their next occurrence, and a confirmation message shows the new due date.

**Key Scheduler behaviors demonstrated:** chronological sorting, priority-first sorting, pet/status filtering, conflict warnings, and automatic recurrence -- all shown live in `main.py`'s CLI output above.
