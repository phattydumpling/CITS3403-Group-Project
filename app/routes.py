from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, StudySession, Task, WellnessCheck, MoodEntry, Friendship, FriendRequest, SharedData, Assessment
from app.forms import LoginForm, RegistrationForm, StudySessionForm, TaskForm, WellnessCheckForm
from datetime import datetime, timedelta, date
from flask_login import login_user, logout_user, login_required, current_user
from app import login_manager
import logging
from zoneinfo import ZoneInfo
from sqlalchemy import and_

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWST = ZoneInfo("Australia/Perth")

def hash_password(password):
    """Safely hash a password using scrypt."""
    try:
        return generate_password_hash(password, method='scrypt')
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def to_awst(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(AWST)

def init_routes(app):
    @app.template_filter('awst')
    def awst_filter(dt):
        return to_awst(dt)

    # Authentication Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = User.query.filter(
                    (User.username == form.username_or_email.data) |
                    (User.email == form.username_or_email.data)
                ).first()
                
                if user and check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                flash('Invalid username/email or password', 'error')
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                hashed_password = hash_password(form.password.data)
                new_user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'error')
        return render_template('signup.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()  # Clear all session data including flash messages
        response = redirect(url_for('index'))
        response.delete_cookie('remember_token')  # Clear the remember me cookie
        return response

    # Main Dashboard
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get the start of the current week (Sunday)
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
        start_of_week = datetime.combine(start_of_week, datetime.min.time())

        # Calculate study streak
        streak = 0
        current_date = today
        while True:
            # Check if there are any study sessions for the current date
            sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= datetime.combine(current_date, datetime.min.time()),
                StudySession.start_time < datetime.combine(current_date, datetime.max.time())
            ).first()
            
            if sessions:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        # Get all friends
        friends = current_user.friends

        # Calculate study hours for each friend
        friend_study_hours = []
        for friend in friends:
            # Get study sessions for this week
            sessions = StudySession.query.filter(
                StudySession.user_id == friend.id,
                StudySession.start_time >= start_of_week
            ).all()

            # Calculate total hours
            total_hours = sum(
                (session.end_time - session.start_time).total_seconds() / 3600 
                for session in sessions 
                if session.end_time
            )

            friend_study_hours.append({
                'friend': friend,
                'hours': round(total_hours, 1)
            })

        # Add current user's study hours
        user_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.start_time >= start_of_week
        ).all()
        user_hours = sum(
            (session.end_time - session.start_time).total_seconds() / 3600 
            for session in user_sessions 
            if session.end_time
        )
        friend_study_hours.append({
            'friend': current_user,
            'hours': round(user_hours, 1)
        })

        # Sort by hours in descending order
        friend_study_hours.sort(key=lambda x: x['hours'], reverse=True)

        # Get completed tasks count
        completed_tasks = Task.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).count()

        # Get weekly mood average
        week_ago = datetime.utcnow() - timedelta(days=7)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= week_ago
        ).all()
        
        weekly_mood = 0
        if mood_entries:
            weekly_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)

        # Get unique subjects studied (non-empty, non-null)
        unique_subjects = db.session.query(StudySession.subject).filter(
            StudySession.user_id == current_user.id,
            StudySession.subject.isnot(None),
            StudySession.subject != ''
        ).distinct().count()

        # Get all upcoming assessments (not done)
        upcoming_assessments = Assessment.query.filter_by(user_id=current_user.id, done=False).order_by(Assessment.due_date).all()

        # Calculate assessment completion rate
        total_assessments = Assessment.query.filter_by(user_id=current_user.id).count()
        completed_assessments = Assessment.query.filter_by(user_id=current_user.id, done=True).count()
        assessment_completion_rate = 0
        if total_assessments > 0:
            assessment_completion_rate = int(round((completed_assessments / total_assessments) * 100))

        return render_template('dashboard.html',
            friend_study_hours=friend_study_hours[:3],  # Only pass top 3 for the podium
            completed_tasks=completed_tasks,
            weekly_mood=round(weekly_mood, 1),
            unique_subjects=unique_subjects,
            upcoming_assessments=upcoming_assessments,
            now=date.today(),
            assessment_completion_rate=assessment_completion_rate,
            study_streak=streak,
            timedelta=timedelta  # Add timedelta to template context
        )

    # Study Area Route
    @app.route('/study_area')
    @login_required
    def study_area():
        today = datetime.today().date()
        user_id = current_user.id

        # Query today's sessions
        sessions_today = StudySession.query.filter_by(user_id=user_id).filter(StudySession.start_time >= today).all()

        # Total time in seconds
        total_time_seconds = sum(
            (session.end_time - session.start_time).total_seconds() for session in sessions_today if session.end_time
        )
        
        # Format time as HH:MM:SS string
        total_time_formatted = str(timedelta(seconds=total_time_seconds))

        # Convert time to minutes for the frontend
        total_time_minutes = round(total_time_seconds / 60)

        completed_sessions = len(sessions_today)

        # Get recent sessions (last 5)
        recent_sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.start_time.desc()).limit(5).all()

        # Convert times to AWST for template
        for session in recent_sessions:
            session.start_time_awst = to_awst(session.start_time)
            session.end_time_awst = to_awst(session.end_time)

        return render_template(
            'study_area.html',
            total_time=total_time_formatted,
            total_time_minutes=total_time_minutes,
            completed_sessions=completed_sessions,
            sessions=recent_sessions
        )

    @app.route('/study_session', methods=['GET', 'POST'])
    @login_required
    def study_session():
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                session_date = datetime.fromisoformat(data['start_time']).date()
                start_dt = datetime.fromisoformat(data['start_time'])
                end_dt = None  # Will be updated when session ends

                study_session = StudySession(
                    user_id=current_user.id,
                    subject=data['subject'],
                    start_time=start_dt,
                    end_time=end_dt,
                    notes=data.get('notes')
                )
                db.session.add(study_session)
                db.session.commit()
                return jsonify({'success': True, 'session_id': study_session.id})
            else:
                form = StudySessionForm()
                if form.validate_on_submit():
                    session_date = form.date.data
                    start_dt = datetime.combine(session_date, form.start_time.data)
                    end_dt = datetime.combine(session_date, form.end_time.data) if form.end_time.data else None

                    study_session = StudySession(
                        user_id=current_user.id,
                        subject=form.subject.data,
                        start_time=start_dt,
                        end_time=end_dt,
                        notes=form.notes.data
                    )
                    db.session.add(study_session)
                    db.session.commit()
                    flash('Study session recorded successfully!', 'success')
                    return redirect(url_for('dashboard'))
        return render_template('study_session.html', form=form)

    @app.route('/study_session/<int:session_id>', methods=['DELETE'])
    @login_required
    def delete_study_session(session_id):
        session = StudySession.query.get_or_404(session_id)
        if session.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        db.session.delete(session)
        db.session.commit()
        return '', 204

    @app.route('/study_session/<int:session_id>', methods=['PUT'])
    @login_required
    def update_study_session(session_id):
        session = StudySession.query.get_or_404(session_id)
        if session.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if 'end_time' in data:
            session.end_time = datetime.fromisoformat(data['end_time'])
        
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/active_session')
    @login_required
    def get_active_session():
        # Find the most recent session without an end time
        active_session = StudySession.query.filter_by(
            user_id=current_user.id,
            end_time=None
        ).order_by(StudySession.start_time.desc()).first()
        
        return jsonify({
            'active_session': active_session is not None,
            'session_id': active_session.id if active_session else None
        })

    @app.route('/study_history')
    @login_required
    def study_history():
        sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).all()
        # Convert times to AWST for template
        for session in sessions:
            session.start_time_awst = to_awst(session.start_time)
            session.end_time_awst = to_awst(session.end_time)
        return render_template('study_history.html', sessions=sessions)


    @app.route('/task_overview', methods=['GET', 'POST'])
    @login_required
    def task_overview():
        form = TaskForm()
        if form.validate_on_submit():
            task = Task(
                user_id=current_user.id,
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
        
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template('task_overview.html', form=form, tasks=tasks)

    @app.route('/lecture_log')
    @login_required
    def lecture_log():
        return render_template('lecture_log.html')

    @app.route('/assessments')
    @login_required
    def assessments():
        return render_template('assessments.html')

    @app.route('/resources')
    @login_required
    def resources():
        return render_template('resources.html')

    # Care Page Routes
    @app.route('/health_carer', methods=['GET', 'POST'])
    @login_required
    def health_carer():
        # Handle main goals form submission
        if request.method == 'POST':
            emotional_goal = request.form.get('emotional-goal')
            physical_goal = request.form.get('physical-goal')
            study_goal = request.form.get('study-goal')
            emotional_custom = request.form.get('emotional-custom')
            physical_custom = request.form.get('physical-custom')
            study_custom = request.form.get('study-custom')

            # Prefer custom input if provided, else use selected radio
            selected_goals = {
                'emotional': emotional_custom if emotional_custom else emotional_goal,
                'physical': physical_custom if physical_custom else physical_goal,
                'study': study_custom if study_custom else study_goal
            }
            flash(f"Goals submitted: Emotional - {selected_goals['emotional']}, Physical - {selected_goals['physical']}, Study - {selected_goals['study']}", "success")

        # Get user's mood entries for the past week
        week_ago = datetime.utcnow() - timedelta(days=7)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= week_ago
        ).order_by(MoodEntry.created_at.desc()).all()
        # Convert times to AWST for template
        for entry in mood_entries:
            entry.created_at_awst = to_awst(entry.created_at)
        return render_template('health_carer.html', mood_entries=mood_entries)

    @app.route('/wellness_check', methods=['GET', 'POST'])
    @login_required
    def wellness_check():
        form = WellnessCheckForm()
        if form.validate_on_submit():
            check = WellnessCheck(
                user_id=current_user.id,
                mood_score=int(form.mood_score.data),
                stress_level=int(form.stress_level.data),
                notes=form.notes.data
            )
            db.session.add(check)
            db.session.commit()
            flash('Wellness check recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('wellness_check.html', form=form)

    # Data Sharing Route
    @app.route('/share_data')
    @login_required
    def share_data():
        # Get friends list with user objects
        friendships = Friendship.query.filter(
            (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
        ).all()
        
        # Get the actual friend user objects
        friends = []
        for friendship in friendships:
            if friendship.user_id == current_user.id:
                friend = User.query.get(friendship.friend_id)
            else:
                friend = User.query.get(friendship.user_id)
            if friend:
                friends.append(friend)
        
        return render_template('share_data.html', friends=friends)

    @app.route('/shared_data_history')
    @login_required
    def shared_data_history():
        # Get shared data history (data you've shared)
        shared_data = SharedData.query.filter_by(from_user_id=current_user.id).order_by(SharedData.created_at.desc()).all()
        # Convert times to AWST for template
        for data in shared_data:
            data.created_at_awst = to_awst(data.created_at)
        return render_template('shared_data_history.html', shared_data=shared_data)

    @app.route('/data_shared_with_you')
    @login_required
    def data_shared_with_you():
        # Get data shared with you
        data_shared_with_you = SharedData.query.filter_by(to_user_id=current_user.id).order_by(SharedData.created_at.desc()).all()
        # Convert times to AWST for template
        for data in data_shared_with_you:
            data.created_at_awst = to_awst(data.created_at)
        return render_template('data_shared_with_you.html', data_shared_with_you=data_shared_with_you)

    @app.route('/api/share_data', methods=['POST'])
    @login_required
    def share_data_api():
        data = request.get_json()
        if not data or 'friend_id' not in data or 'data' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        friend = User.query.get(data['friend_id'])
        if not friend or friend not in current_user.friends:
            return jsonify({'success': False, 'error': 'Invalid friend'}), 400

        # Prepare data to share based on selected options
        shared_data = {}
        if data['data'].get('study_progress'):
            # Get study sessions from the last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            study_sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.created_at >= week_ago
            ).all()
            shared_data['study_progress'] = [{
                'subject': session.subject,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'notes': session.notes
            } for session in study_sessions]

        if data['data'].get('mood'):
            # Get mood entries from the last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            mood_entries = MoodEntry.query.filter(
                MoodEntry.user_id == current_user.id,
                MoodEntry.created_at >= week_ago
            ).all()
            shared_data['mood'] = [{
                'mood_score': entry.mood_score,
                'reflection': entry.reflection,
                'created_at': entry.created_at.isoformat()
            } for entry in mood_entries]

        if data['data'].get('tasks'):
            # Get completed tasks from the last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            tasks = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'completed',
                Task.created_at >= week_ago
            ).all()
            shared_data['tasks'] = [{
                'title': task.title,
                'description': task.description,
                'completed_at': task.created_at.isoformat()
            } for task in tasks]

        # Create shared data entry
        shared_data_entry = SharedData(
            from_user_id=current_user.id,
            to_user_id=friend.id,
            data_type='combined',
            data_content=shared_data
        )
        db.session.add(shared_data_entry)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/notifications')
    @login_required
    def notifications():
        pending_requests = FriendRequest.query.filter_by(to_user_id=current_user.id, status='pending').all()
        accepted_requests = FriendRequest.query.filter_by(from_user_id=current_user.id, status='accepted', is_read=False).all()
        shared_data = SharedData.query.filter_by(to_user_id=current_user.id, is_read=False).all()

        # Mark shared data and accepted requests as read
        for data in shared_data:
            data.is_read = True
        for request in accepted_requests:
            request.is_read = True
        db.session.commit()

        # Convert times to AWST for template
        for req in pending_requests:
            req.created_at_awst = to_awst(req.created_at)
        for req in accepted_requests:
            req.created_at_awst = to_awst(req.created_at)
            req.updated_at_awst = to_awst(req.updated_at) if req.updated_at else None
        for data in shared_data:
            data.created_at_awst = to_awst(data.created_at)

        # Combine friend requests and accepted requests into one list
        friend_notifications = []
        for req in pending_requests:
            friend_notifications.append({
                'type': 'pending',
                'request': req,
                'timestamp': req.created_at_awst
            })
        for req in accepted_requests:
            friend_notifications.append({
                'type': 'accepted',
                'request': req,
                'timestamp': req.updated_at_awst or req.created_at_awst
            })
        # Sort by timestamp, newest first
        friend_notifications.sort(key=lambda x: x['timestamp'], reverse=True)

        return render_template('notifications.html', 
                             friend_notifications=friend_notifications,
                             shared_data=shared_data)

    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            pending_count = FriendRequest.query.filter_by(to_user_id=current_user.id, status='pending').count()
            accepted_count = FriendRequest.query.filter_by(from_user_id=current_user.id, status='accepted', is_read=False).count()
            unread_shared_data = SharedData.query.filter_by(to_user_id=current_user.id, is_read=False).count()
            return dict(
                pending_requests_count=pending_count,
                accepted_requests_count=accepted_count,
                unread_shared_data_count=unread_shared_data
            )
        return dict(pending_requests_count=0, accepted_requests_count=0, unread_shared_data_count=0)

    # API Routes for Tasks
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        } for task in tasks])

    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        task = Task(
            user_id=current_user.id,
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
    @login_required
    def delete_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        return '', 204

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @login_required
    def update_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
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
    @login_required
    def profile():
        # Show pending friend requests
        pending_requests = FriendRequest.query.filter_by(to_user_id=current_user.id, status='pending').all()
        
        if request.method == 'POST':
            try:
                # Handle profile updates
                email = request.form.get('email')
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                university = request.form.get('university')
                profile_picture = request.form.get('profile_picture')
                username = request.form.get('username')
                
                # Update username if provided
                if username and username != current_user.username:
                    # Validate username length
                    if len(username) < 3 or len(username) > 80:
                        flash('Username must be between 3 and 80 characters', 'error')
                    else:
                        # Check if username is already taken
                        existing_user = User.query.filter_by(username=username).first()
                        if existing_user and existing_user.id != current_user.id:
                            flash('Username already taken', 'error')
                        else:
                            current_user.username = username
                            flash('Username updated successfully', 'success')
                
                # Update profile picture if provided
                if profile_picture is not None:
                    current_user.profile_picture = profile_picture if profile_picture else None
                    flash('Profile picture updated successfully', 'success')
                
                # Update email if provided
                if email and email != current_user.email:
                    # Check if email is already taken
                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user and existing_user.id != current_user.id:
                        flash('Email already in use', 'error')
                    else:
                        current_user.email = email
                        flash('Email updated successfully', 'success')
                
                # Update university if provided
                if university is not None and university != current_user.university:
                    current_user.university = university
                    flash('University updated successfully', 'success')
                
                # Update password if provided
                if current_password and new_password:
                    if check_password_hash(current_user.password, current_password):
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
                            try:
                                current_user.password = hash_password(new_password)
                                flash('Password updated successfully', 'success')
                            except Exception as e:
                                logger.error(f"Password update error: {str(e)}")
                                flash('An error occurred while updating your password. Please try again.', 'error')
                    else:
                        flash('Current password is incorrect', 'error')
                
                db.session.commit()
                return redirect(url_for('profile'))
            except Exception as e:
                logger.error(f"Profile update error: {str(e)}")
                db.session.rollback()
                flash('An error occurred while updating your profile. Please try again.', 'error')
        
        return render_template('profile.html', current_user=current_user, pending_requests=pending_requests)

    @app.route('/delete_account', methods=['POST'])
    @login_required
    def delete_account():
        try:
            # Delete all user's data
            # Delete study sessions
            StudySession.query.filter_by(user_id=current_user.id).delete()
            
            # Delete tasks
            Task.query.filter_by(user_id=current_user.id).delete()
            
            # Delete wellness checks
            WellnessCheck.query.filter_by(user_id=current_user.id).delete()
            
            # Delete mood entries
            MoodEntry.query.filter_by(user_id=current_user.id).delete()
            
            # Delete friendships
            Friendship.query.filter(
                (Friendship.user_id == current_user.id) | 
                (Friendship.friend_id == current_user.id)
            ).delete()
            
            # Delete friend requests
            FriendRequest.query.filter(
                (FriendRequest.from_user_id == current_user.id) | 
                (FriendRequest.to_user_id == current_user.id)
            ).delete()
            
            # Delete shared data
            SharedData.query.filter(
                (SharedData.from_user_id == current_user.id) | 
                (SharedData.to_user_id == current_user.id)
            ).delete()
            
            # Delete assessments
            Assessment.query.filter_by(user_id=current_user.id).delete()
            
            # Finally, delete the user
            db.session.delete(current_user)
            db.session.commit()
            
            # Logout the user
            logout_user()
            flash('Your account has been successfully deleted.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Account deletion error: {str(e)}")
            db.session.rollback()
            flash('An error occurred while deleting your account. Please try again.', 'error')
            return redirect(url_for('profile'))

    @app.route('/api/mood_entries', methods=['POST'])
    @login_required
    def create_mood_entry():
        data = request.get_json()
        if not data or 'mood_score' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        entry = MoodEntry(
            user_id=current_user.id,
            mood_score=int(data['mood_score']),
            reflection=data.get('reflection', '')
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({
            'id': entry.id,
            'mood_score': entry.mood_score,
            'reflection': entry.reflection,
            'created_at': entry.created_at.isoformat()
        }), 201

    @app.route('/api/mood_entries', methods=['GET'])
    @login_required
    def get_mood_entries():
        week_ago = datetime.utcnow() - timedelta(days=7)
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= week_ago
        ).order_by(MoodEntry.created_at.desc()).all()
        return jsonify([{
            'id': entry.id,
            'mood_score': entry.mood_score,
            'reflection': entry.reflection,
            'created_at': entry.created_at.isoformat()
        } for entry in entries])

    @app.route('/api/mood_entries/<int:entry_id>', methods=['DELETE'])
    @login_required
    def delete_mood_entry(entry_id):
        try:
            entry = MoodEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
            if not entry:
                return jsonify({'error': 'Entry not found'}), 404
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'message': 'Entry deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/friends', methods=['GET', 'POST'])
    @login_required
    def friends():
        friends = current_user.friends
        pending_requests = FriendRequest.query.filter_by(to_user_id=current_user.id, status='pending').all()

        if request.method == 'POST':
            friend_username = request.form.get('friend_username')
            friend = User.query.filter_by(username=friend_username).first()
            if not friend:
                flash('User not found.', 'error')
            elif friend == current_user:
                flash('You cannot add yourself as a friend.', 'error')
            elif friend in friends:
                flash('Already friends.', 'info')
            elif FriendRequest.query.filter_by(from_user_id=current_user.id, to_user_id=friend.id, status='pending').first():
                flash('Friend request already sent.', 'info')
            else:
                new_request = FriendRequest(from_user_id=current_user.id, to_user_id=friend.id)
                db.session.add(new_request)
                db.session.commit()
                flash(f'Friend request sent to {friend.username}!', 'success')
            return redirect(url_for('friends'))

        return render_template('friends.html', friends=friends, pending_requests=pending_requests)

    @app.route('/remove_friend/<int:friend_id>', methods=['POST'])
    @login_required
    def remove_friend(friend_id):
        # Remove both friendship records
        friendship1 = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend_id).first()
        friendship2 = Friendship.query.filter_by(user_id=friend_id, friend_id=current_user.id).first()
        
        if friendship1:
            db.session.delete(friendship1)
        if friendship2:
            db.session.delete(friendship2)
            
        if friendship1 or friendship2:
            db.session.commit()
            flash('Friend removed.', 'success')
        else:
            flash('Friendship not found.', 'error')
        return redirect(url_for('friends'))

    @app.route('/accept_friend/<int:request_id>', methods=['POST'])
    @login_required
    def accept_friend(request_id):
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.to_user_id == current_user.id and friend_request.status == 'pending':
            # Accept the request
            friend_request.status = 'accepted'
            
            # Create friendship records for both users
            friendship1 = Friendship(user_id=friend_request.to_user_id, friend_id=friend_request.from_user_id)
            friendship2 = Friendship(user_id=friend_request.from_user_id, friend_id=friend_request.to_user_id)
            
            db.session.add(friendship1)
            db.session.add(friendship2)
            db.session.commit()
            flash(f'You are now friends with {friend_request.from_user.username}!', 'success')
        else:
            flash('Invalid friend request.', 'error')
        return redirect(url_for('friends'))

    @app.route('/reject_friend/<int:request_id>', methods=['POST'])
    @login_required
    def reject_friend(request_id):
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.to_user_id == current_user.id and friend_request.status == 'pending':
            friend_request.status = 'rejected'
            db.session.commit()
            flash('Friend request rejected.', 'info')
        else:
            flash('Invalid friend request.', 'error')
        return redirect(url_for('friends'))

    @app.route('/api/study_sessions', methods=['GET'])
    @login_required
    def get_study_sessions():
        view = request.args.get('view', 'week')  # Default to weekly view
        now = datetime.now(AWST)  # Use AWST timezone
        
        if view == 'day':
            # Get data for the current day in AWST
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= start_time
            ).all()
            
            # Group by hour
            hours = [0] * 24
            for session in sessions:
                if session.end_time:
                    # Convert session time to AWST
                    session_start = to_awst(session.start_time)
                    hour = session_start.hour
                    duration = (session.end_time - session.start_time).total_seconds() / 60  # Convert to minutes
                    hours[hour] += duration
            
            return jsonify({
                'labels': [f"{i:02d}:00" for i in range(24)],
                'data': hours
            })
            
        elif view == 'week':
            # Get data for the current week (Sunday to Saturday) in AWST
            today = now.date()
            # Find the most recent Sunday
            start_of_week = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
            sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= datetime.combine(start_of_week, datetime.min.time())
            ).all()

            # Group by weekday (0=Sunday, 6=Saturday)
            days = [0] * 7
            for session in sessions:
                if session.end_time:
                    # Convert session time to AWST
                    session_start = to_awst(session.start_time)
                    weekday = session_start.weekday()  # 0=Monday, 6=Sunday
                    weekday = (weekday + 1) % 7      # Convert to 0=Sunday, 6=Saturday
                    duration = (session.end_time - session.start_time).total_seconds() / 3600
                    days[weekday] += duration

            return jsonify({
                'labels': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                'data': days
            })
            
        else:  # month view
            # Get data for the current month in AWST
            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= first_day
            ).all()

            # Group by week of the month (1-4)
            weeks = [0] * 4
            for session in sessions:
                if session.end_time:
                    # Convert session time to AWST
                    session_start = to_awst(session.start_time)
                    session_date = session_start.date()
                    # Calculate week index: 0 for days 1-7, 1 for 8-14, 2 for 15-21, 3 for 22-end
                    week_index = (session_date.day - 1) // 7
                    if 0 <= week_index < 4:
                        duration = (session.end_time - session.start_time).total_seconds() / 3600
                        weeks[week_index] += duration

            return jsonify({
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'data': weeks
            })

    @app.route('/api/unit_distribution')
    @login_required
    def unit_distribution():
        # Get all study sessions for the user with a non-empty subject
        sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        subject_times = {}
        for session in sessions:
            if session.end_time and session.subject and session.subject.strip():
                duration = (session.end_time - session.start_time).total_seconds() / 60  # minutes
                subject_times[session.subject] = subject_times.get(session.subject, 0) + duration
        labels = list(subject_times.keys())
        data = [round(subject_times[subj], 2) for subj in labels]
        return jsonify({'labels': labels, 'data': data})

    # API Endpoints for Assessments
    @app.route('/api/assessments', methods=['GET'])
    @login_required
    def get_assessments():
        assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.due_date).all()
        return jsonify([
            {
                'id': a.id,
                'subject': a.subject,
                'title': a.title,
                'due_date': a.due_date.isoformat(),
                'done': a.done,
                'grade': a.grade,
                'weight': a.weight
            } for a in assessments
        ])

    @app.route('/api/assessments', methods=['POST'])
    @login_required
    def create_assessment():
        data = request.get_json()
        if not data or not all(k in data for k in ('subject', 'title', 'due_date')):
            return jsonify({'error': 'Missing required fields'}), 400
        assessment = Assessment(
            user_id=current_user.id,
            subject=data['subject'],
            title=data['title'],
            due_date=datetime.fromisoformat(data['due_date']).date(),
            done=data.get('done', False),
            grade=data.get('grade'),
            weight=data.get('weight')
        )
        db.session.add(assessment)
        db.session.commit()
        return jsonify({'id': assessment.id}), 201

    @app.route('/api/assessments/<int:assessment_id>', methods=['PUT'])
    @login_required
    def update_assessment(assessment_id):
        assessment = Assessment.query.filter_by(id=assessment_id, user_id=current_user.id).first()
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        data = request.get_json()
        if 'subject' in data:
            assessment.subject = data['subject']
        if 'title' in data:
            assessment.title = data['title']
        if 'due_date' in data:
            assessment.due_date = datetime.fromisoformat(data['due_date']).date()
        if 'done' in data:
            assessment.done = data['done']
        if 'grade' in data:
            assessment.grade = data['grade']
        if 'weight' in data:
            assessment.weight = data['weight']
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/assessments/<int:assessment_id>', methods=['DELETE'])
    @login_required
    def delete_assessment(assessment_id):
        assessment = Assessment.query.filter_by(id=assessment_id, user_id=current_user.id).first()
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        db.session.delete(assessment)
        db.session.commit()
        return '', 204

    @app.route('/friend_leaderboard')
    @login_required
    def friend_leaderboard():
        # Get the start of the current week (Sunday)
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
        start_of_week = datetime.combine(start_of_week, datetime.min.time())

        # Get all friends
        friends = current_user.friends

        # Calculate study hours for each friend
        friend_study_hours = []
        for friend in friends:
            # Get study sessions for this week
            sessions = StudySession.query.filter(
                StudySession.user_id == friend.id,
                StudySession.start_time >= start_of_week
            ).all()

            # Calculate total hours
            total_hours = sum(
                (session.end_time - session.start_time).total_seconds() / 3600 
                for session in sessions 
                if session.end_time
            )

            friend_study_hours.append({
                'friend': friend,
                'hours': round(total_hours, 1)
            })

        # Sort by hours in descending order
        friend_study_hours.sort(key=lambda x: x['hours'], reverse=True)

        return render_template('friend_leaderboard.html', 
                             friend_study_hours=friend_study_hours,
                             start_of_week=start_of_week) 