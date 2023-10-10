from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import locale

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
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
    time.sleep(7)
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, '(Default)')
    kpi.send_keys('\n')
    kpi = driver.find_element(By.LINK_TEXT, 'KPI Dashboard Info')
    kpi.send_keys('\n')
    time.sleep(5)
    return driver

def getDailyFuelVolume():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="7515da8f-90c4-456a-b39e-402665a30759"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    volume = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
    date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
    print(date.text)
    print(float(locale.atof(volume.text)))

def getDailyFuelSales():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="706da4e9-5865-452a-a7c3-aae010996c20"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
    date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
    print(date.text)
    print(float(locale.atof(sales.text[1:])))

def getMonthlyFuelSales():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="d1648a60-bdcf-4525-87e7-4226dbe224f0"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    txt = ''
    while txt == '':
        sales = window.find_element(By.XPATH, '//div[contains(@id,"DataTables_Table")]/div[2]/div[2]/table')
        txt = sakes.text
    print(parseMonthlyData(sales.text))

def getMonthlyFuelVolume():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="9ea7687d-5a89-435c-9916-1549d03ee223"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    # time.sleep(1)
    txt = ''
    while txt == '':
        volume = window.find_element(By.XPATH, '//div[contains(@id,"DataTables_Table")]/div[2]/div[2]/table')
        txt = volume.text
    print(parseMonthlyData(volume.text))

def getDailyStoreSales():
    window = openKPIDashboard(driver)
    report = window.find_element(By.XPATH, '//div[@id="b197098d-e7ea-4f57-923f-dba5f9b71b2b"]/div[2]/div[2]/div/div/a/span[2]')
    report.click()
    grid = window.find_element(By.LINK_TEXT, 'Grid')
    grid.click()
    sales = window.find_element(By.CSS_SELECTOR, '.ng-scope > .alignRight')
    date = window.find_element(By.CSS_SELECTOR, '.sorting_1')
    print(date.text)
    print(float(locale.atof(sales.text[1:])))


def openFuelSales(driver):
    pass
    # fuel = driver.find_element('xpath', '//*[@id="desktop-module-menu"]/div/ul/li[8]/a')
    # fuel.send_keys('\n')
    # time.sleep(3)
    # host = driver.find_element('xpath', '//*[@id="page-wrapper"]/div[2]/div[2]/div/div[2]/ss-report/div/div/div/ul/li/form/ss-criteria-set/div[1]/ss-site-picker/div/wc-sitepicker')
    # shadowRoot = driver.execute_script('return arguments[0].shadowRoot', host)
    # btn = shadowRoot.find_element(By.CLASS_NAME, 'input-group-btn > button')
    # btn.click()
    # //*[contains(@id,"component_wc_app_sitepciker")]/ss-site-picker/ss-site-picker-dlg/div/span/button
getDailyStoreSales()
while True:
    pass