from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, StudySession, Task, WellnessCheck, MoodEntry
from app.forms import LoginForm, RegistrationForm, StudySessionForm, TaskForm, WellnessCheckForm
from datetime import datetime, timedelta

def init_routes(app):
    # Authentication Routes
    @app.route('/')
    def home():
        if 'username' not in session:
            return redirect(url_for('login'))
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
        
        # Get user's mood entries for the past week
        user = User.query.get(session['user_id'])
        week_ago = datetime.utcnow() - timedelta(days=7)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == session['user_id'],
            MoodEntry.created_at >= week_ago
        ).order_by(MoodEntry.created_at.desc()).all()
        
        return render_template('health_carer.html', mood_entries=mood_entries)

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

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Handle profile updates
            email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            # Update email if provided
            if email and email != user.email:
                # Check if email is already taken
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user.id:
                    flash('Email already in use', 'error')
                else:
                    user.email = email
                    flash('Email updated successfully', 'success')
            
            # Update password if provided
            if current_password and new_password:
                if check_password_hash(user.password, current_password):
                    # Validate new password requirements
                    if len(new_password) < 8:
                        flash('Password must be at least 8 characters long', 'error')
                    elif not any(c.isupper() for c in new_password):
                        flash('Password must contain at least one uppercase letter', 'error')
                    elif not any(c.islower() for c in new_password):
                        flash('Password must contain at least one lowercase letter', 'error')
                    elif not any(c.isdigit() for c in new_password):
                        flash('Password must contain at least one number', 'error')
                    elif not any(c in '!@#$%^&*(),.?":{}|<>' for c in new_password):
                        flash('Password must contain at least one special character', 'error')
                    else:
                        user.password = generate_password_hash(new_password)
                        flash('Password updated successfully', 'success')
                else:
                    flash('Current password is incorrect', 'error')
            
            db.session.commit()
            return redirect(url_for('profile'))
        
        return render_template('profile.html', user=user)

    @app.route('/api/mood_entries', methods=['POST'])
    def create_mood_entry():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        data = request.get_json()
        if not data or 'mood_score' not in data or 'sleep_quality' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        entry = MoodEntry(
            user_id=session['user_id'],
            mood_score=int(data['mood_score']),
            sleep_quality=int(data['sleep_quality']),
            reflection=data.get('reflection', '')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'id': entry.id,
            'mood_score': entry.mood_score,
            'sleep_quality': entry.sleep_quality,
            'reflection': entry.reflection,
            'created_at': entry.created_at.isoformat()
        }), 201

    @app.route('/api/mood_entries', methods=['GET'])
    def get_mood_entries():
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == session['user_id'],
            MoodEntry.created_at >= week_ago
        ).order_by(MoodEntry.created_at.desc()).all()
        
        return jsonify([{
            'id': entry.id,
            'mood_score': entry.mood_score,
            'sleep_quality': entry.sleep_quality,
            'reflection': entry.reflection,
            'created_at': entry.created_at.isoformat()
        } for entry in entries])

    @app.route('/api/mood_entries/<int:entry_id>', methods=['DELETE'])
    def delete_mood_entry(entry_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        try:
            entry = MoodEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first()
            if not entry:
                return jsonify({'error': 'Entry not found'}), 404
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'message': 'Entry deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500 