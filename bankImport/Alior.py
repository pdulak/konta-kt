import os
import unittest
import SeleniumDrivers


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

        elem = driver.find_element_by_id("login")
        elem.send_keys(SeleniumDrivers.alior_user_name)

        driver.find_element_by_xpath("//button[@type='submit']").click()

    def tearDown(self):
        # nothing to do
        1

    @classmethod
    def tearDownClass(self):
        # self.driver.close()
        1
