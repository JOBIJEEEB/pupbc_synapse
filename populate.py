import random
from datetime import date, timedelta
from app import create_app, db
from app.models import Student

# --- CONFIGURATION ---
COURSES = {
    "ACES": ["BSCpE", "DCPET"],
    "HRSS": ["BSBA-HRM"],
    "IBITS": ["BSIT", "DIT"],
    "JPIA": ["BSA"],
    "PIIE": ["BSIE"],
    "SMS": ["BSPSY"],
    "YES": ["BSED-ENG", "BSED-SS", "BEED"]
}

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Miguel", "Angela", "Javier", "Bea", "Francis", "Katrina", "Paolo", "Bianca"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]

def generate_student_id(year_level):
    base_year = 2026 - year_level
    sequence = random.randint(100, 99999)
    return f"{base_year}-{sequence:05d}-BN-0"

def generate_birthdate():
    start_date = date(2000, 1, 1)
    end_date = date(2006, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def populate():
    app = create_app()
    with app.app_context():
        # --- STEP 1: CLEAN OLD DATA (Optional but recommended) ---
        print("🧹 Cleaning old student records...")
        try:
            num_deleted = db.session.query(Student).delete()
            db.session.commit()
            print(f"   Deleted {num_deleted} old records.")
        except Exception as e:
            db.session.rollback()
            print(f"   Could not delete records: {e}")

        # --- STEP 2: ADD NEW DATA ---
        print("\n🚀 Starting population...")
        total_added = 0
        
        for org, course_list in COURSES.items():
            for course in course_list:
                print(f"   Processing {course}...", end="")
                
                for _ in range(10): # 10 students per course
                    year = random.randint(1, 4)
                    
                    # --- THE FIX ---
                    # Instead of "1-1", we just put "1"
                    # This matches standard dropdown values
                    section = str(random.randint(1, 2)) 
                    
                    fname = random.choice(FIRST_NAMES)
                    lname = random.choice(LAST_NAMES)
                    student_num = generate_student_id(year)
                    email = f"{fname.lower()}.{lname.lower()}@iskolarngbayan.pup.edu.ph"
                    bday = generate_birthdate()
                    
                    student = Student(
                        student_number=student_num,
                        first_name=fname,
                        middle_name="D.",
                        last_name=lname,
                        birthdate=bday,
                        email=email,
                        course=course,
                        year_level=year,   # Stored as Integer (1, 2, 3, 4)
                        section=section,   # Stored as String ("1", "2")
                        organization=org,
                        academic_year="AY 2025-2026",
                        residential_address="Biñan, Laguna",
                        emergency_contact_name="Parent Guardian",
                        emergency_address="Biñan, Laguna",
                        emergency_contact_number="09123456789",
                        validity_status="Validated",
                        photo_filename=None 
                    )
                    
                    db.session.add(student)
                    total_added += 1
                
                print(f" Done.")

        try:
            db.session.commit()
            print(f"\n✅ Success! Database reset and populated with {total_added} students.")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    populate()