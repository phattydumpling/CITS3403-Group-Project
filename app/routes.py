from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, StudySession, Task, WellnessCheck
from app.forms import LoginForm, RegistrationForm, StudySessionForm, TaskForm, WellnessCheckForm
from datetime import datetime

def init_routes(app):
    @app.route('/')
    def home():
        if 'username' in session:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # Try to find user by username or email
            user = User.query.filter(
                (User.username == form.username_or_email.data) |
                (User.email == form.username_or_email.data)
            ).first()
            
            if user and check_password_hash(user.password, form.password.data):
                session['username'] = user.username
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid username/email or password', 'error')
        return render_template('login.html', form=form)

    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    @app.route('/study_session', methods=['GET', 'POST'])
    def study_session():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        form = StudySessionForm()
        if form.validate_on_submit():
            session = StudySession(
                user_id=session['user_id'],
                subject=form.subject.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                notes=form.notes.data
            )
            db.session.add(session)
            db.session.commit()
            flash('Study session recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('study_session.html', form=form)

    @app.route('/task_overview', methods=['GET', 'POST'])
    def task_overview():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        form = TaskForm()
        if form.validate_on_submit():
            task = Task(
                user_id=session['user_id'],
                title=form.title.data,
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status=form.status.data
            )
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('task_overview'))
        
        tasks = Task.query.filter_by(user_id=session['user_id']).all()
        return render_template('task_overview.html', form=form, tasks=tasks)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html', form=form)

    @app.route('/wellness_check', methods=['GET', 'POST'])
    def wellness_check():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        form = WellnessCheckForm()
        if form.validate_on_submit():
            check = WellnessCheck(
                user_id=session['user_id'],
                mood_score=int(form.mood_score.data),
                stress_level=int(form.stress_level.data),
                sleep_hours=float(form.sleep_hours.data),
                notes=form.notes.data
            )
            db.session.add(check)
            db.session.commit()
            flash('Wellness check recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('wellness_check.html', form=form)

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
        # Clear all flash messages
        session.pop('_flashes', None)
        return redirect(url_for('home')) 