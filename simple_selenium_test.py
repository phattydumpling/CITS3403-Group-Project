import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class SimpleLoginTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://127.0.0.1:5000"
        # Add implicit wait
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.quit()

    def test_simple_login(self):
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Find and fill in the login form
        username_field = self.driver.find_element(By.NAME, "username_or_email")
        password_field = self.driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        # Check if we're on the dashboard
        self.assertIn("Dashboard", self.driver.title)

    def test_invalid_login(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        username_field = self.driver.find_element(By.NAME, "username_or_email")
        password_field = self.driver.find_element(By.NAME, "password")
        
        username_field.send_keys("wronguser")
        password_field.send_keys("wrongpass")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        # Check for error message
        error_message = self.driver.find_element(By.CLASS_NAME, "bg-red-50")
        self.assertTrue(error_message.is_displayed())

    def test_empty_login_fields(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Find login button and click without entering any data
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        time.sleep(1)
        # Check for validation messages
        validation_messages = self.driver.find_elements(By.CLASS_NAME, "bg-red-50")
        self.assertTrue(len(validation_messages) > 0)

    def test_logout_functionality(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        username_field = self.driver.find_element(By.NAME, "username_or_email")
        password_field = self.driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Click logout
        logout_button = self.driver.find_element(By.CSS_SELECTOR, "a[href='/logout']")
        logout_button.click()
        
        time.sleep(2)
        # Check if redirected to login page
        self.assertIn("Login", self.driver.title)

    def test_remember_me_functionality(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Check remember me checkbox
        remember_me = self.driver.find_element(By.NAME, "remember_me")
        remember_me.click()
        
        # Login
        username_field = self.driver.find_element(By.NAME, "username_or_email")
        password_field = self.driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Close and reopen browser
        self.driver.quit()
        self.setUp()
        
        # Visit dashboard directly
        self.driver.get(f"{self.base_url}/dashboard")
        time.sleep(2)
        
        # Should still be logged in
        self.assertIn("Dashboard", self.driver.title)

    def test_password_reset_request(self):
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Click forgot password link
        forgot_password_link = self.driver.find_element(By.LINK_TEXT, "Forgot your password?")
        forgot_password_link.click()
        
        time.sleep(2)
        # Enter email for password reset
        email_field = self.driver.find_element(By.NAME, "email")
        email_field.send_keys("admin@example.com")
        email_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        # Check for success message
        success_message = self.driver.find_element(By.CLASS_NAME, "bg-green-50")
        self.assertTrue(success_message.is_displayed())

    def test_registration_form(self):
        self.driver.get(f"{self.base_url}/signup")
        time.sleep(2)
        
        # Fill registration form
        username_field = self.driver.find_element(By.NAME, "username")
        email_field = self.driver.find_element(By.NAME, "email")
        password_field = self.driver.find_element(By.NAME, "password")
        confirm_password_field = self.driver.find_element(By.NAME, "confirm_password")
        
        username_field.send_keys("newuser")
        email_field.send_keys("newuser@example.com")
        password_field.send_keys("NewPass123!")
        confirm_password_field.send_keys("NewPass123!")
        
        # Submit form
        register_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        register_button.click()
        
        time.sleep(3)
        # Check if redirected to login or dashboard
        self.assertIn("Login", self.driver.title)

    def test_password_mismatch_registration(self):
        self.driver.get(f"{self.base_url}/signup")
        time.sleep(2)
        
        # Fill registration form with mismatched passwords
        username_field = self.driver.find_element(By.NAME, "username")
        email_field = self.driver.find_element(By.NAME, "email")
        password_field = self.driver.find_element(By.NAME, "password")
        confirm_password_field = self.driver.find_element(By.NAME, "confirm_password")
        
        username_field.send_keys("newuser2")
        email_field.send_keys("newuser2@example.com")
        password_field.send_keys("NewPass123!")
        confirm_password_field.send_keys("DifferentPass123!")
        
        # Submit form
        register_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        register_button.click()
        
        time.sleep(2)
        # Check for password mismatch error
        error_message = self.driver.find_element(By.CLASS_NAME, "bg-red-50")
        self.assertTrue(error_message.is_displayed())

    def test_invalid_email_format(self):
        self.driver.get(f"{self.base_url}/signup")
        time.sleep(2)
        
        # Try to register with invalid email
        email_field = self.driver.find_element(By.NAME, "email")
        email_field.send_keys("invalid-email")
        email_field.send_keys(Keys.TAB)  # Move focus to trigger validation
        
        time.sleep(1)
        # Check for email validation error
        validation_error = self.driver.find_element(By.CLASS_NAME, "bg-red-50")
        self.assertTrue(validation_error.is_displayed())

if __name__ == "__main__":
    unittest.main() 