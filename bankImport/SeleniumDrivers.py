# SeleniumDrivers module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import os
sys.path.insert(0, os.getcwd()) # workaround to import kontaKt settings
from kontaKt import privateSettings

current_driver = "Chrome"
mbank_user_name = privateSettings.mbank_user_name
alior_user_name = privateSettings.alior_user_name
user_pass = ""


def load_driver(download_dir=None):
    if current_driver == "Chrome":
        return load_chrome(download_dir)
    return load_firefox(download_dir)


def load_firefox(download_dir=None):
    driver = webdriver.Firefox()
    driver.maximize_window()
    return driver


def load_chrome(download_dir=None):
    options = Options()
    options.add_argument("--start-maximized")

    if download_dir:
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options=options)
    return driver
