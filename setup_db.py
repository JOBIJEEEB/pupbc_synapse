import os
import getpass
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import Admin

app = create_app()

def setup():
    with app.app_context():
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'pupbc.db')
        
        print("\nINITIALIZING SQLITE DATABASE...")
        print(f"   Location: {db_path}")

        db.create_all()
        print("Database tables created successfully.")

        if not Admin.query.first():
            print("\nCREATE ADMIN ACCOUNT")
            print("-----------------------")
            username = input("Enter Username: ").strip()
            password = getpass.getpass("Enter Password: ")
            
            hashed_pw = generate_password_hash(password)
            new_admin = Admin(username=username, password_hash=hashed_pw)
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ Admin '{username}' created.")
        else:
            print("Admin account already exists. Skipping creation.")

        print("\nSETUP COMPLETE! You can now run the app.")

if __name__ == "__main__":
    setup()