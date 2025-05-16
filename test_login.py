import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class StudyTrackerTests(unittest.TestCase):

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.base_url = "http://127.0.0.1:5000"
        self.wait = WebDriverWait(self.driver, 10)  


    def tearDown(self):
        self.driver.quit()

    def test_login(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        wait = WebDriverWait(driver, 10)

        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")

        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Optional: wait for dashboard to load before assertions
        wait.until(EC.title_contains("Dashboard"))

        self.assertIn("Dashboard", driver.title)

    def test_login_nonexistent_account(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        wait = WebDriverWait(driver, 10)

        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("fakeuser@example.com")

        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("wrongpassword")
        password_field.send_keys(Keys.RETURN)

        # Wait up to 10 seconds for the error message
        error_div = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.bg-red-50.text-red-700.border.border-red-200")
            )
        )

        self.assertTrue(error_div.is_displayed())
        print("Error message text:", error_div.text)

    def test_login_with_empty_fields(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        # Find the login button and click it
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Login'] | //input[@type='submit']"))
        )
        login_button.click()

        # Use JavaScript to check if the username_or_email input is valid
        is_username_valid = driver.execute_script(
            "return document.getElementsByName('username_or_email')[0].checkValidity();"
        )
        is_password_valid = driver.execute_script(
            "return document.getElementsByName('password')[0].checkValidity();"
        )

        # Assert that both inputs are invalid (since they are empty and required)
        self.assertFalse(is_username_valid)
        self.assertFalse(is_password_valid)

    def test_study_timer_starts(self):
        driver = self.driver
        
        # First login to be able to access study area
        driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        # Wait until redirected to dashboard or home page
        self.wait.until(EC.title_contains("Dashboard"))

        # Navigate to study area page
        driver.get(f"{self.base_url}/study_area")

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
        driver = self.driver

        # login and navigate to study area as you already do
        driver.get(f"{self.base_url}/login")
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username_or_email")))
        email_field.send_keys("admin2@gmail.com")
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)
        self.wait.until(EC.title_contains("Dashboard"))

        driver.get(f"{self.base_url}/study_area")
        timer_display = self.wait.until(EC.visibility_of_element_located((By.ID, "timer-display")))

        start_button = self.wait.until(EC.element_to_be_clickable((By.ID, "start-button")))
        start_button.click()

        time.sleep(3)
        running_time = timer_display.text

        pause_button = self.wait.until(EC.element_to_be_clickable((By.ID, "pause-button")))
        pause_button.click()

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







    






if __name__ == "__main__":
    unittest.main()
