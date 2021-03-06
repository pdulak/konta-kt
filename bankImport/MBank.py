import os
import time
import unittest
import getpass
import SeleniumDrivers
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger


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
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Jednorazowy dostęp')]"))
        )
        element.find_element_by_xpath('../..').click()

        # switch to full history
        logger.info("Waiting for payments to appear")
        payments_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Cała historia')]" ))
        )

        # switch using JS :)
        driver.execute_script("document.querySelector('mega-menu').shadowRoot.querySelector('nav > ul > li:nth-child(2) > button').click()")
        time.sleep(1)
        driver.execute_script("document.querySelector('mega-menu').shadowRoot.querySelector('div > div > div > div:nth-child(3) > div:nth-child(1) > div > ul > li:nth-child(3) > a').click()")

        # select proper format - CSV
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Format zestawienia')]"))
        )
        select_div = element.find_element_by_xpath('../../div')
        select_div.click()
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'CSV')]"))
        )
        element.click()
        logger.info("CSV selection clicked")

        # select proper time - 3 months
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'ostatnie 3 miesiące')]"))
        )
        element.find_element_by_xpath('../../../input').click()
        logger.info("3 months selection clicked")

        # wait for the account select to be visible
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Z rachunku')]"))
        )
        # show accounts list
        select_div = element.find_element_by_xpath('../../div')
        select_div.click()
        logger.info("list of accounts clicked")

        # locate first account on the list
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "menu-root"))
        )
        accounts_list = element.find_element_by_xpath('div/div/div/ul')
        accounts = accounts_list.find_elements_by_tag_name("li")
        number_of_accounts = len(accounts)
        logger.info("number of accounts: {}".format(number_of_accounts))
        accounts[0].click()

        for i in range(0, number_of_accounts):
            logger.info("selecting accounts one by one, now it is {}".format(i))
            # wait for the account select to be visible
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Z rachunku')]"))
            )
            # show accounts list
            select_div = element.find_element_by_xpath('../../div')
            select_div.click()

            # locate first account on the list
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "menu-root"))
            )
            accounts_list = element.find_element_by_xpath('div/div/div/ul')
            accounts = accounts_list.find_elements_by_tag_name("li")
            accounts[i].click()

            # wait for the account select to be visible
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Pobierz zestawienie')]"))
            )
            element.find_element_by_xpath('../..').click()
            time.sleep(2)
            logger.info("download in progress")

        logger.info("operation finished")


    def tearDown(self):
        # nothing to do
        1

    @classmethod
    def tearDownClass(self):
        self.driver.close()
        1
