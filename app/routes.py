from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, StudySession, Task, WellnessCheck, MoodEntry, Friendship, FriendRequest, SharedData
from app.forms import LoginForm, RegistrationForm, StudySessionForm, TaskForm, WellnessCheckForm
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, login_required, current_user
from app import login_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password):
    """Safely hash a password using pbkdf2:sha256 with a salt."""
    try:
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_routes(app):
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
        return render_template('dashboard.html')

    # Study Area Routes
    @app.route('/study_area')
    @login_required
    def study_area():
        return render_template('study_area.html')

    @app.route('/study_session', methods=['GET', 'POST'])
    @login_required
    def study_session():
        form = StudySessionForm()
        if form.validate_on_submit():
            study_session = StudySession(
                user_id=current_user.id,
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
    @app.route('/health_carer')
    @login_required
    def health_carer():
        # Get user's mood entries for the past week
        week_ago = datetime.utcnow() - timedelta(days=7)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= week_ago
        ).order_by(MoodEntry.created_at.desc()).all()
        
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
        return render_template('shared_data_history.html', shared_data=shared_data)

    @app.route('/data_shared_with_you')
    @login_required
    def data_shared_with_you():
        # Get data shared with you
        data_shared_with_you = SharedData.query.filter_by(to_user_id=current_user.id).order_by(SharedData.created_at.desc()).all()
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

        # Combine friend requests and accepted requests into one list
        friend_notifications = []
        for req in pending_requests:
            friend_notifications.append({
                'type': 'pending',
                'request': req,
                'timestamp': req.created_at
            })
        for req in accepted_requests:
            friend_notifications.append({
                'type': 'accepted',
                'request': req,
                'timestamp': req.updated_at or req.created_at
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