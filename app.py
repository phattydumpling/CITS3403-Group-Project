from app import create_app, db
from flask_migrate import Migrate, upgrade
import os

app = create_app()
migrate = Migrate(app, db)

def init_db():
    # Create instance directory if it doesn't exist
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    with app.app_context():
        # Run any pending migrations
        upgrade()

if __name__ == '__main__':
    # Initialize database before running the app
    init_db()
    app.run(debug=True) 