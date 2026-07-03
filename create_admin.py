import os
import sys
from sqlalchemy.orm import Session

# Add current directory to path to resolve app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin():
    print("--- Create Admin / Superuser ---")
    db: Session = SessionLocal()
    try:
        email = input("Enter admin email: ").strip()
        if not email:
            print("Error: Email cannot be empty.")
            return

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            if existing_user.is_superuser:
                print(f"User '{email}' is already an admin/superuser.")
                return
            
            confirm = input(
                f"User '{email}' exists but is not an admin. Promote to admin? (y/n): "
            ).strip().lower()
            if confirm == 'y':
                existing_user.is_superuser = True
                db.commit()
                print(f"Successfully promoted user '{email}' to admin/superuser.")
            else:
                print("Operation cancelled.")
            return

        password = input("Enter admin password: ").strip()
        if not password or len(password) < 6:
            print("Error: Password must be at least 6 characters.")
            return

        full_name = input("Enter full name (optional): ").strip()
        if not full_name:
            full_name = "Admin User"

        # Create user
        new_admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True,
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print(f"Successfully created admin user: {email}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
