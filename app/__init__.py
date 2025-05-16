import os
from flask import Flask, render_template, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import timezone
from zoneinfo import ZoneInfo
from config import DeploymentConfig


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


AWST = ZoneInfo("Australia/Perth")

def to_awst(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(AWST)

def create_app(config_object=None):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(DeploymentConfig)

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    csrf.init_app(app)  # Enable CSRF protection


    # Register blueprints
    from app.blueprints import main
    app.register_blueprint(main)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', 
                             pending_requests_count=0,
                             accepted_requests_count=0,
                             unread_shared_data_count=0), 404

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

    # Add AWST template filter
    @app.template_filter('awst')
    def awst_filter(dt):
        return to_awst(dt)

    return app