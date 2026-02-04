import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, jsonify
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, func
from app.models import db, Admin, Student, Organization, Course, Section
import json
import csv
import io
import subprocess
from flask import Response, stream_with_context
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please login muna po :)", "danger")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        suspicious_patterns = [
            "'", '"', "--", ";", "/*", "#",
            "OR 1=1", "OR '1'='1", "OR TRUE",
            "UNION", "SELECT", "DROP", "DELETE", "UPDATE", "INSERT", "TABLE", "FROM",
            "INFORMATION_SCHEMA", "SYSOBJECTS", "@@VERSION",
            "SLEEP", "WAITFOR", "BENCHMARK",
            "<SCRIPT", "JAVASCRIPT", "ALERT(", "ONERROR", "IMG SRC"
        ]
        u_upper = username.upper()
        p_upper = password.upper()

        for pattern in suspicious_patterns:
            if pattern in u_upper or pattern in p_upper:
                print(f"Hacking attempt detected! IP: {request.remote_addr}. Pattern: {pattern}")
                return redirect(url_for("admin.troll_page"))

        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('admin.login'))
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    organizations = Organization.query.order_by(Organization.code).all()
    stats_query = db.session.query(
        Student.course,
        func.count(Student.id)
    ).group_by(Student.course).all()
    course_counts = {course: count for course, count in stats_query}
    return render_template('admin/dashboard.html', organizations=organizations, course_counts=course_counts)

@admin_bp.route('/course/<string:course_name>')
@login_required
def view_course(course_name):
    course_obj = Course.query.filter_by(name=course_name).first()
    course_code = course_obj.code if course_obj else course_name

    students = Student.query.filter(
        or_(
            Student.course == course_name,
            Student.course == course_code
        )
    ).all()

    total_registered = len(students)
    section_counts = {}

    grouped_data = {}
    for student in students:
        year = student.year_level
        section = student.section

        section_counts[section] = section_counts.get(section, 0) + 1

        if year not in grouped_data:
            grouped_data[year] = {}

        if section not in grouped_data[year]:
            grouped_data[year][section] = []

        grouped_data[year][section].append(student)

    sorted_grouped_data = {
        year: dict(sorted(sections.items()))
        for year, sections in sorted(grouped_data.items())
    }
    course = Course.query.filter_by(name=course_name).first()
    org = course.organization if course else None

    return render_template('admin/course_view.html',
                           course_name=course_name,
                           grouped_data=sorted_grouped_data,
                           course_code=course_code,
                           org=org,
                           total_registered=total_registered,
                           section_counts=section_counts)

@admin_bp.route('/generate_id/<int:id>')
@login_required
def generate_id(id):
    student = Student.query.get_or_404(id)

    course_obj = Course.query.filter_by(code=student.course).first()

    student.full_course_name = course_obj.name if course_obj else student.course
    return render_template('admin/id_card.html', students=[student])


@admin_bp.route('/batch_print', methods=['POST'])
@login_required
def batch_print():
    ids = request.form.getlist('student_ids')
    if not ids:
        flash('No students selected!', 'warning')
        return redirect(request.referrer)
    students = Student.query.filter(Student.id.in_(ids)).order_by(Student.last_name).all()
    all_courses = {c.code: c.name for c in Course.query.all()}

    for s in students:
        s.full_course_name = all_courses.get(s.course, s.course)

    return render_template('admin/id_card.html', students=students)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('admin.login'))

@admin_bp.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        try:
            student.first_name = request.form['first_name']
            student.middle_name = request.form['middle_name']
            student.last_name = request.form['last_name']
            student.student_number = request.form['student_number']
            student.email = request.form['email']
            student.residential_address = request.form['residential_address']

            birthdate_str = request.form['birthdate']
            if birthdate_str:
                student.birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()

            student.organization = request.form['organization']
            student.course = request.form['course']
            student.year_level = request.form['year_level']
            student.section = request.form['section']
            student.emergency_contact_name = request.form['emergency_contact_name']
            student.emergency_contact_number = request.form['emergency_contact_number']
            student.emergency_address = request.form['emergency_address']

            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(current_app.root_path, 'static/uploads', filename)
                    file.save(save_path)
                    student.photo_filename = 'uploads/' + filename
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin.view_course', course_name=student.course))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')

    orgs = Organization.query.order_by(Organization.code).all()
    org_data = {org.code: {"courses": [{"code": c.code, "name": c.name} for c in org.courses]} for org in orgs}

    section_data = {}
    all_sections = Section.query.join(Course).all()
    for sec in all_sections:
        c_code = sec.course.code
        y_level = sec.year_level
        if c_code not in section_data: section_data[c_code] = {}
        if y_level not in section_data[c_code]: section_data[c_code][y_level] = []
        section_data[c_code][y_level].append(sec.name)

    return render_template('admin/edit_student.html',
                           student=student,
                           org_data_json=json.dumps(org_data),
                           section_data_json=json.dumps(section_data))

@admin_bp.route('/delete_student/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    course_name = student.course
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!')
    return redirect(request.referrer)

@admin_bp.route('/admin/delete_bulk', methods=['POST'])
@login_required
def delete_bulk():
    student_ids = request.form.getlist('student_ids')

    if not student_ids:
        flash('No students selected.', 'warning')
        return redirect(request.referrer)

    try:
        Student.query.filter(Student.id.in_(student_ids)).delete(synchronize_session=False)
        db.session.commit()

        flash(f'Successfully deleted {len(student_ids)} students.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting students: {str(e)}', 'danger')
    return redirect(request.referrer)

#  SETTINGS

@admin_bp.route('/settings')
@login_required
def settings():
    orgs = Organization.query.order_by(Organization.code).all()
    courses = Course.query.order_by(Course.code).all()

    raw_sections = Section.query.join(Course).order_by(Course.code, Section.year_level, Section.name).all()
    grouped_sections = {}
    for sec in raw_sections:
        key = f"{sec.course.code}|{sec.year_level}"
        if key not in grouped_sections:
            grouped_sections[key] = {"course_code": sec.course.code, "course_id": sec.course.id, "year_level": sec.year_level, "sections": []}
        grouped_sections[key]["sections"].append({"id": sec.id, "name": sec.name})
    return render_template('settings.html', orgs=orgs, courses=courses, grouped_sections=grouped_sections)

@admin_bp.route('/settings/add_org', methods=['POST'])
@login_required
def add_org():
    try:
        code = request.form['code'].upper()
        name = request.form['name']
        color_primary = request.form['color_primary']
        color_gradient = f"linear-gradient(to right, {color_primary}, {color_primary})"

        logo_filename = 'default_logo.png'
        header_filename = 'default_header.jpg'

        if 'logo' in request.files and request.files['logo'].filename != '':
            file = request.files['logo']
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.root_path, 'static/img/orgs')
            if not os.path.exists(save_path): os.makedirs(save_path)

            file.save(os.path.join(save_path, filename))
            logo_filename = filename

        if 'header_bg' in request.files and request.files['header_bg'].filename != '':
            file = request.files['header_bg']
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.root_path, 'static/img/orgs')
            file.save(os.path.join(save_path, filename))
            header_filename = filename

        new_org = Organization(
            code=code,
            name=name,
            color_primary=color_primary,
            color_gradient=color_gradient,
            logo_filename=logo_filename,
            header_bg_filename=header_filename
        )

        db.session.add(new_org)
        db.session.commit()

        flash(f"Organization '{code}' added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding organization: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/add_course', methods=['POST'])
@login_required
def add_course():
    try:
        org_id = request.form['org_id']
        code = request.form['code'].upper()
        name = request.form['name']

        new_course = Course(org_id=org_id, code=code, name=name)
        db.session.add(new_course)
        db.session.commit()

        for year in ["1ST YEAR", "2ND YEAR", "3RD YEAR", "4TH YEAR"]:
            db.session.add(Section(course_id=new_course.id, year_level=year, name="1-1"))
        db.session.commit()

        flash(f"Course '{code}' added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding course: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/add_section', methods=['POST'])
@login_required
def add_section():
    try:
        course_id = request.form['course_id']
        year_level = request.form['year_level']
        name = request.form['name']

        new_section = Section(course_id=course_id, year_level=year_level, name=name)
        db.session.add(new_section)
        db.session.commit()

        flash(f"Section '{name}' added!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding section: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

# DELETE ROUTES (Redirects)

@admin_bp.route('/settings/delete_org/<int:id>', methods=['POST'])
@login_required
def delete_org(id):
    try:
        org = Organization.query.get_or_404(id)
        courses = Course.query.filter_by(org_id=org.id).all()
        for course in courses:
            Section.query.filter_by(course_id=course.id).delete()
            db.session.delete(course)

        db.session.delete(org)
        db.session.commit()
        flash(f"Organization '{org.code}' deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting organization: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/delete_course/<int:id>', methods=['POST'])
@login_required
def delete_course(id):
    try:
        course = Course.query.get_or_404(id)
        Section.query.filter_by(course_id=course.id).delete()
        db.session.delete(course)
        db.session.commit()
        flash(f"Course '{course.code}' deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting course: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))


@admin_bp.route('/settings/delete_section/<int:id>', methods=['POST'])
@login_required
def delete_section(id):
    try:
        section = Section.query.get_or_404(id)
        name = section.name
        db.session.delete(section)
        db.session.commit()
        flash(f"Section '{name}' deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting section: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

# EDIT ROUTES (Redirects)

@admin_bp.route('/settings/edit_org/<int:id>', methods=['POST'])
@login_required
def edit_org(id):
    try:
        org = Organization.query.get_or_404(id)
        org.code = request.form['code']
        org.name = request.form['name']
        org.color_primary = request.form['color_primary']
        org.color_gradient = f"linear-gradient(to right, {org.color_primary}, {org.color_primary})"

        db.session.commit()
        flash(f"Organization '{org.code}' updated!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating org: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/edit_course/<int:id>', methods=['POST'])
@login_required
def edit_course(id):
    try:
        course = Course.query.get_or_404(id)
        course.code = request.form['code']
        course.name = request.form['name']
        course.org_id = request.form['org_id']

        db.session.commit()
        flash(f"Course '{course.code}' updated!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating course: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/edit_section/<int:id>', methods=['POST'])
@login_required
def edit_section(id):
    try:
        section = Section.query.get_or_404(id)
        section.name = request.form['name']
        section.year_level = request.form['year_level']
        section.course_id = request.form['course_id']

        db.session.commit()
        flash(f"Section '{section.name}' updated!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating section: {str(e)}", "danger")

    return redirect(url_for('admin.settings'))

@admin_bp.route('/export_csv_filtered')
@login_required
def export_csv_filtered():
    target_year = request.args.get('year')
    target_section = request.args.get('section')
    target_course_name = request.args.get('course_name')

    query = Student.query
    file_prefix = "StudentList"
    if target_year:
        query = query.filter_by(year_level=target_year)
    if target_section:
        query = query.filter_by(section=target_section)
    if target_course_name:
        course_obj = Course.query.filter_by(name=target_course_name).first()
        if course_obj:
            file_prefix = course_obj.code
            target_code = course_obj.code
        else:
            file_prefix = "UnknownCourse"
            target_code = target_course_name

        query = query.filter(
            or_(
                Student.course == target_course_name,
                Student.course == target_code
            )
        )
    students = query.order_by(Student.last_name).all()
    if not students:
        flash("No students found in that section.", "warning")
        return redirect(request.referrer)

    filename = f"{file_prefix}_{target_section}.csv"

    def generate():
        data = io.StringIO()
        w = csv.writer(data)

        w.writerow((
            'STUDNO',
            'LASTNAME',
            'MDLENAME',
            'FRSTNAME',
            'PROGCODE',
            'YRLVL',
            'SEC',
            'BRTHDATE',
            'RES_ADDRESS',
            'CONTACT_PERSON',
            'CONTACT_PERSON_ADDRESS',
            'CONTACT_PERSON_NUMBER',
            'FNMI'
        ))

        yield data.getvalue().encode('windows-1252', errors='replace')
        data.seek(0)
        data.truncate(0)

        for s in students:
            def clean(text):
                return str(text).strip().upper() if text else ""

            s_studno = clean(s.student_number)
            s_lname = clean(s.last_name)
            s_mname = clean(s.middle_name)
            s_fname = clean(s.first_name)

            if s_mname:
                s_fnmi = f"{s_fname} {s_mname[0]}."
            else:
                s_fnmi = s_fname

            w.writerow((
                s_studno,
                s_lname,
                s_mname,
                s_fname,
                clean(s.course),
                clean(s.year_level),
                clean(s.section),
                s.birthdate.strftime('%m/%d/%Y'),
                clean(s.residential_address),
                clean(s.emergency_contact_name),
                clean(s.emergency_address),
                str(s.emergency_contact_number),
                s_fnmi
            ))

            yield data.getvalue().encode('windows-1252', errors='replace')
            data.seek(0)
            data.truncate(0)

    response = Response(stream_with_context(generate()), mimetype='text/csv; charset=windows-1252')
    response.headers.set('Content-Disposition', 'attachment', filename=filename)
    return response

@admin_bp.route('/nice-try')
def troll_page():
    return render_template('admin/jb.html')

@admin_bp.route('/api/public_stats')
def public_stats():
    username = os.environ.get('USER')
    try:
        home_out = subprocess.check_output(['du', '-sb', f"/home/{username}"])
        total_bytes = int(home_out.split()[0])
        real_mb = round(total_bytes / (1024 * 1024), 1)
    except:
        real_mb = 0

    system_overhead = 16.0

    final_mb = real_mb + system_overhead
    quota_mb = 512.0

    username = os.environ.get('USER')
    total_bytes = 0
    try:
        total_bytes += int(subprocess.check_output(['du', '-sb', f"/home/{username}"]).split()[0])
        final_mb = round((total_bytes / (1024*1024)) + 16.0, 1)
    except:
        final_mb = 0

    course_counts = {}
    try:
        results = db.session.query(Student.course, func.count(Student.id)).group_by(Student.course).all()
        for course, count in results:
            course_counts[course] = count
    except:
        course_counts = {"Error": 0}

    lock_file = os.path.join(current_app.root_path, 'maintenance.lock')
    is_maintenance = os.path.exists(lock_file)

    return jsonify({
        'storage_mb': final_mb,
        'quota_mb': 512.0,
        'percent': round((final_mb/512.0)*100, 1),
        'courses': course_counts,
        'maintenance': is_maintenance
    })

@admin_bp.route('/api/toggle_maintenance', methods=['POST'])
def toggle_maintenance():
    if request.headers.get('X-Secret') != "ACES_COMMAND_KEY_2026":
        return jsonify({'error': 'Unauthorized'}), 403

    lock_file = os.path.join(current_app.root_path, 'maintenance.lock')

    action = request.json.get('action')

    if action == 'on':
        open(lock_file, 'a').close()
        return jsonify({'status': 'locked'})
    else:
        if os.path.exists(lock_file):
            os.remove(lock_file)
        return jsonify({'status': 'unlocked'})