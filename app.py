from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"

def get_connection():
    return pymysql.connect(host='localhost', user='root', password='root', database='sams_db', cursorclass=pymysql.cursors.DictCursor)

# Home / dashboard
@app.route('/')
def index():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c_students FROM students")
        students_count = cur.fetchone()['c_students']
        cur.execute("SELECT COUNT(*) AS c_subjects FROM subjects")
        subjects_count = cur.fetchone()['c_subjects']
    conn.close()
    return render_template('index.html', students_count=students_count, subjects_count=subjects_count)

# ---------------- Students ----------------
@app.route('/students')
def students():
    selected_dept = request.args.get('department')
    
    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        # Get students sorted by roll_no
        if selected_dept:
            cur.execute("SELECT * FROM students WHERE department=%s ORDER BY roll_no", (selected_dept,))
        else:
            cur.execute("SELECT * FROM students ORDER BY roll_no")
        students = cur.fetchall()

        # Get unique departments for dropdown
        cur.execute("SELECT DISTINCT department FROM students")
        departments = [d['department'] for d in cur.fetchall()]

    conn.close()
    return render_template('students.html', students=students, departments=departments, selected_dept=selected_dept)


@app.route('/students/add', methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        year = request.form['year'] or None
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO students (roll_no,name,department,year,email,phone) VALUES (%s,%s,%s,%s,%s,%s)",
                            (roll_no,name,department,year,email,phone))
            conn.commit()
            flash('Student added','success')
        except pymysql.err.IntegrityError:
            flash('Roll number already exists','danger')
        finally:
            conn.close()
        return redirect(url_for('students'))
    return render_template('add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET','POST'])
def edit_student(id):
    conn = get_connection()
    if request.method == 'POST':
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        year = request.form['year'] or None
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        with conn.cursor() as cur:
            cur.execute("UPDATE students SET roll_no=%s, name=%s, department=%s, year=%s, email=%s, phone=%s WHERE id=%s",
                        (roll_no,name,department,year,email,phone,id))
        conn.commit()
        conn.close()
        flash('Student updated','success')
        return redirect(url_for('students'))
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE id=%s", (id,))
            student = cur.fetchone()
        conn.close()
        if not student:
            flash('Not found','warning')
            return redirect(url_for('students'))
        return render_template('edit_student.html', student=student)

@app.route('/students/delete/<int:id>')
def delete_student(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Student deleted','success')
    return redirect(url_for('students'))

# ---------------- Subjects ----------------
@app.route('/subjects')
def subjects():
    selected_dept = request.args.get('department')

    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        if selected_dept:
            cur.execute("SELECT * FROM subjects WHERE department=%s ORDER BY department, name", (selected_dept,))
        else:
            cur.execute("SELECT * FROM subjects ORDER BY department, name")
        subjects = cur.fetchall()

        # Get unique departments for dropdown
        cur.execute("SELECT DISTINCT department FROM subjects")
        departments = [d['department'] for d in cur.fetchall()]

    conn.close()
    return render_template('subjects.html', subjects=subjects, departments=departments, selected_dept=selected_dept)



@app.route('/subjects/add', methods=['GET','POST'])
def add_subject():
    if request.method == 'POST':
        code = request.form['code'].strip()
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO subjects (code,name,department) VALUES (%s,%s,%s)", (code,name,department))
            conn.commit()
            flash('Subject added','success')
        except pymysql.err.IntegrityError:
            flash('Subject code already exists','danger')
        finally:
            conn.close()
        return redirect(url_for('subjects'))
    return render_template('add_subject.html')

@app.route('/subjects/edit/<int:id>', methods=['GET','POST'])
def edit_subject(id):
    conn = get_connection()
    if request.method == 'POST':
        code = request.form['code'].strip()
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        with conn.cursor() as cur:
            cur.execute("UPDATE subjects SET code=%s, name=%s, department=%s WHERE id=%s", (code,name,department,id))
        conn.commit()
        conn.close()
        flash('Subject updated','success')
        return redirect(url_for('subjects'))
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM subjects WHERE id=%s", (id,))
            subject = cur.fetchone()
        conn.close()
        if not subject:
            flash('Not found','warning')
            return redirect(url_for('subjects'))
        return render_template('edit_subject.html', subject=subject)

@app.route('/subjects/delete/<int:id>')
def delete_subject(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM subjects WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Subject deleted','success')
    return redirect(url_for('subjects'))

# ---------------- Attendance ----------------
@app.route('/attendance')
def attendance():
    selected_date = request.args.get('date')
    selected_dept = request.args.get('department')

    conn = get_connection()

    # Get unique departments
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT DISTINCT department FROM students ORDER BY department ASC")
        departments = [r['department'] for r in cur.fetchall()]

    # Build query without subject
    query = """
        SELECT s.roll_no, s.name AS student_name, s.department, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
    """
    conditions = []
    params = []

    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            conditions.append("a.date = %s")
            params.append(date_obj)
        except ValueError:
            pass

    if selected_dept:
        conditions.append("s.department = %s")
        params.append(selected_dept)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.roll_no ASC"

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    conn.close()
    return render_template(
        'attendance.html', attendance=rows, departments=departments,
        selected_date=selected_date, selected_dept=selected_dept
    )


@app.route('/attendance/mark', methods=['GET','POST'])
def mark_attendance():
    conn = get_connection()
    if request.method == 'POST':
        department = request.form['department']
        date_str = request.form['date']
        present_ids = request.form.getlist('present')  # list of checked student IDs
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        with conn.cursor() as cur:
            # Delete existing attendance for that date and department
            cur.execute("""
                DELETE a FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.date=%s AND s.department=%s
            """, (date_obj, department))

            # Get all students in the department
            cur.execute("SELECT id FROM students WHERE department=%s ORDER BY roll_no ASC", (department,))
            all_students = [r['id'] for r in cur.fetchall()]

            # Insert attendance
            for sid in all_students:
                # present_ids are strings, sid is int, so convert sid to str
                status = 'P' if str(sid) in present_ids else 'A'
                cur.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                    (sid, date_obj, status)
                )

        conn.commit()
        conn.close()
        flash('Attendance saved successfully!', 'success')
        return redirect(url_for('attendance'))

    else:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch departments
            cur.execute("SELECT DISTINCT department FROM students ORDER BY department ASC")
            departments = [r['department'] for r in cur.fetchall()]

            # Fetch students
            cur.execute("SELECT * FROM students ORDER BY department, roll_no ASC")
            students = cur.fetchall()

        conn.close()
        today = datetime.today().strftime('%Y-%m-%d')
        return render_template('mark_attendance.html', students=students, departments=departments, today=today)


@app.route('/attendance/delete/<int:id>')
def delete_attendance(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM attendance WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Attendance record deleted','success')
    return redirect(url_for('attendance'))

# ---------------- Marks ----------------
@app.route('/marks')
def marks():
    selected_subject = request.args.get('subject')
    
    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        marks = []
        if selected_subject:
            query = """
                SELECT m.id, s.name AS student_name, s.roll_no, s.department, sub.name AS subject_name,
                       m.subject_id, m.exam_type, m.marks_obtained, m.max_marks
                FROM marks m
                JOIN students s ON m.student_id = s.id
                JOIN subjects sub ON m.subject_id = sub.id
                WHERE m.subject_id = %s
                ORDER BY s.roll_no
            """
            cur.execute(query, (selected_subject,))
            marks = cur.fetchall()

        # Get subjects for dropdown
        cur.execute("SELECT * FROM subjects")
        subjects = cur.fetchall()

    conn.close()
    return render_template('marks.html', marks=marks, subjects=subjects,
                           selected_subject=selected_subject)




@app.route('/marks/add', methods=['GET','POST'])
def add_marks():
    conn = get_connection()
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        exam_type = request.form['exam_type']
        marks_obtained = request.form['marks_obtained'] or None
        max_marks = request.form['max_marks'] or None

        with conn.cursor() as cur:
            cur.execute("INSERT INTO marks (student_id,subject_id,exam_type,marks_obtained,max_marks) VALUES (%s,%s,%s,%s,%s)",
                        (student_id,subject_id,exam_type,marks_obtained,max_marks))
        conn.commit()
        conn.close()
        flash('Marks added','success')
        return redirect(url_for('marks'))

    else:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            cur.execute("SELECT * FROM subjects")
            subjects = cur.fetchall()
            cur.execute("SELECT DISTINCT department FROM students")
            departments = [d['department'] for d in cur.fetchall()]
        conn.close()
        return render_template('add_marks.html', students=students, subjects=subjects, departments=departments)








@app.route('/marks/delete/<int:id>')
def delete_marks(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM marks WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Marks deleted','success')
    return redirect(url_for('marks'))

# ---------------- Reports ----------------
@app.route('/reports')
def reports():
    selected_dept = request.args.get('department')

    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        # Fetch departments for dropdown
        cur.execute("SELECT DISTINCT department FROM students ORDER BY department ASC")
        departments = [r['department'] for r in cur.fetchall()]

        att_summary = []
        marks_summary = []

        if selected_dept:
            # Attendance summary for selected department
            cur.execute("""
                SELECT s.id, s.name,
                 SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) AS present,
                 COUNT(a.id) AS total
                FROM students s
                LEFT JOIN attendance a ON s.id=a.student_id
                WHERE s.department=%s
                GROUP BY s.id, s.name
                ORDER BY s.id
            """, (selected_dept,))
            att_summary = cur.fetchall()

            # Marks summary for selected department
            cur.execute("""
                SELECT s.id, s.name,
                  IFNULL(SUM(m.marks_obtained),0) AS sum_marks,
                  IFNULL(SUM(m.max_marks),0) AS sum_max
                FROM students s
                LEFT JOIN marks m ON s.id=m.student_id
                WHERE s.department=%s
                GROUP BY s.id, s.name
                ORDER BY s.id
            """, (selected_dept,))
            marks_summary = cur.fetchall()

    conn.close()

    # Compute percentages
    for r in att_summary:
        total = r['total'] or 0
        r['percent'] = round((r['present']/total*100),2) if total>0 else None

    for r in marks_summary:
        r['percent'] = round((r['sum_marks']/r['sum_max']*100),2) if r['sum_max'] and r['sum_max']>0 else None

    return render_template('reports.html', 
                           departments=departments,
                           selected_dept=selected_dept,
                           att_summary=att_summary,
                           marks_summary=marks_summary)


if __name__ == '__main__':
    app.run(debug=True)
