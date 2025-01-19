# import requests
# from bs4 import BeautifulSoup
# import itertools
# import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def brute_force_attack(target_ip):
     # response = requests.get(target_ip)
     # soup = BeautifulSoup(response.text, 'html.parser')
     # form = soup.find('form')
     
     # initialisation de sellenium 
     driver = webdriver.Chrome() # Assurez-vous que ChromeDriver est dans le PATH
     driver.get(target_ip)
     
     # Attente pour s'assurer que la page est complètement chargée
     time.sleep(2)
     return "Good"
     