from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
import pytz

import re

import os, time

def saveHTML(driver, fileName: str):
    """
    Save the HTML seen by Selenium into the 'generated' folder.
    """
    folder = "generated"
    os.makedirs(folder, exist_ok=True)  # create the folder if didn't exists
    path = os.path.join(folder, fileName+".html")

    html = driver.page_source
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def Login(driver: WebDriver):
    """
    Log in on the schoolpack platform with the provided credentials by the .env file
    """
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")

    if not username or not password:
        print("[ERROR] USERNAME or PASSWORD environment variables are not set.")
        return

    try:
        # wait until the input are rendered
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vUSUCOD")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vPASS")))

        user_input = driver.find_element(By.ID, "vUSUCOD")
        pass_input = driver.find_element(By.ID, "vPASS")

        user_input.send_keys(username)
        pass_input.send_keys(password)

        # wait until the button is ready to be clicked
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "BUTTON1")))
        confirm_button = driver.find_element(By.ID, "BUTTON1")

        confirm_button.click()  
        
        # Wait until the iframe appears
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "gxp0_ifrm"))
        )

        # wait until the return button appears
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='BUTTON1' and @value='Regresar']"))
        )
        
        # get return button reference and then click it
        return_input = driver.find_element(By.ID, "BUTTON1")
        return_input.click()

        print("[INFO] Login successful, post-login element detected.")
    except Exception as e:
        print(f"[ERROR] Failed to login: {e}")

# OpenClasses prepare the session and put the scraper on the table ready to schedule class
def OpenClasses(driver: WebDriver):
    """
    open the available clases
    """
    try:
        # return to the default page (no iframe)
        driver.switch_to.default_content()

        # wait until the image appears 
        image_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "IMAGE18"))
        )

        # click on the image
        image_button.click()
    
        # wait until the element appears
        plan_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "span_W0030TMPDESART_0001"))
        )

        # get the span text
        plan_element.click()
        
        # click on start
        start_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "BUTTON1"))
        )
        start_element.click()
        
        #click on "Iniciar"
        init_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "W0030BUTTON1"))
        )
        init_element.click()
        print(f"[INFO] Plan de curso detectado")
        
    except Exception as e:
        print(f"[ERROR] Failed to open classes: {e}")

def selectClass(driver: WebDriver):
    """
    select the latest class to schedule
    """
    
    try:
        # switch to the corect iframe
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gxp0_ifrm")))
        driver.switch_to.frame(iframe)
 
        # Select the "Pending to schedule" option (value 2) from the dropdown
        dropdown_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vTPEAPROBO")))
        select = Select(dropdown_element)
        
        # Get the current table before applying filter
        old_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Grid1ContainerTbl")))
        select.select_by_value("2")  # Apply the filter
        
        # Wait until the table becomes stale (i.e., gets updated)
        WebDriverWait(driver, 10).until(EC.staleness_of(old_table))
        
        # Re-locate and switch back to the iframe since it might have been refreshed
        driver.switch_to.default_content()
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gxp0_ifrm")))
        driver.switch_to.frame(iframe)
        
        # Locate the updated table and search for a class row
        while True:
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Grid1ContainerTbl")))
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                text = row.text.lower()
                match = re.search(r"clase\s*\d+", text)
                if match:
                    print(f"[INFO] Matching class found: {match.group()}")
                    row.click()
                    
                    # Wait and click the assign button
                    assign = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "BUTTON1")))
                    assign.click()
                    print(f"[INFO] Class {match.group()} selected")
                    return

            # If no class row is found, click the next button and wait for table to reload
            print(f"[INFO] No class found on this page, attempting to load the next page")
            next_button = table.find_element(By.CLASS_NAME, "PagingButtonsNext")
            next_button.click()
            WebDriverWait(driver, 10).until(EC.staleness_of(table))

    except Exception as e:
        print(f"[ERROR] Failed to schedule class: {e}")
        return None

def confirmClass(driver: WebDriver, day: str):
    """
    Schedule the desired hours of the selected class.
    """

    target_times = ["18:00", "19:30"]
    confirmed_times = []

    try:
        # Switch to correct iframe
        refocus_iframe(driver, "gxp1_ifrm")

        if(day):
           # Select the desired day
            dropdown_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "vDIA")))
            select = Select(dropdown_element)
            
            # Get an element of the DOM
            old_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Grid1ContainerTbl")))
            
            # Select option (update DOM)
            select.select_by_value(day)
            print(f"[INFO] Day {day} selected")

            # Wait for dropdown to become stale (means content is reloading)
            WebDriverWait(driver, 10).until(EC.staleness_of(old_table)) 

        # Re-focus iframe and get updated table rows
        refocus_iframe(driver, "gxp1_ifrm")
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Grid1ContainerTbl")))
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for i in range(len(rows)):
            try:
                # Refocus and reload row list before each iteration (since the table may update)
                refocus_iframe(driver, "gxp1_ifrm")
                table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Grid1ContainerTbl")))
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                row = rows[i]

                time_element = row.find_element(By.XPATH, ".//td[@data-colindex='2']")
                time_text = time_element.text.strip()

                if time_text in target_times and time_text not in confirmed_times:
                    print(f"[INFO] Matching class time found: {time_text}")
                    row.click()

                    # Confirm class
                    confirm = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "BUTTON1")))
                    confirm.click()
                    time.sleep(3)

                    # Check for error message
                    try:
                        error_span = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'ErrorViewer')]/div"))
                        )
                        print("[WARNING] Error message displayed:")
                        print(error_span.text.strip())
                    except:
                        print(f"[INFO] Class at {time_text} successfully confirmed.")
                        confirmed_times.append(time_text)

            except Exception as inner_e:
                print(f"[ERROR] Could not confirm class at this row: {inner_e}")
                continue

        print(f"[INFO] Confirmed times: {confirmed_times}")

        if confirmed_times:
            # Ensure we exit the iframe context before continuing
            driver.switch_to.default_content()
            selectClass(driver)

    except Exception as e:
        print(f"[ERROR] Failed to confirm class: {e}")



def refocus_iframe(driver: WebDriver, iframe_id: str):
    """
    Return local Colombia day of the week with Sunday=1, Saturday=7.
    Optional offset shifts the day (e.g., offset=1 means tomorrow).
    """
    driver.switch_to.default_content()
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, iframe_id)))
    driver.switch_to.frame(iframe)

def get_colombia_day(offset:int=0)-> str:
    colombia_tz = pytz.timezone("America/Bogota")
    now_colombia = datetime.now(colombia_tz)
    
    # apply offset in days
    target_day = now_colombia + timedelta(days=offset)

    # convert sunday = 1 and saturday = 7
    # original monday = 0 and sunday = 7
    weekday = target_day.weekday()
    day_map = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '1'}
    return day_map[weekday]


