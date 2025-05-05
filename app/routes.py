from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, StudySession, Task, WellnessCheck
from app.forms import LoginForm, RegistrationForm, StudySessionForm, TaskForm, WellnessCheckForm
from datetime import datetime

def init_routes(app):
    # Authentication Routes
    @app.route('/')
    def home():
        if 'username' in session:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
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

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        session.pop('user_id', None)
        session.pop('_flashes', None)
        return redirect(url_for('home'))

    # Main Dashboard
    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    # Study Area Routes
    @app.route('/study_area')
    def study_area():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('study_area.html')

    @app.route('/study_session', methods=['GET', 'POST'])
    def study_session():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        form = StudySessionForm()
        if form.validate_on_submit():
            study_session = StudySession(
                user_id=session['user_id'],
                subject=form.subject.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                notes=form.notes.data
            )
            db.session.add(study_session)
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

    @app.route('/lecture_log')
    def lecture_log():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('lecture_log.html')

    @app.route('/assessments')
    def assessments():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('assessments.html')

    @app.route('/resources')
    def resources():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('resources.html')

    # Care Page Routes
    @app.route('/health_carer')
    def health_carer():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('health_carer.html')

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

    # Data Sharing Route
    @app.route('/share_data')
    def share_data():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('share_data.html')

    # API Routes for Tasks
    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.created_at.desc()).all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        } for task in tasks])

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        task = Task(
            user_id=session['user_id'],
            title=data['title'],
            status='pending',
            priority='medium'
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        }), 201

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        return '', 204

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        if 'title' in data:
            task.title = data['title']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        
        db.session.commit()
        return jsonify({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        }) 