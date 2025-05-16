import unittest
from datetime import datetime, UTC, timedelta
from app import create_app, db
from app.models import User, FriendRequest, StudySession, Task, WellnessCheck, Assessment
from config import TestConfig
from werkzeug.security import generate_password_hash

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_database(self):
        """Test basic database functionality"""
        test_user = User(
            username='testuser2',
            email='test2@example.com',
            password=generate_password_hash('testpass123')
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        # Verify we can query the user
        user = User.query.filter_by(username='testuser2').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')

    def test_user_creation(self):
        """Test user creation and validation"""
        user = User(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            university='Test University'
        )
        db.session.add(user)
        db.session.commit()

        # Test user was created
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.university, 'Test University')

    def test_friend_request(self):
        """Test friend request functionality"""
        # Create two users
        user1 = User(username='user1', email='user1@example.com', password='User1Pass123!')
        user2 = User(username='user2', email='user2@example.com', password='User2Pass123!')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create friend request
        friend_request = FriendRequest(from_user_id=user1.id, to_user_id=user2.id)
        db.session.add(friend_request)
        db.session.commit()

        # Test friend request was created
        self.assertIsNotNone(friend_request.id)
        self.assertEqual(friend_request.status, 'pending')
        self.assertFalse(friend_request.is_read)

        # Test relationships
        self.assertEqual(len(user1.sent_friend_requests), 1)
        self.assertEqual(len(user2.received_friend_requests), 1)

    def test_study_session(self):
        """Test study session creation and validation"""
        user = User(username='student', email='student@example.com', password='StudentPass123!')
        db.session.add(user)
        db.session.commit()

        start_time = datetime.now(UTC)
        end_time = start_time + timedelta(hours=2)
        
        session = StudySession(
            user_id=user.id,
            start_time=start_time,
            end_time=end_time,
            subject='Mathematics',
            notes='Studied calculus'
        )
        db.session.add(session)
        db.session.commit()

        # Test study session was created
        self.assertIsNotNone(session.id)
        self.assertEqual(session.subject, 'Mathematics')
        self.assertEqual(session.notes, 'Studied calculus')
        self.assertEqual(session.user_id, user.id)

    def test_task_management(self):
        """Test task creation and status updates"""
        user = User(username='taskuser', email='task@example.com', password='TaskUserPass123!')
        db.session.add(user)
        db.session.commit()

        task = Task(
            user_id=user.id,
            title='Complete Project',
            description='Finish the group project',
            due_date=datetime.now(UTC) + timedelta(days=7),
            priority='high'
        )
        db.session.add(task)
        db.session.commit()

        # Test task was created
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, 'Complete Project')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'pending')

        # Test status update
        task.status = 'in_progress'
        db.session.commit()
        self.assertEqual(task.status, 'in_progress')

    def test_wellness_check(self):
        """Test wellness check functionality"""
        user = User(username='wellness', email='wellness@example.com', password='WellnessPass123!')
        db.session.add(user)
        db.session.commit()

        wellness = WellnessCheck(
            user_id=user.id,
            mood_score=8,
            stress_level=3,
            notes='Feeling good today'
        )
        db.session.add(wellness)
        db.session.commit()

        # Test wellness check was created
        self.assertIsNotNone(wellness.id)
        self.assertEqual(wellness.mood_score, 8)
        self.assertEqual(wellness.stress_level, 3)
        self.assertEqual(wellness.notes, 'Feeling good today')

    def test_assessment(self):
        """Test assessment creation and grade updates"""
        user = User(username='student', email='student@example.com', password='StudentPass123!')
        db.session.add(user)
        db.session.commit()

        assessment = Assessment(
            user_id=user.id,
            subject='Computer Science',
            title='Final Project',
            due_date=datetime.now(UTC).date() + timedelta(days=30),
            weight=0.4
        )
        db.session.add(assessment)
        db.session.commit()

        # Test assessment was created
        self.assertIsNotNone(assessment.id)
        self.assertEqual(assessment.subject, 'Computer Science')
        self.assertEqual(assessment.weight, 0.4)
        self.assertFalse(assessment.done)

        # Test grade update
        assessment.grade = 85.5
        assessment.done = True
        db.session.commit()
        self.assertEqual(assessment.grade, 85.5)
        self.assertTrue(assessment.done)

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_page_loads(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create an Account', response.data)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back', response.data)

    def test_signup_and_login(self):
        # Sign up a new user
        response = self.client.post('/signup', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Log in with the new user
        response = self.client.post('/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPass123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboard', response.data.lower())  # Adjust as needed for your dashboard page

    def test_profile_update(self):
        """Test profile update functionality"""
        # First create and login a user
        self.client.post('/signup', data={
            'username': 'profileuser',
            'email': 'profile@example.com',
            'password': 'ProfilePass123!',
            'confirm_password': 'ProfilePass123!'
        })
        
        self.client.post('/login', data={
            'username_or_email': 'profileuser',
            'password': 'ProfilePass123!'
        })

        # Test profile update
        response = self.client.post('/profile', data={
            'email': 'updated@example.com',
            'university': 'Updated University',
            'current_password': 'ProfilePass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Check for individual success messages
        self.assertIn(b'Email updated successfully', response.data)
        self.assertIn(b'University updated successfully', response.data)
        self.assertIn(b'Password updated successfully', response.data)

        # Verify the changes in the database
        user = User.query.filter_by(username='profileuser').first()
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.university, 'Updated University')

    def test_unit_distribution(self):
        """Test unit distribution API endpoint"""
        # Create and login a user
        self.client.post('/signup', data={
            'username': 'studyuser',
            'email': 'study@example.com',
            'password': 'StudyPass123!',
            'confirm_password': 'StudyPass123!'
        })
        
        self.client.post('/login', data={
            'username_or_email': 'studyuser',
            'password': 'StudyPass123!'
        })

        # Create some study sessions
        user = User.query.filter_by(username='studyuser').first()
        start_time = datetime.now(UTC)
        
        # Add study sessions for different subjects
        sessions = [
            StudySession(
                user_id=user.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=2),
                subject='Mathematics',
                notes='Studied calculus'
            ),
            StudySession(
                user_id=user.id,
                start_time=start_time + timedelta(hours=3),
                end_time=start_time + timedelta(hours=5),
                subject='Physics',
                notes='Studied mechanics'
            )
        ]
        db.session.add_all(sessions)
        db.session.commit()

        # Test the unit distribution API
        response = self.client.get('/api/unit_distribution')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertEqual(len(data['labels']), 2)
        self.assertEqual(len(data['data']), 2)
        self.assertIn('Mathematics', data['labels'])
        self.assertIn('Physics', data['labels'])

    def test_login_invalid(self):
        response = self.client.post('/login', data={
            'username_or_email': 'wronguser',
            'password': 'WrongPass123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username/email or password', response.data)

if __name__ == '__main__':
    unittest.main()
