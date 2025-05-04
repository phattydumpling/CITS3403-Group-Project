from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def test_database():
    app = create_app()
    with app.app_context():
        # Create a test user
        test_user = User(
            username='testuser2',
            email='test2@example.com',
            password=generate_password_hash('testpass123')
        )
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("Successfully created test user!")
            
            # Verify we can query the user
            user = User.query.filter_by(username='testuser2').first()
            if user:
                print(f"Successfully retrieved user: {user.username}")
                print(f"Email: {user.email}")
                print(f"Created at: {user.created_at}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    test_database() 