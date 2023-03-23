import requests
import re
import json
from time import sleep
from datetime import datetime
import xml.etree.ElementTree as ET

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyrebase


SECRETS = "../Secrets/"

with open("json/startUrls.json", "r") as file:
    urls = json.load(file)

# Create the web object that we can interact with.
browser = webdriver.Chrome(SECRETS.join("webdriver"))


def checkGamestop(gameName, url):
    """
    Runs the logic for checking Gamestops availability for the game.
    """
    addressLoc = "../Secrets/address.json" 
    # Get my Address from the secret folder.
    with open(addressLoc) as file:
        address = json.load(file)
    
    browser.get(url)

    # Variables that will be pased into the database 
    gameAvailability = None

    b =  browser.find_element(By.CLASS_NAME, "component, primary-details-row,  pricing-redesign")
    gamePrice = b.find_element(By.CLASS_NAME, "actual-price, actual-price-strikethroughable-span").text

    # Get the grouping of where all the buttons live
    buttonsTag = browser.find_element(By.CLASS_NAME, "cart-and-ipay, divider-line, top-divider")

    verifyAddressButton = buttonsTag.find_element(By.CLASS_NAME, 'btn-check-availability, btn, btn-primary, add-to-cart-redesign')
    # First check if we need to verify our shipping address.
    if verifyAddressButton.is_displayed():
        verifyAddressButton.click()
        verifyAddressBox = browser.find_element(By.ID, "SDDStoreVerifyModal")

        sleep(2) # Needs to pause for a couple seconds before it continues
        # Add address in for delivery
        verifyAddressBox.find_element(By.ID, 'address1').send_keys(address['street'])
        verifyAddressBox.find_element(By.ID, 'city').send_keys(address['city'])
        verifyAddressBox.find_element(By.ID, 'state').send_keys(address['state'])
        verifyAddressBox.find_element(By.ID, 'zipCode').send_keys(address['zip'])

        # Submit form and close the window (Next step will verify if product is unavail/Avail)
        verifyAddressBox.find_element(By.NAME, 'submit').click()
        verifyAddressBox.find_element(By.CLASS_NAME, "close, pull-right").click()


    purchaseButton = buttonsTag.find_element(By.CLASS_NAME, "add-to-cart, btn, btn-primary, add-to-cart-redesign, all")
    availableStatus = purchaseButton.get_attribute('innerHTML')

    if availableStatus == 'Not Available':
        # TODO: Pass to Database Price and that product is not Available.
        gameAvailability = False
    else:
        # TODO: Pass to Database Price and that product is Available.
        gameAvailability = True
    insertIntoFirebase(gameName, gamePrice, gameAvailability, "gamestop")

def insertIntoFirebase(gameName, gamePrice, gameAvailability, company):
    with open("../Secrets/firebaseConfig.json", "r") as file:
        firebaseConfig = json.load(file)

    firebase = pyrebase.initialize_app(firebaseConfig)
    currTime = datetime.today().strftime('%m-%d-%Y, %H:%M')
    database = firebase.database()

    data = {
        "site" : company,
        "Price" : gamePrice,
        "Available" : gameAvailability
    }

    database.child("GameNames").child(f"{gameName}/{company}/{currTime}").set(data)





def romanToInt(s : str) -> int:
    roman_to_int = {
        "I" : 1,
        "V" : 5,
        "X" : 10,
        "L" : 50,
        "C" : 100,
        "D" : 500,
        "M" : 1000,
    }
    last_rn = ""
    sum = 0
    sum_to_add = 0
    for rn in s:
        if (last_rn == "I" and (rn == "V" or rn == "X")) or \
           (last_rn == "X" and (rn == "L" or rn == "C")) or\
           (last_rn == "C" and (rn == "D" or rn == "M")):
            sum += (-1 * sum_to_add)
        else:
            sum += sum_to_add
        sum_to_add = roman_to_int[rn]
        last_rn = rn #save the rn so we can check later if It's I before V... etc..
    sum += sum_to_add
    return sum

def intToRoman(num: int) -> str:
    int_to_roman = {
        1000 : "M",
        900 : "CM",
        500 : "D",
        400 : "CD",
        100 : "C",
        90 : "XC",
        50 : "L",
        40 : "XL",
        10 : "X",
        9 : "IX",
        5 : "V",
        4 : "IV",
        1 : "I"
    }
    
    outString = ""
    for value, symbol in int_to_roman.items():
        # Deduct from num and add the symbol to the string.
        while value <= num:
            print(num)
            num -= value
            outString += symbol

    return outString.lower()



def searchXml(root, gameName):
    # Stores each word in the gameName
    gameNameList = []
    # Stores each match in a list.
    matches = []

    for node in gameName.lower().split(" "):
        if node.isdigit() and int(node) < 4000: # Parameter for function is less than 4000.
            gameNameList.append(intToRoman(int(node)))
        gameNameList.append(node)

    # Search the XML on the Gamestop XML to the URL
    for element in  root.findall(".//{*}loc"):
        url = element.text
        productString = url.split("/")[-2]
        # Removes patterns such as ---playstation-4...
        if re.search("---", productString):
            i = productString.find("---")
            productString = productString[:i]
            
        count = 0
        for word in gameNameList:
            # regex issue is if you have a decimal number like 4.4 on Dragonquest 4
            # This handles that issue.
            if re.search(f"([^.]|^){word}([^.]|$)", productString):
                count+=1
        if count > 0:
            matches.append((productString, url, count))

    matches.sort(key=lambda key: key[2], reverse=True)
    
    return matches


def getProductMatches(company, userInput):
    """
    Takes in the companys name to get the Xml file(s)
    and parses the information to find the 
    """
    if not urls.get(company):
        print("Invalid company")
        return False
    
    sitemap = urls[company]

    # Some companies, like target have multiple XML's
    # TODO: Make Target's version with multiple iterations...
    if type(sitemap) is not list:
        headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
        response = requests.get(sitemap, headers=headers)
        if not response.status_code:
            print(f"Error: {response.status_code}")
            return False

        # Create an XML root to pass into searchXml
        root = ET.fromstring(response.text)
        return searchXml(root=root, gameName=userInput)
              



class Company:
    def __init__(self):
        pass
    
    @staticmethod
    def formatData():
        """
        Formats the Json data into the expected data // Or checks the format on how it's sent.
        """
        return False

    @staticmethod
    def saveProduct(jsonObject):
        """Method is used to return false in a jsonObject to its dictionary"""
        return False

    @staticmethod
    def searchProduct():
        return False

class GameStop(Company):
    @staticmethod
    def formatData():
        return False

    @staticmethod
    def saveProduct(jsonObject):
        with open ("../json/gamestop.json", "wb", encoding='utf-8') as file:
            json.dump(jsonObject)



# The below code I believe will mostly just be for testing. Data above will be reworked into class structures.
mainUrlDict = {
    "gamestop" : "https://www.gamestop.com/"
}


browser.get("https://www.gamestop.com/")

userInput = 0
# Bad engine to help me generate game data.
while 1:
    print("*"*50)
    userInput = input("Please enter name of the game you'd like to keep track of: ")
    if str(userInput) == "-1":
        break 
    matches = getProductMatches("gamestop", userInput)
    for i, match in enumerate(matches[:10]):
        print(f"{i}: {match[0]}")
    
    userInput = input("Select any of these, or hit -1 to search another game: ")
    if userInput != "-1":

        # Where I left off. This URL is the one we need to search.
        scrapeUrl = matches[int(userInput)][1]

    print("*"*50)
browser.close()