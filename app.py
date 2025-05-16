from app import create_app, db
from flask_migrate import Migrate, upgrade
import os

app = create_app()
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        # Run any pending migrations
        upgrade()

if __name__ == '__main__':
    # Initialize database before running the app
    init_db()
    app.run(debug=True) 