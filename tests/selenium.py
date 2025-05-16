import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

class SimpleLoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test application context
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('Test123@')
        )
        db.session.add(test_user)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://127.0.0.1:5000"
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_simple_login(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        
        username_field.send_keys("test@example.com")
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        self.assertIn("Dashboard", self.driver.title)

    def test_invalid_login(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        
        username_field.send_keys("wronguser@example.com")
        password_field.send_keys("wrongpass123")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        # Verify we're still on the login page
        self.assertIn("Login", self.driver.title)

    def test_study_area(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to study area page
        self.driver.get(f"{self.base_url}/study_area")
        time.sleep(2)

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

    def test_dashboard(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're on the dashboard
        self.assertIn("Dashboard", self.driver.title)

    def test_profile_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to profile page
        self.driver.get(f"{self.base_url}/profile")
        time.sleep(2)

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

    def test_assessments_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to assessments page
        self.driver.get(f"{self.base_url}/assessments")
        time.sleep(2)

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

    def test_friends_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to friends page
        self.driver.get(f"{self.base_url}/friends")
        time.sleep(2)

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

    def test_wellness_check(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("test@example.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Test123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to wellness check page
        self.driver.get(f"{self.base_url}/wellness_check")
        time.sleep(2)

        # Verify we can find the body element
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

if __name__ == "__main__":
    unittest.main() 