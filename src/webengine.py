import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
SECRETS = "../../Secrets/"


# Create the web object that we can interact with.
browser = webdriver.Chrome(SECRETS.join("webdriver"))

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
    
    # This shwos the top 10 of the matches. 
    for m in matches[:10]:
        print(m)


# The below code I believe will mostly just be for testing. Data above will be reworked into class structures.
mainUrlDict = {
    "gamestop" : "https://www.gamestop.com/"
}

browser.get("https://www.gamestop.com/")


browser.close()