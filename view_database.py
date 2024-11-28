'''
This script was used to view the data in the database prior to implementing the streamlit UI.
'''
import sqlite3

conn = sqlite3.connect('volunteer_tracking.db')
cursor = conn.cursor()

# View all data from volunteers table
cursor.execute("SELECT * FROM volunteers")
volunteers = cursor.fetchall()

print("Volunteers in the database:")
for volunteer in volunteers:
    print(volunteer)
    
# View all data from shifts table
cursor.execute("SELECT * FROM shifts")
shifts = cursor.fetchall()

print("\nShifts in the database:")
for shift in shifts:
    print(shift)
    
# View all data from feedback table
cursor.execute("SELECT * FROM feedback")
feedback = cursor.fetchall()

print("\nFeedback in the database:")
for f in feedback:
    print(f)
    
conn.close()