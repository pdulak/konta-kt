import unittest
from bankImport import SeleniumDrivers
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class MBank(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        SeleniumDrivers.user_pass = input("Enter pass: ")
        self.driver = SeleniumDrivers.load_driver()
        driver = self.driver
        driver.get("https://online.mbank.pl/pl/Login/")

    def setUp(self):
        driver = self.driver

    def test_mBank_login(self):
        driver = self.driver
        elem = driver.find_element_by_name("userID")
        elem.send_keys(SeleniumDrivers.user_name)
        elem = driver.find_element_by_name("pass")
        elem.send_keys(SeleniumDrivers.user_pass)
        driver.find_element_by_id("submitButton").click()
        # switch to full history
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "full-history"))
        )
        element.click()
        # switch to the other view
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "transactionListContainer"))
        )
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Zmień widok')]"))
        )
        element.click()
        # wait for select
        accountsCombo = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "rangepanel"))
        )

    def tearDown(self):
        # nothing to do
        1

    @classmethod
    def tearDownClass(self):
        # self.driver.close()
        1
