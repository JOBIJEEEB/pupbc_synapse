from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False) 
    name = db.Column(db.String(100), nullable=False)          

    color_primary = db.Column(db.String(20), default="#2c3e50") 
    color_gradient = db.Column(db.String(150))                   
    
    logo_filename = db.Column(db.String(100))
    header_bg_filename = db.Column(db.String(100))

    courses = db.relationship('Course', backref='organization', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    code = db.Column(db.String(20), nullable=False) 
    name = db.Column(db.String(150), nullable=False) 
    
    sections = db.relationship('Section', backref='course', lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    year_level = db.Column(db.String(20), nullable=False) 
    name = db.Column(db.String(10), nullable=False)       


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    
    academic_year = db.Column(db.String(20), nullable=False, default='AY 25-26')
    organization = db.Column(db.String(50), nullable=False)   
    course = db.Column(db.String(100), nullable=False)        
    year_level = db.Column(db.String(20), nullable=False)     
    section = db.Column(db.String(20), nullable=False)        

    birthdate = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    residential_address = db.Column(db.Text, nullable=False)
    
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_address = db.Column(db.Text, nullable=False)
    emergency_contact_number = db.Column(db.String(20), nullable=False)

    validity_status = db.Column(db.String(100), default='Pending') 
    photo_filename = db.Column(db.String(255), nullable=True)
    barcode_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    change_requests = db.relationship('ChangeRequest', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.student_number}>'

# ADMIN TABLE
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# CHANGE REQUEST TABLE - note: not yet enforced, for future use nalang 'to
class ChangeRequest(db.Model):
    __tablename__ = 'change_requests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    field_to_change = db.Column(db.String(50), nullable=False)
    new_value = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    
    request_date = db.Column(db.DateTime, default=datetime.utcnow)