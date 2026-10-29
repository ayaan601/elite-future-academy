from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'elite123'

# MySQL XAMPP Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'school_db'

mysql = MySQL(app)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrap(*a, **k):
        if 'user' not in session: return redirect('/login')
        return f(*a, **k)
    return wrap

@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cur.fetchone()[0]
    cur.close()
    return render_template('index.html', total_students=total_students, total_teachers=total_teachers)

# --- STUDENTS ---
@app.route('/students')
@login_required
def students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return render_template('students.html', students=data)

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        class_name = request.form['class_name']
        roll_no = request.form['roll_no']
        parent_name = request.form['parent_name']
        contact = request.form['contact']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, class_name, roll_no, parent_name, contact, admission_date) VALUES (%s,%s,%s,%s,%s,CURDATE())", (name, class_name, roll_no, parent_name, contact))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('students'))

@app.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('students'))

# --- TEACHERS ---
@app.route('/teachers')
@login_required
def teachers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teachers")
    data = cur.fetchall()
    cur.close()
    return render_template('teachers.html', teachers=data)

@app.route('/add_teacher', methods=['POST'])
@login_required
def add_teacher():
    name = request.form['name']
    subject = request.form['subject']
    email = request.form['email']
    contact = request.form['contact']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO teachers (name, subject, email, contact) VALUES (%s,%s,%s,%s)", (name, subject, email, contact))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('teachers'))

@app.route('/attendance')
@login_required
def attendance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT a.id, s.name, s.class_name, a.date, a.status FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.date DESC")
    att_data = cur.fetchall()
    cur.execute("SELECT id, name FROM students")
    studs = cur.fetchall()
    cur.close()
    return render_template('attendance.html', attendance=att_data, all_students=studs)

@app.route('/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s,%s,%s)", (request.form['student_id'], request.form['date'], request.form['status']))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('attendance'))

# --- FEES - YE MAIN FIX HAI ---
@app.route('/fees')
@login_required
def fees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT f.id, s.name, s.roll_no, f.total_fees, f.paid_fees, f.due_fees FROM fees f JOIN students s ON f.student_id = s.id ORDER BY f.id DESC")
    fees_data = cur.fetchall()
    cur.execute("SELECT id, name FROM students")
    studs = cur.fetchall()
    cur.close()
    return render_template('fees.html', fees=fees_data, all_students=studs)

@app.route('/add_fees', methods=['POST'])
@login_required
def add_fees():
    student_id = request.form['student_id']
    total_fees = int(request.form['total_fees'])
    paid_fees = int(request.form['paid_fees'])
    due_fees = total_fees - paid_fees
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO fees (student_id, total_fees, paid_fees, due_fees) VALUES (%s, %s, %s, %s)", (student_id, total_fees, paid_fees, due_fees))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('fees'))

# LOGIN SYSTEM
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        if u == 'admin' and p == 'admin123':
            session['user'] = 'admin'
            return redirect('/')
        else:
            return render_template('login.html', error="Galat Username ya Password!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)