# SeleniumDrivers module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

current_driver = "Chrome"
user_name = "mbank_user_name_here"
user_pass = ""

def load_driver():
    if current_driver == "Chrome":
        return load_chrome()
    else:
        return load_firefox()

def load_firefox():
    driver = webdriver.Firefox()
    driver.maximize_window()
    return driver


def load_chrome():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_options=options)
    return driver
