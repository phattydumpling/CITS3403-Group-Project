from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, SelectField
from wtforms import StringField, DateField, TimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[
        DataRequired(),
        Length(min=3, max=120, message="Input must be between 3 and 120 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
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
        Length(min=6, message="Password must be at least 6 characters long")
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
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', format='%H:%M')
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