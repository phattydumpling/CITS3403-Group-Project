from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',  # Point to the templates directory at root level
                static_folder='../static')  # Also point to the static directory at root level
    app.secret_key = 'your-secret-key'  # Required for session handling

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_planner.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CSRF Protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = 'your-csrf-secret-key'  # Change this to a secure secret key

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Initialize routes
    from app.routes import init_routes
    init_routes(app)

    return app 