# WebCrawler_Products
The webcrawler code for the product information.


This repository is apart of a multi-stage Resume project.
The goal of this portion:
    Is to search specified websites for information on Products. Gather if they're available and at what price.
    For example, I'm attempting to find old DS games like Dragon Quest 4 on the DS.
    This will check website like gamestop and maybe Ebay
    Gather if the product is available and if it is at what price.

    This script will work in conjunction with Airflow and Firebase:
        For Airflow, I will be working towards running this on my Raspberry Pi 4, 4GB with Airflow as the scheduler.

        The data will store in Firebase. The goal is to also initially read the list of products I am tracking and what sites I have found them on first(Will look into building this out)
        
    For other information on this overall project:
        Besides Webcrawling, Firebase, and Airflow. The reason I'm using Firebase, is because this data will be read by an Android App written in Kotlin. Hence, why I'm using Firebase 
        And it's a cheap database service with a NoSql format that is doable for this project. 
        
    

Project Setup Notes:
To install all Python libraries for this project in your terminal type

    pip install -r requirements.txt

In a folder called Secrets outside this directory
-OverallDirectory
|-Secrets
|-{This Project}
   |-{This File}

(To be clear, this project folder and the secrets folder will be in the same directory, the secrets folder will not be inside this project folder)

The Secrets folder will be where I keep:
1. Chrome webdriver (Please download the most up to date version at https://chromedriver.chromium.org/downloads)
    (Future note, this link helped me https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2; AKA for anyone else, I am not responsible for this article. It's just one that helped me get WSL working.)
2. . . .


