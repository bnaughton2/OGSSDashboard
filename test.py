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
locale.setlocale(locale.LC_ALL, '')



# fuel = driver.find_element('xpath', '//*[@id="desktop-module-menu"]/div/ul/li[8]/a')
# fuel.send_keys('\n')
# site = driver.find_element('xpath', '//*[@id="component_wc_app_sitepciker_615.3396415788302"]/ss-site-picker/ss-site-picker-dlg/div/input')
# site.click()

def parseMonthlyData(string):
    tmp = string.split('\n')
    d = dict()
    for i in tmp:
        arr = i.split(' ')
        d[arr[0]] = float(locale.atof(arr[1].strip('$')))
    return d

def formatDate(string):
    local = pytz.timezone('America/New_York')
    naive = datetime.strptime(string+"  06:00:00", '%m/%d/%Y %H:%M:%S')
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    date = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
    return date

def openKPIDashboard(driver):
    driver.get("https://sscsta.sscsinc.com/Auth.App/#/login?returnUrl=%2FCStore.Web%2FAccount%2FLogin%3FreturnUrl%3D%252FCStore.Web%252FHome%252FIndex")
    # driver.get("https://sscsta.sscsinc.com/TransactionAnalysis.App/#!/fuelsales/?startDate=20230926000000&endDate=20230926235959&selectedSites=007151001&salestype=Amount&totaltype=Day&autosubmit=true")
    driver.maximize_window()
    driver.implicitly_wait(10)
    username = driver.find_element('xpath', '//*[@id="page-wrapper"]/div/div/div/div[2]/div/div[2]/div[1]/form/div[1]/input')
    username.send_keys('v7151mgr3')
    password = driver.find_element('xpath', '//*[@id="page-wrapper"]/div/div/div/div[2]/div/div[2]/div[1]/form/div[2]/input')
    password.send_keys('Camera1$')
    button = driver.find_element('xpath', '//*[@id="page-wrapper"]/div/div/div/div[2]/div/div[2]/div[1]/form/button')
    button.click()
    time.sleep(3)
    return driver

def main():
    try:
        d = openKPIDashboard(driver)
        d.get('https://sscsta.sscsinc.com/TransactionAnalysis.App/#!/storestats/?selectedSites=007151001')
        time.sleep(2)
        button = d.find_element('xpath', '//button[contains(.,"Submit")]')
        button.send_keys('\n')
        time.sleep(2)
        item = d.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight:nth-child(3)')
        transactions = int(item.text)
        print(transactions)
    finally:
        d.quit()


if __name__ == "__main__":
    main()
