from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User
import re

def validate_password_strength(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[
        DataRequired(),
        Length(min=3, max=120, message="Input must be between 3 and 120 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address"),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class StudySessionForm(FlaskForm):
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(max=100)
    ])
    start_time = DateTimeField('Start Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    end_time = DateTimeField('End Time', format='%Y-%m-%d %H:%M')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Session')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=100)
    ])
    description = TextAreaField('Description')
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M')
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    submit = SubmitField('Save Task')

class WellnessCheckForm(FlaskForm):
    mood_score = SelectField('Mood Score (1-10)', choices=[(str(i), str(i)) for i in range(1, 11)], validators=[DataRequired()])
    stress_level = SelectField('Stress Level (1-10)', choices=[(str(i), str(i)) for i in range(1, 11)], validators=[DataRequired()])
    sleep_hours = StringField('Hours of Sleep', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Wellness Check') 