from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models
from app.core.security import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    user_email = "admin@example.com"
    user_password = "password"
    
    existing_user = db.query(models.User).filter(models.User.email == user_email).first()
    if not existing_user:
        print(f"Creating user: {user_email}")
        user = models.User(
            email=user_email,
            hashed_password=get_password_hash(user_password),
            full_name="Admin User",
            role="admin"
        )
        db.add(user)
        db.commit()
    else:
        print(f"User {user_email} already exists.")
    
    db.close()

if __name__ == "__main__":
    seed_db()
