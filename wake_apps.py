from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app_urls = [
    "https://csvexpl0rer.streamlit.app",
    "https://csvsplittertool.streamlit.app",
    "https://datasetexplorer.streamlit.app",
    "https://datasetexplorerv2.streamlit.app",
    "https://friendlyharanalyzer.streamlit.app",
    "https://p0dcasterapp2.streamlit.app",
    "https://physm0deller.streamlit.app",
    "https://p0dcaster.streamlit.app",
    "https://exporterforrolesandpermissions.streamlit.app",
    "https://os-scorm-inspector.streamlit.app",
    "https://simplechartgenerator.streamlit.app",
    "https://wordcloudandsentimentanalyzer.streamlit.app",
    "https://wordcloudandsentimentanalyzer2.streamlit.app"
]

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Initialize Chrome Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wake_up():
    print(f"⏰ Waking up {len(app_urls)} apps using Headless Chrome...")
    
    driver = get_driver()
    
    for url in app_urls:
        try:
            print(f"🚀 Visiting {url}...")
            driver.get(url)
            
            # CRITICAL: Wait for JavaScript to execute and WebSocket to connect
            # 10 seconds is usually enough for Streamlit to acknowledge the user
            time.sleep(15) 
            
            # Optional: Check if the title indicates it loaded
            print(f"✅ Visited: {driver.title}")
            
        except Exception as e:
            print(f"❌ Error on {url}: {e}")
            # If driver crashes, try to restart it
            try:
                driver.quit()
                driver = get_driver()
            except:
                pass

    print("🏁 Done. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    wake_up()
