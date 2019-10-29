import os
import unittest
import SeleniumDrivers
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

class Alior(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        dest_dir = os.path.join(base_dir, 'temp/alior')
        self.driver = SeleniumDrivers.load_driver(dest_dir)
        driver = self.driver
        driver.get("https://system.aliorbank.pl/sign-in")

    def setUp(self):
        driver = self.driver

    def test_alior_login(self):
        driver = self.driver

        # enter user ID
        elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "login"))
        )
        elem.send_keys(SeleniumDrivers.alior_user_name)

        driver.find_element_by_xpath("//button[@type='submit']").click()

        # enter password
        elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'js-password-masked-fields')]"))
        )
        maskedInputs = elem.find_elements_by_xpath("//div[contains(@class, 'js-password-masked-fields')]/div[contains(@class, 'masked-input-wrapper')]/input[not(contains(@class, 'visually-hidden'))]")

        logger.info(len(maskedInputs))
        for i, e in enumerate(maskedInputs):
            if e.is_enabled():
                e.send_keys(SeleniumDrivers.user_pass[i])
                logger.info("On location {} placing char {}".format(i, SeleniumDrivers.user_pass[i]))



    def tearDown(self):
        # nothing to do
        1

    @classmethod
    def tearDownClass(self):
        # self.driver.close()
        1
