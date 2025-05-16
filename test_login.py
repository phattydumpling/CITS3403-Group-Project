import unittest
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




    






if __name__ == "__main__":
    unittest.main()
