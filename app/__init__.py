from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',  # Point to the templates directory at root level
                static_folder='../static')  # Also point to the static directory at root level
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-local')  # Required for session handling

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_planner.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CSRF Protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = 'your-csrf-secret-key'  # Change this to a secure secret key

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Initialize routes
    from app.routes import init_routes
    init_routes(app)

    return app 