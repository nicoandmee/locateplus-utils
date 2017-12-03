from time import time
import requests
import re
from time import sleep
from bs4 import BeautifulSoup
from json import load
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


fileName = "{}.csv".format(time())

#Load login details and search query data
with open("login_details.txt") as r:
    auth = load(r)

user_id = auth['USERNAME']
pwd = auth['PASSWORD']
acnt_num = auth['ACCOUNTNUM']
wait_more = float(auth['LAZY_LOGIN'])
wait_less =float(auth['LAZY_FORM'])

with open("LocatePlus.csv", "r") as f:
    rows = f.read().split("\n")
#-------------------------------------


def get_answer(text):
    if "What was the street number of the house you grew up in" in text:
        answer = "4455"
    elif "Where did you spend your childhood summers" in text:
        answer = "Los Angeles"
    else:
        answer = "San Luis Obispo"
    print('Answer is: {}'.format(answer))
    return answer


driver = webdriver.Chrome()

wait = WebDriverWait(driver, 60)
driver.get("https://app.locateplus.com/")

sleep(wait_more)

# Login form fill
username = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")

username.send_keys(user_id)
sleep(wait_less)
password.send_keys(pwd)

driver.find_element_by_name("approve").click()
driver.find_element_by_name("submit").click()

wait.until(EC.presence_of_element_located((By.NAME, "a_0")))
soup = BeautifulSoup(driver.page_source, "html5lib")
question_no = soup.find("input", attrs={"required": "required"})['name']
answer_box = driver.find_element_by_name(question_no)
sleep(wait_less)
answer_box.send_keys(get_answer(soup.text))
sleep(1)
driver.find_element_by_name("submit").click()
sleep(wait_more)

for row in rows[1:]:
    driver.get(
        "https://app.locateplus.com/searchOptions.asp?searchType=2&searchBy=21&searchTypeOpt=Phone&searchByOpt=Residential&reportID=51")
    try:
        row = re.sub("^\s*|\s*$", "", row)
        row = re.sub("\s\s+", " ", row)
        row = re.sub("^ | $", "", row)
        row = row.replace(" | ", "|")
        print(row)
        info = row.split("|")
        first_name = driver.find_element_by_name("firstname")
        last_name = driver.find_element_by_name("lastname")
        address = driver.find_element_by_name("address")
        state = Select(driver.find_element_by_name("state"))
        state.select_by_value(info[3])
        sleep(1)
        city = Select(driver.find_element_by_name("city"))

        first_name.send_keys(info[0])
        sleep(wait_less)
        last_name.send_keys(info[1])
        sleep(wait_less)
        address.send_keys(info[2])
        sleep(wait_less)
        city.select_by_value(info[4].upper())
        driver.find_element_by_name('city')

        sleep(1)

        check_boxes = driver.find_elements_by_id('chkGLB')
        for cbox in check_boxes:
            try:
                cbox.send_keys(Keys.SPACE)
                break
            except:
                pass
        
        submit_btns = driver.find_elements_by_id('Submit')
        for sbtn in submit_btns:
            try:
                sbtn.send_keys(Keys.ENTER)
                break
            except:
                pass

        soup = BeautifulSoup(driver.page_source, "html5lib")
        phone, name, address, old_carrier, carrier = "","","","",""
        phone = soup.find("span", attrs={"id": "phoneResltsPhoneNumber"}).text
        try:
            name = soup.find("a", attrs={"id": "Person_linked_href_search_1"}).text
        except:
            pass
        try:
            address = soup.find("div", attrs={"id": "mapped_address_data_1"}).text
        except:
            pass
        try:
            carrier_table = soup.find_all("td", attrs={"class": "content phoneResultsCarierData"})
            for table in carrier_table:
                if "Historical Carrier" in table.text:
                    old_carrier = soup.find("div", attrs={"class": "carrierContact"}).ul.text
                else:
                    carrier = soup.find("div", attrs={"class": "carrierContact"}).ul.text
        except:
            pass

        data = '"' + '","'.join(re.sub("\s\s+|\n+", " ", str(x)) for x in [info[0], info[1], info[2], info[3], info[4], phone, name, address, old_carrier, carrier]) + '"'
        print(data)
        with open(fileName, "a") as d:
            d.write(data)
            d.write("\n")


    except Exception as e:
        with open("LocatePlus_log.txt", "a") as log:
            log.write(str(e))
            log.write("\n")
        with open("LocatePlus_Error.txt", "a") as error:
            error.write(row)
            error.write("\n")
