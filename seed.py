from app import create_app, db
from app.models import Organization, Course, Section

app = create_app()

def seed_everything():
    with app.app_context():
        print("\nSTARTING DB SEED")

        org_data = [
            {
                "id": 1, "code": "ACES", "name": "Association of Computer Engineering Students",
                "color": "#800000", "grad": "linear-gradient(to right, #800000, #800000)",
                "logo": "aces.png", "header": "aces_header.png",
                "courses": [
                    {"code": "BSCpE", "name": "Bachelor of Science in Computer Engineering"},
                    {"code": "DCPET", "name": "Diploma in Computer Engineering Technology"}
                ]
            },
            {
                "id": 2, "code": "IBITS", "name": "Institute of Bachelors in Information Technology Studies",
                "color": "#058EA3", "grad": "linear-gradient(to right, #058EA3, #00d2ff)", 
                "logo": "ibits.png", "header": "ibits_header.png",
                "courses": [
                    {"code": "BSIT", "name": "Bachelor of Science in Information Technology"},
                    {"code": "DIT", "name": "Diploma in Information Technology"}
                ]
            },
            {
                "id": 3, "code": "YES", "name": "Young Educators Society",
                "color": "#090979", "grad": "linear-gradient(to right, #090979, #00d4ff)",
                "logo": "yes.png", "header": "yes_header.png",
                "courses": [
                    {"code": "BSED-ENG", "name": "Bachelor of Secondary Education Major in English"},
                    {"code": "BSED-SS", "name": "Bachelor of Secondary Education Major in Social Studies"},
                    {"code": "BEED", "name": "Bachelor of Elementary Education"}
                ]
            },
            {
                "id": 4, "code": "HRSS", "name": "Human Resource Students Society",
                "color": "#c0392b", "grad": "linear-gradient(to right, #c0392b, #e74c3c)",
                "logo": "hrss.png", "header": "hrss_header.png",
                "courses": [
                    {"code": "BSBA-HRM", "name": "Bachelor of Science in Business Administration Major in Human Resource Management"}
                ]
            },
            {
                "id": 5, "code": "JPIA", "name": "Junior Philippine Institute of Accountants",
                "color": "#FA7507", "grad": "linear-gradient(to right, #c0392b, #FA7507)",
                "logo": "jpia.png", "header": "jpia_header.png",
                "courses": [
                    {"code": "BSA", "name": "Bachelor of Science in Accountancy"}
                ]
            },
            {
                "id": 6, "code": "PIIE", "name": "Philippine Institute of Industrial Engineers",
                "color": "#16AB68", "grad": "linear-gradient(to right, #098A07, #2ecc71)",
                "logo": "piie.png", "header": "piie_header.png",
                "courses": [
                    {"code": "BSIE", "name": "Bachelor of Science in Industrial Engineering"}
                ]
            },
            {
                "id": 7, "code": "SMS", "name": "Samahan ng mga Mag-aaral ng Sikolohiya",
                "color": "#4F0580", "grad": "linear-gradient(to right, #4F0580, #bdc3c7)",
                "logo": "sms.png", "header": "sms_header.png",
                "courses": [
                    {"code": "BSPSY", "name": "Bachelor of Science in Psychology"}
                ]
            }
        ]

        for data in org_data:
            org = Organization.query.filter_by(code=data['code']).first()
            if not org:
                org = Organization(
                    code=data['code'],
                    name=data['name'],
                    color_primary=data['color'],
                    color_gradient=data['grad'],
                    logo_filename=data['logo'],
                    header_bg_filename=data['header']
                )
                db.session.add(org)
                db.session.commit()
                print(f"ORG CREATED: {data['code']}")
            else:
                print(f"Org {data['code']} already exists.")

            for c_data in data['courses']:
                course = Course.query.filter_by(code=c_data['code']).first()
                if not course:
                    course = Course(
                        code=c_data['code'],
                        name=c_data['name'],
                        org_id=org.id
                    )
                    db.session.add(course)
                    db.session.commit()
                    print(f"   Course Added: {c_data['code']}")

                standard_sections = ['1-1', '2-1', '3-1', '4-1']
                
                if c_data['code'] == 'BSCpE':
                    standard_sections.append('1-2')
                
                if c_data['code'] == 'BSBA-HRM':
                    standard_sections.extend(['1-2', '2-2', '3-2', '4-2'])

                for sec_name in standard_sections:
                    if sec_name.startswith('1'): yl = "1ST YEAR"
                    elif sec_name.startswith('2'): yl = "2ND YEAR"
                    elif sec_name.startswith('3'): yl = "3RD YEAR"
                    else: yl = "4TH YEAR"

                    sec = Section.query.filter_by(name=sec_name, course_id=course.id).first()
                    if not sec:
                        new_sec = Section(name=sec_name, year_level=yl, course_id=course.id)
                        db.session.add(new_sec)
                
                db.session.commit()
                print(f"      Sections synced.")

        print("\nSUCCESS! Database is fully populated with original data.")
if __name__ == "__main__":
    seed_everything()