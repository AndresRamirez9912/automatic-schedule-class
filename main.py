from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helper.helper import *

time.sleep(10)

chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=chrome_options
)


driver.implicitly_wait(10)  # fallback time

# go to the scholpack page
driver.get("https://schoolpack.smart.edu.co/idiomas/alumnos.aspx") 

# login
Login(driver)

# open classes
OpenClasses(driver)

# select class to schedule
selectedClass = selectClass(driver)

# select hours and day
confirmClass(driver) #schedule current day

next_day = get_colombia_day(1)
confirmClass(driver, next_day) #schedule next day

# delete chromium
driver.quit()

