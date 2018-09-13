import requests
import time
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# Drop list:
# https://www.supremecommunity.com/season/spring-summer2018/droplists/

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--silent")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_path = "driver/chromedriver.exe"

def main():
    purchaseInput = inputFromCSV()
    supremeInput(purchaseInput)
    time.sleep(50)
    # while True:
    #     checkInstockItems()
    print("Done")
    browser.quit()

def supremeInput(inputs):
    for input in inputs:
        browser=webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_path)
        browser.get(input[0])
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'cctrl')))
        browser.find_element_by_css_selector("#add-remove-buttons input").click()
        time.sleep(1)
        browser.find_element_by_css_selector("a.button.checkout").click()
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'pay')))
        browser.find_element_by_css_selector("input#order_billing_name.string.required").send_keys(input[1])
        browser.find_element_by_css_selector("input#order_email.string.email.required").send_keys(input[2])
        browser.find_element_by_css_selector("input#order_tel.string.required").send_keys(input[3])
        browser.find_element_by_css_selector("input#bo.string.required").send_keys(input[4])
        if input[5]:
            browser.find_element_by_css_selector("input#oba3.string.optional").send_keys(input[5])
        browser.find_element_by_css_selector("input#order_billing_zip.string.required").send_keys(input[6])
        browser.find_element_by_css_selector("input#order_billing_city.string.required").send_keys(input[7])
        browser.find_element_by_css_selector("select#order_billing_state.select.optional").send_keys(input[8])
        if input[8] is "CANADA":
            browser.find_element_by_css_selector("select#order_billing_country.select.optional").send_keys(input[9])
        browser.find_element_by_css_selector("input#nnaerb.string.required").send_keys(input[10])
        browser.find_element_by_css_selector("select#credit_card_month").send_keys(input[11])
        browser.find_element_by_css_selector("select#credit_card_year").send_keys(input[12])
        browser.find_element_by_css_selector("input#orcer.string.required").send_keys(input[13])
        time.sleep(.5)
        checkbox = browser.find_element_by_css_selector("input#order_terms.checkbox")
        actions = ActionChains(browser)
        actions.move_to_element(checkbox)
        actions.click(checkbox)
        actions.perform()
        browser.find_element_by_css_selector("input.button").click()

def inputFromCSV():
    inputs = []
    try:
        inputFile = open("inputs.csv",'r')
    except:
        print("No file named inputs.csv")
    lines = inputFile.readlines()
    for line in lines:
        line = line.replace('\n','')
        inputs += [line.split(',')]
    inputFile.close()
    print(inputs)
    return  inputs

def checkInstockItems():
    items = []
    instockItems = []
    check = 0

    supremeAll = requests.get("http://www.supremenewyork.com/shop/all")
    soup = BeautifulSoup(supremeAll.content, "lxml")
    links = soup.find_all("a")

    for link in links:
        url = link.get("href")
        pages = ["/shop/jackets/", "/shop/shirts/", "/shop/tops_sweaters", "/shop/sweatshirts", "/shop/pants/", "/shop/hats/", "/shop/bags/", "/shop/accessories/", "/shop/skate"]
        for page in pages:
            if page in url:
                supremeItemURL = "http://www.supremenewyork.com" + url
                supremeItemPage = requests.get(supremeItemURL)
                soup = BeautifulSoup(supremeItemPage.content, "lxml")
                soldout = soup.find("b", { "class" : "button sold-out"})
                name = soup.find("h1", { "class" : "protect"})
                color = soup.find("p", { "class" : "style protect"})
                sizes = soup.find_all("option")
                if soldout:
                    if color:
                        items.append(['Out of Stock', name.text, color.text, '', supremeItemURL])
                    else:
                        items.append(['Out of Stock', name.text, '', '', supremeItemURL])
                else:
                    if sizes:
                        for size in sizes:
                            items.append(['In Stock', name.text, color.text, size.text, supremeItemURL])
                    else:
                        if color:
                            items.append(['In Stock', name.text, color.text, '', supremeItemURL])
                        else:
                            items.append(['In Stock', name.text, '', '', supremeItemURL])

    readCSVFile('instock.csv', instockItems, 'In Stock')
    writeCSVFile('instock.csv',instockItems, items, check)

    if check:
        print("THRE IS A RESTOCK OF ITEMS")
    else:
        print("Failed to find any restocked items")

    return 0

def readCSVFile(file,array,stock):
    # Read in instock.csv to instockItems
    try:
        instockRead = open(file,'r')
    except:
        print("No file named %s", file)
    lines = instockRead.readlines()
    for line in lines:
        line = line.replace('\n','')
        item = [stock]
        item = item + line.split(',')
        array.append(item)
    instockRead.close()

def writeCSVFile(file,array, items, check):
    # Write to instock.csv and check if there are new stock items
    instockWrite = open(file,'w')
    outofstockWrite= open('outofstock.csv','w')
    instockWrite.write('Name,Color,Size,URL\n')
    outofstockWrite.write('Name,Color,Size,URL\n')
    for item in items:
        if 'In Stock' in item:
            if item not in array :
                print("NEW ITEM IN STOCK: %s - %s - %s" % (item[1],item[2],item[3]))
                instockWrite.write('%s,%s,%s,%s\n' % (item[1],item[2],item[3],item[4]))
                check = 1
            else:
                instockWrite.write('%s,%s,%s,%s\n' % (item[1],item[2],item[3],item[4]))
        else:
            outofstockWrite.write('%s,%s,%s,%s\n' % (item[1],item[2],item[3],item[4]))

    instockWrite.close()

main()
