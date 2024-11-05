from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import os
from dotenv import load_dotenv

load_dotenv()

HEADLESS = os.environ.get('HEADLESS') in ("True", "true", "1")

class WebDriverManager:
    def __init__(self):
        self.headless = HEADLESS
        self.driver = self._init_driver()
        self.driver.implicitly_wait(10)

    def _init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        chrome_install = ChromeDriverManager().install()

        folder = os.path.dirname(chrome_install)
        chromedriver_path = os.path.join(folder, "chromedriver.exe")

        service = ChromeService(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def open_url(self, url):
        self.driver.get(url)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def click_element(self, by, value):
        element = self.find_element(by, value)
        element.click()

    def send_keys(self, by, value, keys):
        element = self.find_element(by, value)
        element.send_keys(keys)

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def close(self):
        self.driver.quit()