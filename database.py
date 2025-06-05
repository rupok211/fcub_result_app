from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    subjects = db.relationship('Subject', backref='result', cascade='all, delete-orphan')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))
