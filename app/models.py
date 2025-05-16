from datetime import datetime, UTC, timedelta
from app import db
from flask_login import UserMixin

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Define relationships with back_populates
    from_user = db.relationship('User', foreign_keys=[from_user_id], back_populates='sent_friend_requests')
    to_user = db.relationship('User', foreign_keys=[to_user_id], back_populates='received_friend_requests')

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='_user_friend_uc'),)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    university = db.Column(db.String(120))
    profile_picture = db.Column(db.String(120), default=None)  # Store the filename of the profile picture
    
    # Relationships
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    wellness_checks = db.relationship('WellnessCheck', backref='user', lazy=True)
    study_goals = db.relationship('StudyGoal', backref='user', lazy=True)
    friends = db.relationship(
        'User',
        secondary='friendship',
        primaryjoin=(Friendship.user_id == id),
        secondaryjoin=(Friendship.friend_id == id),
        backref='friend_of'
    )
    # Update relationship names to avoid conflicts
    sent_friend_requests = db.relationship('FriendRequest', 
                                         foreign_keys='FriendRequest.from_user_id',
                                         back_populates='from_user',
                                         lazy=True)
    received_friend_requests = db.relationship('FriendRequest',
                                            foreign_keys='FriendRequest.to_user_id',
                                            back_populates='to_user',
                                            lazy=True)

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    subject = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class WellnessCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer)  # 1-10 scale
    stress_level = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)
    reflection = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    user = db.relationship('User', backref=db.backref('mood_entries', lazy=True))

class SharedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # study_progress, mood, etc.
    data_content = db.Column(db.JSON, nullable=False)  # Store the actual shared data
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='shared_data_sent')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='shared_data_received')

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    done = db.Column(db.Boolean, default=False)
    grade = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)

class StudyGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    target_hours = db.Column(db.Float, nullable=False)  # Target study hours per week
    current_hours = db.Column(db.Float, default=0)  # Current study hours this week
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<StudyGoal {self.subject} - {self.target_hours} hours>' 