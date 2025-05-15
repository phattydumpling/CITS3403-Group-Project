from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from flask import url_for, current_app
from config import DeploymentConfig
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, 
                template_folder='../templates',  # Point to the templates directory at root level
                static_folder='../static')  # Also point to the static directory at root level

    # Load configuration
    app.config.from_object(DeploymentConfig)

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    csrf.init_app(app)  # Enable CSRF protection

    # Initialize routes
    from app.routes import init_routes
    init_routes(app)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Cache-busting static file helper
    def static_file(filename):
        # Get the absolute path to the static file
        static_folder = app.static_folder
        file_path = os.path.join(static_folder, filename)
        try:
            version = int(os.path.getmtime(file_path))
        except OSError:
            version = 0
        return url_for('static', filename=filename, v=version)

    app.jinja_env.globals['static_file'] = static_file

    return app