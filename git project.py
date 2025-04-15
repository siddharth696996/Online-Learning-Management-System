import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# DB Setup
conn = sqlite3.connect("lms.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    due_date TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    resource_link TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
''')
conn.commit()

# GUI
root = tk.Tk()
root.title("Online Learning Management System")
root.geometry("600x400")

def refresh_courses():
    course_list.delete(0, tk.END)
    cur.execute("SELECT * FROM courses")
    for row in cur.fetchall():
        course_list.insert(tk.END, f"{row[0]} - {row[1]}")

def add_course():
    name = simpledialog.askstring("Course Name", "Enter course name:")
    if name:
        try:
            cur.execute("INSERT INTO courses (name) VALUES (?)", (name,))
            conn.commit()
            refresh_courses()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course already exists!")

def delete_course():
    selection = course_list.curselection()
    if selection:
        course = course_list.get(selection[0])
        course_id = int(course.split(" - ")[0])
        cur.execute("DELETE FROM courses WHERE id=?", (course_id,))
        cur.execute("DELETE FROM assignments WHERE course_id=?", (course_id,))
        cur.execute("DELETE FROM materials WHERE course_id=?", (course_id,))
        conn.commit()
        refresh_courses()

def manage_assignments():
    selection = course_list.curselection()
    if not selection:
        return messagebox.showwarning("Select Course", "Select a course first.")
    course = course_list.get(selection[0])
    course_id = int(course.split(" - ")[0])

    def add_assignment():
        title = simpledialog.askstring("Assignment Title", "Enter title:")
        due = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
        if title and due:
            cur.execute("INSERT INTO assignments (course_id, title, due_date) VALUES (?, ?, ?)", (course_id, title, due))
            conn.commit()
            show_assignments()

    def show_assignments():
        assign_list.delete(0, tk.END)
        cur.execute("SELECT title, due_date FROM assignments WHERE course_id=?", (course_id,))
        for a in cur.fetchall():
            assign_list.insert(tk.END, f"{a[0]} (Due: {a[1]})")

    win = tk.Toplevel(root)
    win.title("Assignments")
    win.geometry("400x300")
    tk.Button(win, text="Add Assignment", command=add_assignment).pack()
    assign_list = tk.Listbox(win, width=50)
    assign_list.pack(pady=10)
    show_assignments()

def manage_materials():
    selection = course_list.curselection()
    if not selection:
        return messagebox.showwarning("Select Course", "Select a course first.")
    course = course_list.get(selection[0])
    course_id = int(course.split(" - ")[0])

    def add_material():
        title = simpledialog.askstring("Material Title", "Enter title:")
        link = simpledialog.askstring("Link or Filename", "Enter resource link:")
        if title and link:
            cur.execute("INSERT INTO materials (course_id, title, resource_link) VALUES (?, ?, ?)", (course_id, title, link))
            conn.commit()
            show_materials()

    def show_materials():
        mat_list.delete(0, tk.END)
        cur.execute("SELECT title, resource_link FROM materials WHERE course_id=?", (course_id,))
        for m in cur.fetchall():
            mat_list.insert(tk.END, f"{m[0]}: {m[1]}")

    win = tk.Toplevel(root)
    win.title("Materials")
    win.geometry("400x300")
    tk.Button(win, text="Add Material", command=add_material).pack()
    mat_list = tk.Listbox(win, width=50)
    mat_list.pack(pady=10)
    show_materials()

# Main UI
frame = tk.Frame(root)
frame.pack(pady=10)

course_list = tk.Listbox(frame, width=50, height=10)
course_list.pack(side=tk.LEFT, padx=10)

btn_frame = tk.Frame(frame)
btn_frame.pack(side=tk.LEFT)

tk.Button(btn_frame, text="Add Course", command=add_course).pack(pady=2)
tk.Button(btn_frame, text="Delete Course", command=delete_course).pack(pady=2)
tk.Button(btn_frame, text="Assignments", command=manage_assignments).pack(pady=2)
tk.Button(btn_frame, text="Materials", command=manage_materials).pack(pady=2)

refresh_courses()

root.mainloop()
