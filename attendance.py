import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askstring

# Initialize database with required tables
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    # Attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    # Professors table
    c.execute('''
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Students table for storing approved student IDs
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Function to register attendance if the student ID is valid
def register_attendance(student_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Check if student ID exists in students table
    c.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
    valid_student = c.fetchone()
    
    if not valid_student:
        messagebox.showerror("Error", "Student ID not registered.")
        conn.close()
        return
    
    # Check last status of the student (in or out)
    c.execute('''
        SELECT status FROM attendance 
        WHERE student_id = ? ORDER BY id DESC LIMIT 1
    ''', (student_id,))
    result = c.fetchone()
    
    # Determine new status
    new_status = 'in' if result is None or result[0] == 'out' else 'out'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert attendance record
    c.execute('''
        INSERT INTO attendance (student_id, status, timestamp)
        VALUES (?, ?, ?)
    ''', (student_id, new_status, timestamp))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", f"Successfully registered: {new_status} at {timestamp}")

# Function to manage students in professor profile
def manage_students():
    def add_student():
        student_id = askstring("Add Student", "Enter New Student ID:")
        if student_id:
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO students (student_id) VALUES (?)', (student_id,))
                conn.commit()
                messagebox.showinfo("Success", "Student ID added successfully.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Student ID already exists.")
            conn.close()

    def remove_student():
        student_id = askstring("Remove Student", "Enter Student ID to Remove:")
        if student_id:
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()
            c.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            if c.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Success", "Student ID removed successfully.")
            else:
                messagebox.showerror("Error", "Student ID not found.")
            conn.close()

    student_window = Toplevel(root)
    student_window.title("Manage Students")
    
    Button(student_window, text="Add Student", command=add_student).pack(pady=5)
    Button(student_window, text="Remove Student", command=remove_student).pack(pady=5)

# Function to login as professor
def professor_login(username, password):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM professors WHERE username = ? AND password = ?', (username, password))
    result = c.fetchone()
    conn.close()
    
    if result:
        manage_students()
    else:
        messagebox.showerror("Error", "Invalid credentials.")

# Function to register a professor
def register_professor():
    username = askstring("Register Professor", "Enter New Username:")
    password = askstring("Register Professor", "Enter New Password:")
    
    if username and password:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO professors (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Professor registered successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        
        conn.close()
    else:
        messagebox.showwarning("Warning", "Both username and password are required.")

# GUI setup
def open_student_entry():
    student_id = askstring("Student Entry", "Enter Student ID:")
    if student_id:
        register_attendance(student_id)

def open_professor_login():
    login_window = Toplevel(root)
    login_window.title("Professor Login")
    
    Label(login_window, text="Username:").pack()
    username_entry = Entry(login_window)
    username_entry.pack()
    
    Label(login_window, text="Password:").pack()
    password_entry = Entry(login_window, show="*")
    password_entry.pack()
    
    Button(login_window, text="Login", command=lambda: professor_login(username_entry.get(), password_entry.get())).pack()

# Main window setup
root = Tk()
root.title("Attendance System")
root.geometry("300x300")

Label(root, text="Welcome to the Attendance System", font=("Arial", 14)).pack(pady=10)

Button(root, text="Register Attendance", command=open_student_entry).pack(pady=5)
Button(root, text="Professor Login", command=open_professor_login).pack(pady=5)
Button(root, text="Register Professor", command=register_professor).pack(pady=5)
Button(root, text="Exit", command=root.quit).pack(pady=5)

# Initialize the database and start the GUI loop
init_db()
root.mainloop()
