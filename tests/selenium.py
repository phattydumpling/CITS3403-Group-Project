import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleLoginTest(unittest.TestCase):
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
        
        username_field.send_keys("admin2@gmail.com")
        password_field.send_keys("Admin123@")
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

    def test_study_timer_starts(self):
        # First login to be able to access study area
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to study area page
        self.driver.get(f"{self.base_url}/study_area")

        # Wait for the timer display to appear
        timer_display = self.wait.until(EC.visibility_of_element_located((By.ID, "timer-display")))

        # Verify initial timer text is "25:00"
        self.assertEqual(timer_display.text, "25:00", f"Expected timer to start at 25:00 but got {timer_display.text}")

        # Find and click the start button
        start_button = self.wait.until(EC.element_to_be_clickable((By.ID, "start-button")))
        start_button.click()

        # Wait 3 seconds to allow timer to count down
        time.sleep(3)

        # Check the timer text again, it should have changed from 25:00
        updated_time = timer_display.text
        print("Timer after starting:", updated_time)
        self.assertNotEqual(updated_time, "25:00", "Timer did not start counting down.")

    def test_study_timer_pause(self):
        # First login to be able to access study area
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        email_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to study area page
        self.driver.get(f"{self.base_url}/study_area")

        # Wait for the timer display to appear
        timer_display = self.wait.until(EC.visibility_of_element_located((By.ID, "timer-display")))

        # Start the timer
        start_button = self.wait.until(EC.element_to_be_clickable((By.ID, "start-button")))
        start_button.click()

        # Wait 3 seconds to let timer run
        time.sleep(3)
        running_time = timer_display.text

        # Click pause button
        pause_button = self.wait.until(EC.element_to_be_clickable((By.ID, "pause-button")))
        pause_button.click()

        # Wait 2 seconds to verify timer is paused
        time.sleep(2)
        paused_time = timer_display.text

        print("Time before pause:", running_time)
        print("Time after pause:", paused_time)

        # Convert mm:ss strings to total seconds helper
        def time_to_seconds(t):
            m, s = map(int, t.split(":"))
            return m * 60 + s

        running_seconds = time_to_seconds(running_time)
        paused_seconds = time_to_seconds(paused_time)

        # Assert paused_seconds is less than or equal to running_seconds
        # but not less than running_seconds by more than 2 seconds
        self.assertTrue(
            paused_seconds <= running_seconds and (running_seconds - paused_seconds) <= 2,
            f"Timer did not pause correctly; time changed from {running_time} to {paused_time} which is more than 2 seconds."
        )

    def test_friends_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to friends page
        self.driver.get(f"{self.base_url}/friends")
        time.sleep(2)  # Give the page time to load

        # Verify we can find the body element (most basic check)
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)

    def test_profile_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to profile page
        self.driver.get(f"{self.base_url}/profile")
        time.sleep(2)  # Give the page time to load

        # Verify we can find the body element (most basic check)
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)
        
        # Verify we can find a form element (profile pages typically have forms)
        form = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        self.assertTrue(form.is_displayed(), "Profile form should be visible")

    def test_assessments_page(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to assessments page
        self.driver.get(f"{self.base_url}/assessments")
        time.sleep(2)  # Give the page time to load

        # Verify we can find the body element (most basic check)
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)
        
        # Verify we can find a heading element (pages typically have headings)
        heading = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertTrue(heading.is_displayed(), "Page should have a heading")

    def test_data_shared_with_you(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to data shared with you page
        self.driver.get(f"{self.base_url}/data_shared_with_you")
        time.sleep(2)  # Give the page time to load

        # Verify we can find the body element (most basic check)
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)
        
        # Verify we can find a div element (pages typically have divs)
        div = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "div")))
        self.assertTrue(div.is_displayed(), "Page should have content")

    def test_shared_data_history(self):
        # First login
        self.driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to shared data history page
        self.driver.get(f"{self.base_url}/shared_data_history")
        time.sleep(2)  # Give the page time to load

        # Verify we can find the body element (most basic check)
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed(), "Page body should be visible")
        
        # Verify we're not on the login page
        self.assertNotIn("Login", self.driver.title)
        
        # Verify we can find a div element (pages typically have divs)
        div = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "div")))
        self.assertTrue(div.is_displayed(), "Page should have content")

if __name__ == "__main__":
    unittest.main() 