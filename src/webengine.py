import requests
from selenium import webdriver

SECRETS = "../../Secrets/"


# Create the web object that we can interact with.
browser = webdriver.Chrome(SECRETS.join("webdriver"))



# The below code I believe will mostly just be for testing. Data above will be reworked into class structures.
mainUrlDict = {
    "gamestop" : "https://www.gamestop.com/"
}

browser.get("https://www.gamestop.com/")


