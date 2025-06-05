from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Admin, Result, Subject
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fcub_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Decorator to require admin login
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login first.', 'warning')
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return wrapper

# Validation: subject names only letters, numbers, spaces; grade must be in allowed set
def is_valid_subject_and_grade(subject, grade):
    valid_subject = re.match(r'^[a-zA-Z0-9\s]+$', subject)
    valid_grades = {'A+', 'A', 'A-', 'B+', 'B', 'C', 'D', 'F'}
    return bool(valid_subject) and grade in valid_grades

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True
            flash('Logged in successfully.', 'success')
            return redirect(url_for('manage_results'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/admin/result', methods=['GET', 'POST'])
@admin_required
def admin_result():
    if request.method == 'POST':
        student_name = request.form['student_name'].strip()
        student_id = request.form['student_id'].strip()
        batch = request.form['batch'].strip()
        semester = request.form['semester'].strip()
        subject_names = request.form.getlist('subject_names[]')
        grades = request.form.getlist('grades[]')

        # Validate each subject and grade
        for name, grade in zip(subject_names, grades):
            if not is_valid_subject_and_grade(name.strip(), grade.strip()):
                flash("Invalid subject or grade format. Subjects: letters, numbers, spaces. Grades: A+, A, A-, B+, B, C, D, F only.", "danger")
                return redirect(url_for('admin_result'))

        # Create and save result
        result = Result(student_name=student_name, student_id=student_id, batch=batch, semester=semester)
        db.session.add(result)
        db.session.commit()

        # Save subjects for result
        for name, grade in zip(subject_names, grades):
            subject = Subject(subject_name=name.strip(), grade=grade.strip(), result_id=result.id)
            db.session.add(subject)

        db.session.commit()
        flash("Result added successfully!", "success")
        return redirect(url_for('manage_results'))

    return render_template('admin_result.html')

@app.route('/admin/manage-results')
@admin_required
def manage_results():
    results = Result.query.all()
    return render_template('admin_manage_results.html', results=results)

@app.route('/admin/edit-result/<int:result_id>', methods=['GET', 'POST'])
@admin_required
def edit_result(result_id):
    result = Result.query.get_or_404(result_id)

    if request.method == 'POST':
        result.student_name = request.form['student_name'].strip()
        result.student_id = request.form['student_id'].strip()
        result.batch = request.form['batch'].strip()
        result.semester = request.form['semester'].strip()

        subject_names = request.form.getlist('subject_names[]')
        grades = request.form.getlist('grades[]')

        # Validate inputs again
        for name, grade in zip(subject_names, grades):
            if not is_valid_subject_and_grade(name.strip(), grade.strip()):
                flash("Invalid subject or grade format. Subjects: letters, numbers, spaces. Grades: A+, A, A-, B+, B, C, D, F only.", "danger")
                return redirect(url_for('edit_result', result_id=result.id))

        # Delete old subjects
        Subject.query.filter_by(result_id=result.id).delete()

        # Add new subjects
        for name, grade in zip(subject_names, grades):
            subject = Subject(subject_name=name.strip(), grade=grade.strip(), result_id=result.id)
            db.session.add(subject)

        db.session.commit()
        flash("Result updated successfully!", "success")
        return redirect(url_for('manage_results'))

    # Load subjects to prefill form
    subjects = Subject.query.filter_by(result_id=result.id).all()
    return render_template('admin_add_edit_result.html', result=result, subjects=subjects)

@app.route('/admin/delete-result/<int:result_id>', methods=['POST'])
@admin_required
def delete_result_route(result_id):
    result = Result.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash("Result deleted successfully!", "success")
    return redirect(url_for('manage_results'))

@app.route('/view-result', methods=['GET', 'POST'])
def view_result():
    if request.method == 'POST':
        student_id = request.form['student_id'].strip()
        batch = request.form['batch'].strip()
        result = Result.query.filter_by(student_id=student_id, batch=batch).first()
        if result:
            return render_template('student_result.html', result=result)
        else:
            flash("Result not found", "danger")
            return redirect(url_for('view_result'))
    return render_template('view_result.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if none exists
        if not Admin.query.first():
            default_admin = Admin(username='admin', password=generate_password_hash('admin123'))
            db.session.add(default_admin)
            db.session.commit()
    app.run(debug=True)
