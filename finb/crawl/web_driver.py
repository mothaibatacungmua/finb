import os
from finb import PROJECT_PATH
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_driver_path = os.path.join(PROJECT_PATH, "chromedriver")

gdriver = None

def make_driver():
    global gdriver
    if gdriver is None:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--verbose')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": os.path.join(PROJECT_PATH, "tmp"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        gdriver = webdriver.Chrome(
            executable_path=chrome_driver_path, options=chrome_options
        )
    return gdriver

def close_driver():
    gdriver.close()


# function to take care of downloading file
def enable_download_headless(browser, download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)