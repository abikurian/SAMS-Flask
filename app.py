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
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM students ORDER BY id")
        students = cur.fetchall()
    conn.close()
    return render_template('students.html', students=students)

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
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM subjects ORDER BY id")
        subjects = cur.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

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
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT a.*, s.name AS student_name, sub.name AS subject_name FROM attendance a JOIN students s ON a.student_id=s.id JOIN subjects sub ON a.subject_id=sub.id ORDER BY a.date DESC")
        rows = cur.fetchall()
    conn.close()
    return render_template('attendance.html', attendance=rows)

@app.route('/attendance/mark', methods=['GET','POST'])
def mark_attendance():
    conn = get_connection()
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        date_str = request.form['date']
        present_ids = request.form.getlist('present')  # list of student ids present
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        with conn.cursor() as cur:
            # delete existing for subject+date to allow re-marking
            cur.execute("DELETE FROM attendance WHERE subject_id=%s AND date=%s", (subject_id, date_obj))
            # insert for all students: if in present_ids -> P else A
            cur.execute("SELECT id FROM students")
            all_students = [r['id'] for r in cur.fetchall()]
            for sid in all_students:
                status = 'P' if str(sid) in present_ids else 'A'
                cur.execute("INSERT INTO attendance (student_id, subject_id, date, status) VALUES (%s,%s,%s,%s)", (sid,subject_id,date_obj,status))
        conn.commit()
        conn.close()
        flash('Attendance saved','success')
        return redirect(url_for('attendance'))
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM subjects")
            subjects = cur.fetchall()
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
        conn.close()
        today = datetime.today().strftime('%Y-%m-%d')
        return render_template('mark_attendance.html', subjects=subjects, students=students, today=today)

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
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT m.*, s.name AS student_name, sub.name AS subject_name FROM marks m JOIN students s ON m.student_id=s.id JOIN subjects sub ON m.subject_id=sub.id ORDER BY m.id DESC")
        rows = cur.fetchall()
    conn.close()
    return render_template('marks.html', marks=rows)

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
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            cur.execute("SELECT * FROM subjects")
            subjects = cur.fetchall()
        conn.close()
        return render_template('add_marks.html', students=students, subjects=subjects)

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
    # simple: attendance % per student for selected subject (default all)
    conn = get_connection()
    with conn.cursor() as cur:
        # attendance % overall per student
        cur.execute("""
            SELECT s.id, s.name,
             SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) AS present,
             COUNT(a.id) AS total
            FROM students s
            LEFT JOIN attendance a ON s.id=a.student_id
            GROUP BY s.id, s.name
            ORDER BY s.id
        """)
        att_summary = cur.fetchall()
        # marks summary per student
        cur.execute("""
            SELECT s.id, s.name,
              IFNULL(SUM(m.marks_obtained),0) AS sum_marks,
              IFNULL(SUM(m.max_marks),0) AS sum_max
            FROM students s
            LEFT JOIN marks m ON s.id=m.student_id
            GROUP BY s.id, s.name
            ORDER BY s.id
        """)
        marks_summary = cur.fetchall()
    conn.close()
    # compute percent (avoid division by zero)
    for r in att_summary:
        total = r['total'] or 0
        r['percent'] = round((r['present']/total*100),2) if total>0 else None
    for r in marks_summary:
        if r['sum_max'] and r['sum_max']>0:
            r['percent'] = round((r['sum_marks']/r['sum_max']*100),2)
        else:
            r['percent'] = None
    return render_template('reports.html', att_summary=att_summary, marks_summary=marks_summary)

if __name__ == '__main__':
    app.run(debug=True)
