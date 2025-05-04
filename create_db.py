from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os
from flask_migrate import upgrade

def init_db():
    app = create_app()
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        # Run any pending migrations
        upgrade()
        
        # Check if we already have users
        if User.query.first() is None:
            print("Creating initial admin user...")
            # Create an admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Database already contains users.")

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialization complete!") 