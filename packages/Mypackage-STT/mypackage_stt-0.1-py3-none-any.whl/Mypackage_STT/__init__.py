#pip install selenium

from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
#pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd

from selenium.webdriver.chrome.options import Options




chrome_options = Options()
chrome_options.add_argument("--log-level=3")   # suppress console logs
chrome_options.add_argument("--silent") 
chrome_options.add_argument("--use-fake-ui-for-media-stream") #bypass the mic permission
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

website = "https://budhyadeb2503.github.io/Speech-to-Text-html-site/"
driver.get(website)

rec_file = f"{getcwd()}\\input.txt"

def listen():
    try:
        start_button = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.ID,'startButton')))
        start_button.click()
        print("Listning..")
        output_text = ""

        is_second_click = False
        while True:
            output_element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID,'output')))
            current_text = output_element.text.strip()
            if "START" in start_button.text and is_second_click:
                if output_text:
                    is_second_click = False
            elif "Listning.." in start_button.text:
                is_second_click = False  
            if current_text != output_text:
                 output_text = current_text
                 with open(rec_file,"w") as file:
                     file.write(output_text.lower())
                     print("User : " + output_text)  
    except KeyboardInterrupt:
        pass                       
    except Exception as e:
        print(e)                    




