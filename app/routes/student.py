from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import db, Student, Organization, Course, Section
from app.utils import save_student_photo
import json
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            s_num = request.form['student_number']
            if Student.query.filter_by(student_number=s_num).first():
                flash('Error: Student Number already registered!', 'danger')
                return redirect(url_for('student.register'))

            birthdate_str = request.form.get('birthdate')
            birthdate_obj = None
            if birthdate_str:
                try:
                    birthdate_obj = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Error: Invalid birthdate format!', 'danger')
                    return redirect(url_for('student.register'))

            photo_path = None
            if 'photo' in request.files:
                photo_file = request.files['photo']
                if photo_file.filename != '':
                    photo_path = save_student_photo(photo_file, request.form)

            new_student = Student(
                organization=request.form['organization'],
                course=request.form['course'],
                year_level=request.form['year_level'],
                section=request.form['section'],
                student_number=s_num,
                email=request.form['email'],
                first_name=request.form['first_name'],
                middle_name=request.form.get('middle_name', ''),
                last_name=request.form['last_name'],
                birthdate=birthdate_obj,
                residential_address=request.form['residential_address'],
                emergency_contact_name=request.form['emergency_contact_name'],
                emergency_contact_number=request.form['emergency_contact_number'],
                emergency_address=request.form['emergency_address'],
                photo_filename=photo_path,
                validity_status='Pending'
            )

            db.session.add(new_student)
            db.session.commit()
            flash('Registration Successful!', 'success')
            return redirect(url_for('student.register'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('student.register'))

    orgs = Organization.query.order_by(Organization.code).all()
    
    org_data = {}
    for org in orgs:
        courses = []
        for course in org.courses:
            courses.append({"code": course.code, "name": course.name})
        
        org_data[org.code] = {
            "name": org.name,
            "color": org.color_primary,
            "gradient": org.color_gradient,
            "header_bg": org.header_bg_filename,
            "logo": org.logo_filename,
            "courses": courses
        }

    section_data = {}
    all_sections = Section.query.join(Course).all()
    for sec in all_sections:
        course_code = sec.course.code
        year = sec.year_level
        if course_code not in section_data: section_data[course_code] = {}
        if year not in section_data[course_code]: section_data[course_code][year] = []
        section_data[course_code][year].append(sec.name)

    return render_template('student/register.html', 
                           org_data_json=json.dumps(org_data),
                           section_data_json=json.dumps(section_data))