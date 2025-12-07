from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # STEALTH: Masquerade as a real Windows PC running Chrome
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wake_up():
    # --- STEALTH: RANDOM START TIME ---
    # Sleep between 10 seconds and 600 seconds (10 minutes)
    # This prevents the logs from showing an exact hourly pattern
    start_delay = random.uniform(10, 600)
    print(f"😴 Random start delay: Sleeping for {start_delay:.1f} seconds...")
    time.sleep(start_delay)

    # --- STEALTH: RANDOM ORDER ---
    random.shuffle(app_urls)
    
    print(f"⏰ Waking up {len(app_urls)} apps using Headless Chrome...")
    
    driver = get_driver()
    
    for i, url in enumerate(app_urls):
        try:
            print(f"[{i+1}/{len(app_urls)}] 🚀 Visiting {url}...")
            driver.get(url)
            
            # Wait for Streamlit to boot
            time.sleep(15) 
            
            print(f"   ✅ Visited. Page Title: {driver.title}")
            
        except Exception as e:
            print(f"   ❌ Error on {url}: {e}")
            try:
                driver.quit()
                driver = get_driver()
            except:
                pass
        
        # STEALTH: Random tiny pause between apps
        time.sleep(random.uniform(2, 5))

    print("🏁 Done. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    wake_up()
