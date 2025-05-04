from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

def init_routes(app):
    @app.route('/')
    def home():
        if 'username' in session:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['username'] = username
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials", 401
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    @app.route('/study_session')
    def study_session():
        return render_template('study_session.html')

    @app.route('/task_overview')
    def task_overview():
        return render_template('task_overview.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return "Username already exists", 400
            if User.query.filter_by(email=email).first():
                return "Email already registered", 400
            
            # Create new user
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email)
            
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for('login'))
        return render_template('signup.html')

    @app.route('/lecture_log')
    def lecture_log():
        return render_template('lecture_log.html')

    @app.route('/assessments')
    def assessments():
        return render_template('assessments.html')

    @app.route('/resources')
    def resources():
        return render_template('resources.html')

    @app.route('/health_carer')
    def health_carer():
        return render_template('health_carer.html')

    @app.route('/mental_health')
    def mental_health():
        return render_template('mental_health.html')

    @app.route('/wellness_check')
    def wellness_check():
        return render_template('wellness_check.html')

    @app.route('/study_break')
    def study_break():
        return render_template('study_break.html')

    @app.route('/study_tips')
    def study_tips():
        return render_template('study_tips.html')

    @app.route('/share_data')
    def share_data():
        return render_template('share_data.html')

    @app.route('/study_area')
    def study_area():
        return render_template('study_area.html')

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect(url_for('home')) 