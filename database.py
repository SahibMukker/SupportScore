import sqlite3

# Connect to database (or create one if it doesn't exist)
conn = sqlite3.connect('volunteer_tracking.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables for volunteers, shifts, and feedback
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS volunteers (
                        volunteer_id INTEGER PRIMARY KEY,
                        volunteer_name TEXT UNIQUE,
                        points INTEGER)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS shifts (
                        shift_id INTEGER PRIMARY KEY,
                        volunteer_id INTEGER,
                        shift_date TEXT,
                        hours_worked INTEGER,
                        FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        feedback_id INTEGER PRIMARY KEY,
                        volunteer_id INTEGER,
                        student_id INTEGER,
                        shift_id INTEGER,
                        feedback_score INTEGER,
                        FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id),
                        FOREIGN KEY (shift_id) REFERENCES shifts(shift_id))''')
    
    conn.commit()

def add_volunteer(volunteer_name):
    '''
    Adds volunteer to database
    
    Parameters:
        volunteer_name (str): Name of the volunteer
    '''
    # Check if the volunteer already exists by name
    cursor.execute("SELECT volunteer_id FROM volunteers WHERE volunteer_name = ?", (volunteer_name,))
    existing_volunteer = cursor.fetchone()

    if existing_volunteer:
        # If the volunteer exists, return their existing volunteer_id
        return existing_volunteer[0]
    else:
        # If the volunteer doesn't exist, insert them into the table
        cursor.execute("INSERT INTO volunteers (volunteer_name, points) VALUES (?, 0)", (volunteer_name,))
        conn.commit()
        
        # Return the volunteer_id of the newly inserted volunteer
        return cursor.lastrowid

def log_shift(volunteer_id, shift_date, hours_worked):
    '''
    Logs volunteer shift to database
    
    Parameters:
        volunteer_id (int): ID of the volunteer
        shift_date (str): Date of the shift
        hours_worked (int): Number of hours worked
    '''
    cursor.execute("INSERT INTO shifts (volunteer_id, shift_date, hours_worked) VALUES (?, ?, ?)", 
                   (volunteer_id, shift_date, hours_worked))
    conn.commit()

def log_feedback(volunteer_id, student_id, shift_id, feedback_score):
    '''
    Logs volunteer feedback to database
    
    Parameters:
        volunteer_id(int): ID of the volunteer
        student_id (int): ID of the student
        shift_id (int): ID of the shift
        feedback_score (int): Score of the feedback (out of 5)
    '''
    # Insert feedback into the feedback table
    cursor.execute("INSERT INTO feedback (volunteer_id, student_id, shift_id, feedback_score) VALUES (?, ?, ?, ?)",
                   (volunteer_id, student_id, shift_id, feedback_score))
    conn.commit()

    # Trigger points recalculation
    calculate_points(volunteer_id)

def calculate_points(volunteer_id):
    '''
    Calculates volunteer points based on shifts and feedback
    
    Parameters:
        volunteer_id (int): ID of the volunteer
    '''
    # Sum up the hours worked
    cursor.execute('''SELECT SUM(hours_worked) FROM shifts WHERE volunteer_id = ?''', (volunteer_id,))
    total_hours = cursor.fetchone()[0] or 0  # Default to 0 if no hours found
    
    # Sum up the feedback score (only count feedback >= 3)
    cursor.execute('''SELECT SUM(feedback_score) FROM feedback WHERE volunteer_id = ? AND feedback_score >= 3''', (volunteer_id,))
    positive_feedback = cursor.fetchone()[0] or 0  # Default to 0 if no feedback score >= 3
    
    # Calculate points: total hours + (positive_feedback * 5)
    points = total_hours + (positive_feedback * 5)
    
    # Update volunteer's points in the database
    cursor.execute("UPDATE volunteers SET points = ? WHERE volunteer_id = ?", (points, volunteer_id))
    conn.commit()

def check_rewards(volunteer_id):
    '''
    Checks if volunteer has earned a reward based on points
    
    Parameters:
        volunteer_id (int): ID of the volunteer
    '''
    cursor.execute("SELECT points FROM volunteers WHERE volunteer_id = ?", (volunteer_id,))
    points = cursor.fetchone()[0] or 0
    
    # Reward based on points threshold
    if points >= 100:
        print(f'Congrats! You have reached {points} points. You\'ve earned a reward!')

def get_volunteer_id(volunteer_name):
    '''
    Retrieves the volunteer_id for a given volunteer_name
    
    Parameters:
        volunteer_name (str): Name of the volunteer
    '''
    cursor.execute("SELECT volunteer_id FROM volunteers WHERE volunteer_name = ?", (volunteer_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Initialize database tables when the module is imported
create_tables()
