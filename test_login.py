import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class StudyTrackerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service)  
        cls.driver.maximize_window()
        cls.base_url = "http://localhost:5000"

    def test_login(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        email_field = driver.find_element(By.NAME, "username_or_email")
        email_field.send_keys("admin2@gmail.com")

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("Admin123@")
        password_field.send_keys(Keys.RETURN)

        time.sleep(2)

        print("Current URL after login:", driver.current_url)
        print("Page title after login:", driver.title)
        print("Page content snippet:", driver.page_source[:500])  # First 500 chars

        self.assertIn("Dashboard", driver.title)

    def test_login_nonexistent_account(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        # Enter invalid credentials
        driver.find_element(By.NAME, "username_or_email").send_keys("fakeuser@example.com")
        driver.find_element(By.NAME, "password").send_keys("wrongpassword" + Keys.RETURN)

        # Wait up to 5 seconds for the error message to appear
        wait = WebDriverWait(driver, 5)
        error_div = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bg-red-50.text-red-700.border.border-red-200"
))
        )

        # Assert the error message is displayed
        self.assertTrue(error_div.is_displayed())

        # Optional: print error message text
        print("Error message text:", error_div.text)


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    


if __name__ == "__main__":
    unittest.main()