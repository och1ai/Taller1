from app.core.database import SessionLocal, engine, Base
from app.crud.user import user
from app.schemas.user import UserCreate
import logging

def seed_data():
    """Seed the database with initial data."""
    db = SessionLocal()
    try:
        # Recrear las tablas para empezar desde cero
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
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

        # Crear usuarios con sus roles correspondientes
        for i, user_in in enumerate(users):
            # El primer usuario (Admin User) será administrador
            is_admin = i == 0
            user.create(db, obj_in=user_in, is_admin=is_admin)
            print(f"Created user: {user_in.email} (admin: {is_admin})")
        
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
