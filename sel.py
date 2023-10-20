from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import locale
from datetime import datetime, timedelta
import mysql.connector
import pytz

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
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
    dashboard = driver.find_element(By.CSS_SELECTOR, '#desktop-module-menu .fade-selection-animation:nth-child(3) > a')
    dashboard.send_keys('\n')
    time.sleep(5)
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, '(Default)')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    time.sleep(3)
    return driver

def getDailyFuelVolume():
    volumeVal = 0
    dateVal = ''
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="7515da8f-90c4-456a-b39e-402665a30759"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    try:
        volume = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
        date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
        volumeVal = float(locale.atof(volume.text))
        dateVal = formatDate(date.text)
    except BaseException as error:
        print("No daily fuel volume data available.")
    return [volumeVal, dateVal]

def getDailyFuelSales():
    salesVal = 0
    dateVal = ''
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="706da4e9-5865-452a-a7c3-aae010996c20"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    try:
        sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
        date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
        salesVal = float(locale.atof(sales.text.strip('$')))
        dateVal = formatDate(date.text)
    except BaseException as error:
        print("No daily fuel sales data available.")
    return [salesVal, dateVal]

def getDailyStoreSales():
    salesVal = 0
    dateVal = ''
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="b197098d-e7ea-4f57-923f-dba5f9b71b2b"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    try:
        sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
        date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
        sales = float(locale.atof(sales.text.strip('$')))
        date = formatDate(date.text)
    except BaseException as error:
        print("No daily store sales data available.")
    return [salesVal, dateVal]

def getMonthlyFuelSales():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="d1648a60-bdcf-4525-87e7-4226dbe224f0"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    txt = ''
    while txt == '':
        sales = window.find_element(By.XPATH, '//div[contains(@id,"DataTables_Table")]/div[2]/div[2]/table')
        txt = sales.text
    print(parseMonthlyData(sales.text))

def getMonthlyFuelVolume():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="9ea7687d-5a89-435c-9916-1549d03ee223"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    txt = ''
    while txt == '':
        volume = window.find_element(By.XPATH, '//div[contains(@id,"DataTables_Table")]/div[2]/div[2]/table')
        txt = volume.text
    print(parseMonthlyData(volume.text))


print(getDailyStoreSales())
print(getDailyFuelSales())
print(getDailyFuelVolume())
while True:
    pass