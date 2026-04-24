from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def stay_awake(url):
    options = Options()
    options.add_argument("--headless") # Run without a window
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print(f"Visiting {url} to keep it awake...")
    driver.get(url)
    time.sleep(5) # Wait for page to load
    print("Session refreshed.")
    driver.quit()

if __name__ == "__main__":
    MY_APP_URL = "https://analytica-adpushup-pro.streamlit.app/"
    stay_awake(MY_APP_URL)
