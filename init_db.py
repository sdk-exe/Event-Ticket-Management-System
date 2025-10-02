from app import app, db

# Create the database and the database table within the application context
with app.app_context():
    db.create_all()

print("Database initialized!")
