from distutils.log import error
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC


import smtplib, ssl, sys, os
from email.message import EmailMessage


def sendMails( message, emailTarget = "alwindenherder@gmail.com", title="Watch available!"):
    currentDir = os.path.abspath(os.path.dirname(sys.argv[0]))+'\\'

    # get credentials
    with open(currentDir+'user.txt', 'r') as userFile:
        userString = userFile.read()
    with open(currentDir+'pass.txt', 'r') as passFile:
        passString = passFile.read()
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = title
    msg['From'] = "Alwins Server"
    msg['To'] = emailTarget

    # Create a secure SSL context
    context = ssl.create_default_context()
    port = 465  # For SSL

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(userString, passString)
        server.send_message(msg)
        print('sent email')
        print('to: %s'%(emailTarget))
        print('message: %s'%(title))
        
        
def getWatchLinks():
    with open("links.json", 'r') as openLinks:
        linksContent = json.loads(openLinks.read())
    return linksContent

def startDriver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://www.swatch.com/nl-nl')
    cookieButton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div/div/div/div/div[3]/button[2]")))
    if cookieButton.text == "Ja":
        cookieButton.click()
    else:
        print('error occurred')
        sendMails('ERROR DURING RUNTIME')
        return
    return driver
    
def checkAvailability(driver, watchLink):
    driver.get(watchLink)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[1]/div/aside/div[1]/div[3]/div[2]")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[1]/div/aside/div[1]/div[3]/div[2]")))
    iconContainer = driver.find_element(by=By.XPATH, value="/html/body/div[1]/main/div/div/div[1]/div[1]/div/aside/div[1]/div[3]/div[2]/button/span")
    subIcons = iconContainer.find_elements(By.XPATH, value=".//*")
    iconCheck = []
    for icon in subIcons:
        iconCheck.append(icon.is_displayed())
    return iconCheck != [True, False, True, False, False, False]

def mainFunction():
    watchLinks = getWatchLinks()
    driver= startDriver()
    emailMessage = ""
    try:
        for watchLink in watchLinks:
            watchAvailable = checkAvailability(driver, watchLink)
            if watchAvailable:
                emailMessage += watchLink + '\n'
        if emailMessage != "":
            sendMails(emailMessage)
    except Exception as e:
        driver.close()
        sendMails(str(e), title='WatchChecker - Error during runtime')
        exit()


mainFunction()    
    