from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium import webdriver
from decouple import config
import time
import re
import os

url = "https://busyliving.co.uk/"
username = config("login_username")
password = config("password")

# Log in to the site and get the source code
def site_login(URL):
    driver = webdriver.Chrome("C:/Users/emilf/Downloads/chromedriver.exe") 
    driver.get (URL)
    time.sleep(5)
    driver.find_element_by_class_name('cc-dismiss').click()
    time.sleep(2)
    driver.find_element_by_class_name('sidebar-menu-toggle').click()
    driver.find_element_by_id('user_email').send_keys(username)
    driver.find_element_by_id ('user_password').send_keys(password)
    driver.find_element_by_class_name("btn").click()
    WebDriverWait(driver, 10).until(EC.title_is("Busy Living"))
    html_source = driver.page_source
    driver.close()
    return html_source

# Define a class to store the results needed
class images:
    def __init__(self, title, file, picture):
        self.title = title
        self.file = file
        self.picture = picture

# Finds the elements needed and put them in an array
def finder(html):
    listings = []
    all_text = re.findall(r'(\<div class\=\"icons col-lg-2 col-md-2 col-sm-4 col-xs-6\".*\>(\n.*){14}</div>)', html)
    for i in range(len(all_text)):
        title = re.findall(r'title\=\"(.*)\"', all_text[i][0])
        file = re.findall(r'alt\=\"([^\"]*)\"', all_text[i][0])
        picture = re.findall(r'src\=\"(.*)\"', all_text[i][0])
        listings.append(images(title, file, picture))
    return listings

# Define the path to the files
directory = "s3://busyliving"
local = "C:\\Users\\emilf\\Downloads\\Ringley\\Images\\"
files_names = os.listdir("C:\\Users\\emilf\\Downloads\\Ringley\\Images\\")
grant = " --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers"

# Change the file
def name_changer(temp_item):
    print(f"\nWith which file do you want to replace it with? (enter the name of the file comprehensive of the extension and be wary of caps lock)\n")
    sub_item = input()
    if (sub_item == "skip"):
        # put stuff thats missing
                return None
    while sub_item not in files_names:
            print("\nThe name of the file is wrong\n")
            sub_item = input()
    os.popen(f'aws s3 cp {local}{sub_item} {directory}{temp_item[0]}')
    print(f"\nThe picture has been replaced by {sub_item}\n\n\n")
    # Create a text file containing all the names of the files that are replaced
    with open('substituted_files.txt', 'w') as filehandle:  
        filehandle.write('%s\n' %sub_item)

# Function that does it all
def replace(listings):
    for i in listings:
        print(f"\nThis picture is listed as {i.title[0]} on the website and the file is called {i.file[0]}\n")
        driver = webdriver.Chrome("C:/Users/emilf/Downloads/chromedriver.exe") 
        driver.get(i.picture[0])
        temp_item = re.findall(r'com(.*/.*png)', i.picture[0])
        name_changer(temp_item)
        driver.close()

# Runs the program
replace(finder(site_login(url)))