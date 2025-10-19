# SAMS-Flask

**Student Attendance and Marks System (SAMS)** built with Flask and MySQL.

---

## Author
**Abi Kurian Varghese**

---

## Project Overview
SAMS-Flask is a web-based system to manage **student attendance** and **marks entry**. It allows you to:

- Mark attendance for students in different departments.
- View and filter attendance records by date and department.
- Enter and manage marks for various subjects.
- Generate **attendance and marks reports** per student and department.

---

## Features
1. **Attendance Management**
   - Mark attendance for students.
   - Filter attendance by date and department.
   - Automatically calculates absent/present status.

2. **Marks Management**
   - Enter marks for students for various subjects.
   - Filter marks by department and student.

3. **Reports**
   - Generate attendance summary for students (% attendance).
   - Generate marks summary for students (% of total marks).
   - Filter reports by department.

4. **Responsive UI**
   - Clean, modern, and dark-themed interface.
   - Works on desktops and tablets.

---

## Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 templates
- **Database:** MySQL
- **Version Control:** Git, GitHub

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/abikurian/SAMS-Flask.git
cd SAMS-Flask
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
3.Install Dependencies
```bash
pip install -r requirements.txt
```
4. Set up the database
Set up the database:

Create a MySQL database sams.

Run the SQL scripts to create tables (students, attendance, marks, subjects).

5. Run the app
python app.py
Access the application at http://127.0.0.1:5000


Usage

Mark Attendance: Navigate to /attendance/mark to mark daily attendance.

View Attendance: Navigate to /attendance to filter and view attendance records.

Enter Marks: Navigate to /marks/add to input marks for students.

Reports: Navigate to /reports to view attendance and marks summary.

Notes

Ensure your MySQL database credentials are correctly configured in app.py.

The system currently tracks attendance per student, not per subject.