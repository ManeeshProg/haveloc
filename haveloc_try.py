from selenium import webdriver
from selenium.webdriver.common.by import By
driver=webdriver.Chrome()
driver.get('https://app.haveloc.com/login')
assert 'Haveloc' in driver.title
driver.quit()