import streamlit as st
import pandas as pd

# Load the CSV data
data_url = 'python_learning_schedule_updated.csv'
progress_file = 'progress_tracking.csv'

# Function to load data from the CSV file
@st.cache_data
def load_data():
    df = pd.read_csv(data_url)
    return df

# Load or initialize progress data
def load_progress():
    try:
        progress_df = pd.read_csv(progress_file)
        progress_dict = progress_df.set_index('Key').to_dict()['Completed']
        return progress_dict
    except FileNotFoundError:
        return {}

def save_progress():
    progress_df = pd.DataFrame(list(st.session_state.progress.items()), columns=['Key', 'Completed'])
    progress_df.to_csv(progress_file, index=False)

def display_lectures(day_data, selected_day):
    st.write(f"### Lectures for {selected_day}")
    lectures = day_data['Lecture'].dropna().unique()
    if len(lectures) == 0:
        st.write("No lectures scheduled for this day.")
        return []
    for lecture in lectures:
        key = f"{selected_day}_lecture_{lecture}"
        checked = st.session_state.progress.get(key, False)
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            checked = st.checkbox("", value=checked, key=key)
            st.session_state.progress[key] = checked
        with col2:
            st.markdown(f"[Lecture Link]({lecture})")
    return lectures

def display_projects(day_data, selected_day):
    st.write(f"### Projects for {selected_day}")
    projects = day_data['Project'].dropna().unique()
    if len(projects) == 0:
        st.write("No projects scheduled for this day.")
        return []
    for project in projects:
        key = f"{selected_day}_project_{project}"
        checked = st.session_state.progress.get(key, False)
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            checked = st.checkbox("", value=checked, key=key)
            st.session_state.progress[key] = checked
        with col2:
            st.markdown(f"[Project Link]({project})")
    return projects

def calculate_day_progress(selected_day, lectures, projects):
    lecture_progress = sum([1 for lecture in lectures if st.session_state.progress.get(f"{selected_day}_lecture_{lecture}", False)])
    project_progress = sum([1 for project in projects if st.session_state.progress.get(f"{selected_day}_project_{project}", False)])
    total_items = len(lectures) + len(projects)
    completed_items = lecture_progress + project_progress
    day_progress = (completed_items / total_items) * 100 if total_items > 0 else 0
    return day_progress

def calculate_overall_progress(df, days):
    total_items_overall = 0
    completed_items_overall = 0
    for day in days:
        day_data = df[df['Day'] == day]
        lectures = day_data['Lecture'].dropna().unique()
        projects = day_data['Project'].dropna().unique()
        total_items_day = len(lectures) + len(projects)
        total_items_overall += total_items_day
        for lecture in lectures:
            key = f"{day}_lecture_{lecture}"
            if st.session_state.progress.get(key, False):
                completed_items_overall += 1
        for project in projects:
            key = f"{day}_project_{project}"
            if st.session_state.progress.get(key, False):
                completed_items_overall += 1
    overall_progress = (completed_items_overall / total_items_overall) * 100 if total_items_overall > 0 else 0
    return overall_progress

def main():
    st.title("Python Learning Schedule")
    st.subheader("Lectures and Projects for Each Day")

    df = load_data()

    # Initialize session_state for checkboxes if not present
    if 'progress' not in st.session_state:
        st.session_state.progress = load_progress()

    # Sidebar for overall progress
    st.sidebar.title("Overall Progress")
    days = df['Day'].unique()
    overall_progress = calculate_overall_progress(df, days)
    st.sidebar.progress(overall_progress / 100)
    st.sidebar.write(f"**{overall_progress:.2f}% Completed**")

    # Button to reset progress
    if st.sidebar.button("Reset Progress"):
        st.session_state.progress = {}
        save_progress()
        st.experimental_rerun()

    # Dropdown to select a day
    selected_day = st.selectbox("Select a Day", days)

    # Filter the data for the selected day
    day_data = df[df['Day'] == selected_day]

    # Display lectures and projects
    lectures = display_lectures(day_data, selected_day)
    projects = display_projects(day_data, selected_day)

    # Calculate and display progress for the selected day
    day_progress = calculate_day_progress(selected_day, lectures, projects)
    st.write(f"### Progress for {selected_day}")
    st.progress(day_progress / 100)
    st.write(f"**{day_progress:.2f}% Completed**")

    # Save progress when checkboxes change
    save_progress()

if __name__ == '__main__':
    main()
