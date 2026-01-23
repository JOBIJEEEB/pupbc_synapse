import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_student_photo(file, data):

    # folder structure:
    # uploads/photos/AY/Org/Course/Year/Section/Lastname_Firstname_StudentNum.ext

    ay = data.get('academic_year', 'AY 25-26') 
    org = data.get('organization')
    course = data.get('course')
    year = data.get('year_level')
    section = data.get('section')
    student_num = data.get('student_number')
    
    last = data.get('last_name', 'Unknown')
    first = data.get('first_name', 'Unknown')

    base_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'photos')
    target_folder = os.path.join(base_folder, ay, org, course, year, section)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    clean_last = secure_filename(last)
    clean_first = secure_filename(first)
    clean_num = secure_filename(student_num)
    
    file_ext = os.path.splitext(file.filename)[1]
    
    new_filename = f"{clean_last}_{clean_first}_{clean_num}{file_ext}"

    save_path = os.path.join(target_folder, new_filename)
    file.save(save_path)

    db_path = os.path.join('uploads', 'photos', ay, org, course, year, section, new_filename)
    return db_path.replace("\\", "/")