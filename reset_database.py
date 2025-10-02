# reset_database.py

from app import app, db

def reset_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables have been dropped.")

        # Recreate all tables
        db.create_all()
        print("All tables have been recreated.")

if __name__ == "__main__":
    reset_db()
