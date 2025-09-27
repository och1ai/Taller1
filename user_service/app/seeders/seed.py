from app.core.database import SessionLocal, engine, Base
from app.crud.user import user
from app.schemas.user import UserCreate

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    users = [
        UserCreate(
            full_name="Admin User",
            email="admin@perlametro.cl",
            password="Password123!",
        ),
        UserCreate(
            full_name="John Doe",
            email="john.doe@perlametro.cl",
            password="Password123!",
        ),
    ]

    for user_in in users:
        existing_user = user.get_user_by_email(db, email=user_in.email)
        if not existing_user:
            user.create(db, obj_in=user_in)
    
    db.close()

if __name__ == "__main__":
    seed_data()
