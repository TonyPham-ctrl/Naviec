from selenium import webdriver
from selenium.webdriver.common.by import By

driver=webdriver.Safari()
driver.get("https://www.nemweb.com.au/REPORTS/")
driver.implicitly_wait(10)
element=driver.find_element(By.TAG_NAME, "a")
element.click()
