from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import argparse
from selenium.webdriver.chrome.options import Options

# Classes
from EsportsCapsuleFarmer.Setup.LoginHandler import LoginHandler
from EsportsCapsuleFarmer.Setup.VersionManager import VersionManager
# from EsportsCapsuleFarmer.Setup.Webdriver import Webdriver
from EsportsCapsuleFarmer.Setup.Logger.Logger import Logger
from EsportsCapsuleFarmer.Setup.Config import Config
from selenium import webdriver
from EsportsCapsuleFarmer.Match import Match

###################################################

CURRENT_VERSION = 3.7

parser = argparse.ArgumentParser(prog='CapsuleFarmer.exe', description='Farm Esports Capsules by watching lolesports.com.')
parser.add_argument('-b', '--browser', dest="browser", choices=['chrome', 'firefox', 'edge'], default="chrome",
                    help='Select one of the supported browsers')
parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                    help='Path to a custom config file')
parser.add_argument('-d', '--delay', dest="delay", default=600, type=int,
                    help='Time spent sleeping between match checking (in seconds)')
args = parser.parse_args()

print("*********************************************************")
print(f"*        Thank you for using Capsule Farmer v{CURRENT_VERSION}!        *")
print("* Please consider supporting League of Poro on YouTube. *")
print("*    If you need help with the app, join our Discord    *")
print("*             https://discord.gg/ebm5MJNvHU             *")
print("*********************************************************")
print()

# Mutes preexisting loggers like selenium_driver_updater
log = Logger().createLogger()
config = Config(log=log, args=args).readConfig()
hasAutoLogin, isHeadless, username, password, browser, delay = config.getArgs()

if not VersionManager.isLatestVersion(CURRENT_VERSION):
    log.warning("!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/EsportsCapsuleFarmer/releases/latest")

try:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # linux only
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    # driver = Webdriver(browser=browser, headless=isHeadless and hasAutoLogin).createWebdriver()
except Exception as ex:
    print(ex)
    print("CANNOT CREATE A WEBDRIVER! Are you running the latest browser version? Check the configured browser for any updates!\nPress any key to exit...")
    input()
    exit()

loginHandler = LoginHandler(log=log, driver=driver)

driver.get("https://lolesports.com/schedule")

# Handle login
if hasAutoLogin:
    try:
        loginHandler.automaticLogIn(username, password)
    except TimeoutException:
        log.error("Automatic login failed, incorrect credentials?")
        if isHeadless:
            driver.quit()
            log.info("Exiting...")
            exit()

while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
    if not hasAutoLogin:
        log.info("Waiting for login")
    else: 
        log.warning("Please log in manually")
    time.sleep(5)
log.debug("Okay, we're in")

Match(log=log, driver=driver).watchForMatches(delay=delay)
