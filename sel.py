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
    dashboard = driver.find_element(By.XPATH, '//div[@id="desktop-module-menu"]/div/ul/li[3]/a')
    dashboard.send_keys('\n')
    time.sleep(8)
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, '(Default)')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    time.sleep(5)
    return driver

def getDailyFuelVolume():
    volumeVal = 0
    dateVal = ''
    try:
        window = openKPIDashboard(driver)
        report = window.find_element(By.XPATH, '//div[@id="7515da8f-90c4-456a-b39e-402665a30759"]/div[2]/div[2]/div/div/a/span[2]')
        report.click()
        grid = window.find_element(By.LINK_TEXT, 'Grid')
        grid.click()
    except BaseException as error:
        print("Failure to open daily volume data: " + str(error))
    else:
        try:
            volume = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
            date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
            volumeVal = float(volume.text.replace(',', ''))
            dateVal = formatDate(date.text)
        except BaseException as error:
            print("No daily fuel volume data available: "  + str(error))
    return [volumeVal, dateVal]

def getDailyFuelSales():
    salesVal = 0
    dateVal = ''
    try:
        window = openKPIDashboard(driver)
        report = window.find_element(By.XPATH, '//div[@id="706da4e9-5865-452a-a7c3-aae010996c20"]/div[2]/div[2]/div/div/a/span[2]')
        report.click()
        grid = window.find_element(By.LINK_TEXT, 'Grid')
        grid.click()
    except BaseException as error:
        print("Failure to open daily sales data: " + str(error))
    else:
        try:
            sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
            date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
            salesVal = float(sales.text.strip('$').replace(',', ''))
            dateVal = formatDate(date.text)
        except BaseException as error:
            print("No daily fuel sales data available: " + str(error))
    return [salesVal, dateVal]

def getDailyStoreSales():
    salesVal = 0
    dateVal = ''
    try:
        window = openKPIDashboard(driver)
        report = window.find_element(By.XPATH, '//div[@id="b197098d-e7ea-4f57-923f-dba5f9b71b2b"]/div[2]/div[2]/div/div/a/span[2]')
        report.click()
        grid = window.find_element(By.LINK_TEXT, 'Grid')
        grid.click()
    except BaseException as error:
        print("Failure to open daily store data: " + str(error))
    else:
        try:
            sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
            date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
            salesVal = float(sales.text.strip('$').replace(',', ''))
            dateVal = formatDate(date.text)
        except BaseException as error:
            print("No daily store sales data available: " + str(error))
    return [salesVal, dateVal]

def getStoreData():
    vals = [-1,-1]
    try:
        driver.get("https://www.syftanalytics.com/embed/33ff3d0d-4066-4e4a-960b-a0010f6bd7bb")
        driver.maximize_window()
        time.sleep(10)
        members = driver.find_element('xpath', '//*[@id="number-card-0"]/div[2]/div/div[2]')
        vals[0] = int(float(members.get_attribute('innerHTML')))
        sales = driver.find_element('xpath', '//*[@id="dashboard-graph-heading-2"]/div[2]/div[1]')
        vals[1] = float(sales.get_attribute('innerHTML').strip("$"))
    except BaseException as error:
        print("Error retrieving store members/sales: " + str(error))
    return vals

def main():
    try:
        dbObj = DB()
        time = datetime.now()
        print("Start Time: "+ time.strftime('%Y-%m-%d %H:%M:%S'))
        store = getDailyStoreSales()
        fuelSales = getDailyFuelSales()
        fuelVol = getDailyFuelVolume()
        storeData = getStoreData()
        if(fuelSales[0] != 0 and fuelSales[1] != '') and (fuelVol[0] != 0 and fuelVol[1] != ''):
            if(fuelSales[1] == fuelVol[1]):
                data = [fuelSales[0], fuelVol[0]]
                date = fuelSales[1]
                dbObj.upsertFuelSalesData(data, date)
        if(store[0] != 0 and store[1] != '')  and (storeData[0] != -1 and storeData[1] != -1):
            data = [store[0], storeData[0], storeData[1]]
            date = store[1]
            print(data)
            dbObj.upsertStoreSalesData(store[0], date)
            dbObj.updateStoreMembersData([storeData[0], storeData[1]], date)
    except:
        print("Something went wrong in sel.py")
    finally:
        dbObj.closeDB()
        driver.quit()


if __name__ == "__main__":
    main()
