import os
import sys
from database import SessionLocal
from smartmama.models.person_model import Person
from smartmama.models.user_model import User
from smartmama.models.admin_model import Admin
from smartmama.security import hash_password 

def seed_superadmin():
    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.is_superadmin == True).first()
        if existing:
            print("A superadmin already exists — aborting, nothing created.")
            return

        email = os.environ["SUPERADMIN_EMAIL"]
        password = os.environ["SUPERADMIN_PASSWORD"]
        first_name = os.environ.get("SUPERADMIN_FIRST_NAME", "Super")
        last_name = os.environ.get("SUPERADMIN_LAST_NAME", "Admin")

        person = Person(first_name=first_name, last_name=last_name)
        db.add(person)
        db.flush()

        user = User(
            person_id=person.person_id,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.flush()

        admin = Admin(user_id=user.user_id, is_superadmin=True)
        db.add(admin)
        db.commit()
        print(f"Superadmin created: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_superadmin()