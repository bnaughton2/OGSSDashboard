from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import locale
from datetime import datetime, timedelta, date
import pytz
from mySQLDB import *
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
tz_params = {'timezoneId': 'America/New_York'}
driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

def getStoreMembers():
    try:
        driver.get("https://www.syftanalytics.com/embed/ca4cc9ee-dc63-4dd8-8ac5-9a54bfec8159")
        driver.maximize_window()
        time.sleep(10)
        members = driver.find_element('xpath', '//*[@id="number-card-0"]/div[2]/div[1]/div[2]')
        val = int(members.get_attribute('innerHTML'))
        return val
    except:
        return -1

def main():
    dbObj = DB()
    try:
        time = datetime.now()
        print("Start Time: "+ time.strftime('%Y-%m-%d %H:%M:%S'))
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        data = getStoreMembers()
        dbObj.updateStoreMembersData(data, now)
    except BaseException as error:
        print("Something went wrong in storeMembers.py | " + str(error))
    finally:
        dbObj.closeDB()
        driver.quit()


if __name__ == "__main__":
    main()