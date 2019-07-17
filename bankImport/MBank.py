import os
import time
import unittest
import getpass
import SeleniumDrivers
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class MBank(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        SeleniumDrivers.user_pass = getpass.getpass("Enter pass: ")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        dest_dir = os.path.join(base_dir, 'temp')
        self.driver = SeleniumDrivers.load_driver(dest_dir)
        driver = self.driver
        driver.get("https://online.mbank.pl/pl/Login/")

    def setUp(self):
        driver = self.driver

    def test_mBank_login(self):
        driver = self.driver
        elem = driver.find_element_by_name("userID")
        elem.send_keys(SeleniumDrivers.mbank_user_name)
        elem = driver.find_element_by_name("pass")
        elem.send_keys(SeleniumDrivers.user_pass)
        driver.find_element_by_id("submitButton").click()
        # switch to full history
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "full-history"))
        )
        element.click()
        # switch to the other view
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "transactionListContainer"))
        )
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Zmień widok')]"))
        )
        element.click()

        # switch to iFrame
        driver.get("https://online.mbank.pl/csite/account_oper_list.aspx")
        # wait for select
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "MenuAccountsCombo"))
        )

        # select proper options on the form
        driver.find_element_by_id("lastdays_radio").click()
        days_field = driver.find_element_by_id("lastdays_days")
        days_field.clear()
        days_field.send_keys("4")
        period_select = driver.find_element_by_id("lastdays_period")
        period_select.click()
        period_options = [x for x in period_select.find_elements_by_tag_name("option")]
        period_options[1].click()

        driver.find_element_by_id("export_oper_history_check").click()
        format_select = driver.find_element_by_id("export_oper_history_format")
        format_select.click()
        format_options = [x for x in format_select.find_elements_by_tag_name("option")]
        format_options[2].click()

        # loop by accounts, get CSV
        accounts_combo = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "MenuAccountsCombo"))
        )
        accounts = [x for x in accounts_combo.find_elements_by_tag_name("option")]
        number_of_accounts = len(accounts)

        for i in range(0, number_of_accounts):
            accounts_combo = driver.find_element_by_id("MenuAccountsCombo")
            accounts_combo.click()
            accounts = [x for x in accounts_combo.find_elements_by_tag_name("option")]
            accounts[i].click()
            driver.find_element_by_id("Submit").click()
            time.sleep(1)

    def tearDown(self):
        # nothing to do
        1

    @classmethod
    def tearDownClass(self):
        self.driver.close()
        1
