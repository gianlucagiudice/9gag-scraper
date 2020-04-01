import json
import pickle

from selenium import webdriver


URL = 'https://9gag.com'


class Dumper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.cookies = None

    def dumpCookies(self):
        # Go to captcha page
        self.driver.get(URL)
        # Check if cookies are valid
        self.solveCapthca()
        # Dump cookies
        self.cookies = self.driver.get_cookies()
        # Export cookies
        self.exportCookies()
        # Close driver
        self.driver.quit()

    def parseCookies(self, cookies):
        self.cookies = {cookie['name']: cookie['value'] for cookie in cookies}

    def exportCookies(self):
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def solveCapthca(self):
        input('Resolve the captcha and press enter (press enter if the captcha is not present). . .')
