"""
app.py

Streamlit front-end for PawPal+. Wires the Owner / Pet / Task / Scheduler
classes from pawpal_system.py to an interactive UI, using st.session_state
so the Owner (and all its pets/tasks) persists across Streamlit's stateless
reruns instead of being recreated empty on every click.

Run with: streamlit run app.py
"""

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care management system.")

# ---------------------------------------------------------------------------
# Session state: keep one Owner instance alive across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ---------------------------------------------------------------------------
# 1. Add a pet
# ---------------------------------------------------------------------------
st.subheader("1. Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
    submitted_pet = st.form_submit_button("Add Pet")
    if submitted_pet and pet_name:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} the {species}!")

if not owner.pets:
    st.info("Add a pet above to get started.")
    st.stop()

pet_names = [p.name for p in owner.pets]

# ---------------------------------------------------------------------------
# 2. Schedule a task
# ---------------------------------------------------------------------------
st.subheader("2. Schedule a Task")
with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("Pet", pet_names)
        description = st.text_input("Task description", value="Morning walk")
        time_value = st.time_input("Time")
    with col2:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    submitted_task = st.form_submit_button("Add Task")
    if submitted_task and description:
        pet = owner.get_pet(task_pet)
        pet.add_task(
            Task(
                description=description,
                time=time_value.strftime("%H:%M"),
                pet_name=task_pet,
                frequency=frequency,
                priority=priority,
            )
        )
        st.success(f"Scheduled '{description}' for {task_pet} at {time_value.strftime('%H:%M')}.")

# ---------------------------------------------------------------------------
# 3. Today's schedule (sorting, filtering, conflicts)
# ---------------------------------------------------------------------------
st.subheader("3. Today's Schedule")

sort_mode = st.radio("Sort by", ["Time", "Priority, then time"], horizontal=True)
filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Completed"])

tasks = scheduler.get_all_tasks()
if filter_pet != "All":
    tasks = scheduler.filter_by_pet(filter_pet, tasks)
if filter_status == "Incomplete":
    tasks = scheduler.filter_by_status(False, tasks)
elif filter_status == "Completed":
    tasks = scheduler.filter_by_status(True, tasks)

tasks = scheduler.sort_by_time(tasks) if sort_mode == "Time" else scheduler.sort_by_priority_then_time(tasks)

# Conflict warnings (always checked across ALL tasks, not just the filtered view)
for warning in scheduler.detect_conflicts():
    st.warning(f"⚠️ {warning}")

if tasks:
    table_rows = [
        {
            "Pet": t.pet_name,
            "Time": t.time,
            "Task": t.description,
            "Priority": t.priority,
            "Frequency": t.frequency,
            "Done": "✅" if t.completed else "⬜",
        }
        for t in tasks
    ]
    st.table(table_rows)

    st.markdown("#### Mark a task complete")
    task_labels = [f"{t.pet_name} — {t.time} — {t.description}" for t in tasks]
    selected_label = st.selectbox("Task", task_labels)
    if st.button("Mark Complete"):
        selected_task = tasks[task_labels.index(selected_label)]
        next_task = scheduler.mark_task_complete(selected_task)
        if next_task:
            st.success(
                f"Completed! Since this task repeats {selected_task.frequency}, "
                f"a new one was scheduled for {next_task.due_date}."
            )
        else:
            st.success("Completed!")
        st.rerun()
else:
    st.info("No tasks match the current filters.")
