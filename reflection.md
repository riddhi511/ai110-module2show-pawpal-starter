# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My first pass identified four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` holds a list of `Pet`s and is the top-level entry point for the whole system. `Pet` holds its own name, species, and a list of `Task`s -- I gave each pet ownership of its tasks rather than storing one giant global task list, since that mirrors how a real pet owner thinks ("what does Biscuit need today?"). `Task` is a small, mostly-data class: description, time, frequency, and completion status. `Scheduler` was the one class with no attributes of its own in the draft -- just the "brain" that reads tasks from an `Owner` and reorders/filters them. I chose dataclasses for `Task` and `Pet` specifically because they're primarily data containers, and dataclasses cut down on boilerplate `__init__` code while still letting me add real methods on top.

**b. Design changes**

The design changed in three ways once I got into implementation:

1. `Task` needed a `pet_name` field. In the draft, I assumed the `Scheduler` could always figure out which pet a task belonged to by walking `Owner.pets`, but conflict detection and filtering both need to compare tasks across pets directly, so tagging each `Task` with its owning pet's name up front was much simpler than re-deriving it.
2. `Task` needed a `due_date`, not just a `time`. The original draft only had an `"HH:MM"` string, which is enough to sort a single day's schedule, but recurring tasks ("do this again tomorrow") require an actual date to add `timedelta` to. I added `due_date` (defaulting to today) once I hit that wall in Phase 4.
3. `Scheduler` went from being a stateless utility with 2 methods to a class that holds a reference to its `Owner` and exposes 8 methods (sorting x2, filtering x2, `mark_task_complete`, `detect_conflicts`, `get_all_tasks`, `today_schedule`). Keeping a reference to `Owner` let recurring-task creation actually attach the new `Task` to the right `Pet` instead of just returning a value nobody stores.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three things: **time** (the primary sort key for "what's next"), **priority** (low/medium/high, used as a secondary sort so, e.g., medication doesn't get buried under a low-priority litter box check happening at a similar time), and **frequency** (once/daily/weekly, which determines whether completing a task should spawn a follow-up). I decided time mattered most because a pet owner's actual question is almost always "what do I need to do next," not "what matters most in the abstract" -- but priority still needed to be available as an alternate sort for days with a lot of overlapping tasks.

**b. Tradeoffs**

`detect_conflicts()` only checks for *exact* `"HH:MM"` matches on the same date -- it doesn't model task duration or overlapping time ranges. Two tasks at 8:00 and 8:05 would not be flagged, even though in practice they might conflict if the 8:00 task takes 20 minutes. I chose this tradeoff because tasks in this model don't have an end time, and adding duration would have meant reworking `Task`, the sort keys, and the conflict logic all at once. For a v1 scheduler, exact-time conflicts (e.g., two tasks both scheduled for the vet at 8:00) are the most common real case and the cheapest to detect correctly without false positives.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant differently in each phase: for UML brainstorming in Phase 1, I described the four entities and asked for a Mermaid class diagram, then iterated on the relationships until "Owner has Pets" and "Pet has Tasks" reads cleanly. In Phase 2, I used agent-mode edits to flesh out method bodies from the skeleton stubs, then asked it to review `pawpal_system.py` for missing relationships. In Phase 4, I kept a separate chat session specifically for algorithmic work (sorting/filtering/recurrence/conflicts) so that debugging one method didn't get mixed up with unrelated design questions from earlier phases. The most effective prompts were narrow and file-scoped -- e.g., "given this Scheduler class, how should `sort_by_time` handle an empty task list?" -- rather than open-ended requests, which tended to produce over-engineered answers.

**b. Judgment and verification**

One suggestion I didn't take as-is: when discussing conflict detection, the AI's first draft raised an exception on a detected conflict rather than returning a warning. I rejected that because a scheduling conflict is a normal, expected situation for a pet owner (two pets both need something at 8am) -- it shouldn't crash the whole app. I asked for a "lightweight, non-crashing" version instead and verified it by writing `test_conflict_detection_flags_duplicate_times` and `test_no_conflict_when_times_differ` to confirm it returned warnings correctly in both the positive and negative case before wiring it into the UI.

---

## 4. Testing and Verification

**a. What you tested**

The suite covers: marking a task complete, adding a task increasing a pet's task count, chronological sorting, priority-then-time sorting, filtering by pet and by completion status, daily and weekly recurrence (including that a `"once"` task correctly does *not* recur), conflict detection (both a true positive and a true negative), completed tasks being excluded from conflict checks, and invalid input handling (bad time format, bad frequency value). These were the behaviors most likely to silently break as the system grew -- especially recurrence and conflict detection, since both involve date arithmetic that's easy to get off-by-one on.

**b. Confidence**

I'd put my confidence at 4/5. All 15 tests pass, and `main.py`'s CLI output visibly demonstrates every core behavior end-to-end, not just in isolation. What I'd test next with more time: recurrence across multiple completions in a row (does a weekly task still land on the right weekday after several cycles?), and conflict detection once tasks have real durations instead of just start times.

---

## 5. Reflection

**a. What went well**

The `Scheduler` design holding a reference to `Owner` rather than being a pure static-method bag turned out to be the right call -- it made `mark_task_complete()` able to actually attach a newly-created recurring task to the correct `Pet` in one call, instead of pushing that responsibility onto every caller.

**b. What you would improve**

I'd redesign `Task` to have a duration in addition to a start time, so conflict detection could catch overlapping ranges instead of just exact-time matches -- that's the tradeoff I'm least satisfied with.

**c. Key takeaway**

Acting as the "lead architect" meant the AI was fastest at generating correct-looking code and slowest at knowing which correctness actually mattered for this scenario (e.g., non-crashing conflict warnings over exceptions). My job was less about writing every line and more about deciding what the system should refuse to do, then verifying those decisions held up under tests.
