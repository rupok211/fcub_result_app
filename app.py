from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Admin, Result, Subject
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fcub_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login first.', 'warning')
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True  # Save admin login status in session
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
        student_name = request.form['student_name']
        student_id = request.form['student_id']
        batch = request.form['batch']
        semester = request.form['semester']
        subject_names = request.form.getlist('subject_names[]')
        grades = request.form.getlist('grades[]')

        result = Result(student_name=student_name, student_id=student_id, batch=batch, semester=semester)
        db.session.add(result)
        db.session.commit()

        for name, grade in zip(subject_names, grades):
            subject = Subject(subject_name=name, grade=grade, result_id=result.id)
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
        result.student_name = request.form['student_name']
        result.student_id = request.form['student_id']
        result.batch = request.form['batch']
        result.semester = request.form['semester']

        # Delete old subjects
        Subject.query.filter_by(result_id=result.id).delete()

        subject_names = request.form.getlist('subject_names[]')
        grades = request.form.getlist('grades[]')
        for name, grade in zip(subject_names, grades):
            subject = Subject(subject_name=name, grade=grade, result_id=result.id)
            db.session.add(subject)

        db.session.commit()
        flash("Result updated successfully!", "success")
        return redirect(url_for('manage_results'))

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
        student_id = request.form['student_id']
        batch = request.form['batch']
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
        if not Admin.query.first():
            default_admin = Admin(username='admin', password=generate_password_hash('admin123'))
            db.session.add(default_admin)
            db.session.commit()
    app.run(debug=True)
