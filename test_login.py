import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service


class StudyTrackerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Correctly indented block
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


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()