import streamlit as st
import pandas as pd
from database import (
    add_volunteer, log_shift, log_feedback, calculate_points, check_rewards,
    get_volunteer_id, cursor
)

def display_points_chart():
    '''
    Creates a bar chart of volunteer points
    '''
    cursor.execute("SELECT volunteer_name, points FROM volunteers")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Name", "Points"])
    st.bar_chart(df.set_index("Name"))

def export_volunteer_data():
    # Fetch data from the database
    cursor.execute('''
        SELECT v.volunteer_id, v.volunteer_name, 
               SUM(s.hours_worked) AS total_hours,
               COALESCE(SUM(CASE WHEN f.feedback_score >= 3 THEN f.feedback_score ELSE 0 END), 0) AS positive_feedback,
               v.points
        FROM volunteers v
        LEFT JOIN shifts s ON v.volunteer_id = s.volunteer_id
        LEFT JOIN feedback f ON v.volunteer_id = f.volunteer_id
        GROUP BY v.volunteer_id
    ''')
    data = cursor.fetchall()
    
    # Convert data into a Pandas DataFrame
    df = pd.DataFrame(data, columns=["Volunteer ID", "Volunteer Name", "Total Hours", "Positive Feedback", "Points"])
    
    # Generate a CSV file
    csv_data = df.to_csv(index=False)
    
    # Create a Streamlit download button
    st.download_button(
        label="Download Volunteer Data as CSV",
        data=csv_data,
        file_name="volunteer_data.csv",
        mime="text/csv"
    )
    
def supportscore_ui():
    '''
    StreamLit UI for the SupportScore Tracker
    '''
    st.title("SupportScore Tracker")
    tab1, tab2, tab3 = st.tabs(["Log Shift", "Log Feedback", "View Volunteers"])

    # Log Shift
    with tab1:
        st.subheader("Log Shift")
        volunteer_name = st.text_input("Volunteer Name", key="volunteer_name_shift")
        shift_date = st.date_input("Shift Date", key="shift_date_shift")
        hours_worked = st.number_input("Hours Worked", min_value=1, step=1, key="hours_worked_shift")
        if st.button("Submit Shift", key="submit_shift"):
            if volunteer_name.strip() == '':
                st.error("Please enter a volunteer name.")
            else:
                volunteer_id = add_volunteer(volunteer_name)
                log_shift(volunteer_id, shift_date.strftime("%Y-%m-%d"), hours_worked)
                calculate_points(volunteer_id)
                st.success("Shift logged successfully!")

    # Log Feedback
    with tab2:
        st.subheader("Log Feedback")
        volunteer_name = st.text_input("Volunteer Name", key="volunteer_name_feedback")
        student_id = st.number_input("Student ID", min_value=1, step=1, key="student_id_feedback")
        shift_id = st.number_input("Shift ID", min_value=1, step=1, key="shift_id_feedback")
        feedback_score = st.slider("Feedback Score (1-5)", min_value=1, max_value=5, step=1, key="feedback_score_feedback")
        if st.button("Submit Feedback", key="submit_feedback"):
            volunteer_id = get_volunteer_id(volunteer_name)
            if volunteer_id is None:
                st.error("Volunteer not found. Please ensure the volunteer name is correct.")
            else:
                log_feedback(volunteer_id, student_id, shift_id, feedback_score)
                st.success("Feedback logged successfully!")

    # View Volunteers details
    with tab3:
        st.subheader("Volunteer Details")
        cursor.execute('''SELECT v.volunteer_id, v.volunteer_name, 
                                SUM(s.hours_worked) AS total_hours,
                                COALESCE(SUM(CASE WHEN f.feedback_score >= 3 THEN f.feedback_score ELSE 0 END), 0) AS positive_feedback,
                                v.points
                        FROM volunteers v
                        LEFT JOIN shifts s ON v.volunteer_id = s.volunteer_id
                        LEFT JOIN feedback f ON v.volunteer_id = f.volunteer_id
                        GROUP BY v.volunteer_id''')
        volunteers = cursor.fetchall()
        
        # Display points chart
        display_points_chart()
        
        # Export Volunteer Data
        st.subheader("Export Volunteer Data")
        export_volunteer_data()
        
        # Display volunteer details
        if volunteers:
            for volunteer in volunteers:
                volunteer_id, volunteer_name, total_hours, positive_feedback, points = volunteer
                total_hours = total_hours or 0
                positive_feedback = positive_feedback or 0
                points = points or 0

                st.subheader(f"Volunteer: {volunteer_name}")
                st.write(f'Volunteer ID: **{volunteer_id}**')
                st.write(f"Hours Worked: **{total_hours} hours**")
                st.write(f"Total Points: **{points}**")
                st.write("---")
        else:
            st.info("No volunteers found.")

