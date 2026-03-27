from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
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
    "https://wordcloudandsentimentanalyzer2.streamlit.app",
    "https://datasetexpl0rerupgraded.streamlit.app",
    "https://w0rdcl0udharvesterv4.streamlit.app",
    "https://signalfoundry.streamlit.app",
    "https://lineageanddependencieschecker.streamlit.app",
    "https://datasetsunifiedexplorer.streamlit.app",
    "https://dataunifiedexplorer.streamlit.app",
    "https://refreshcsvcomparisontool.streamlit.app",
    "https://multillmchats.streamlit.app",
    "https://geospatialimpactmonitor.streamlit.app",
    "https://d2l-api-assistant.streamlit.app",
    "https://jbsrch-app.streamlit.app",
    "https://refact0redp0dcaster-2.streamlit.app",
    "https://storytellerpoc.streamlit.app",
    "https://scormifier.streamlit.app"
]

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")        # modern headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Stealth: look like a real recent Chrome on Windows
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Use GitHub's pre-installed Chrome + ChromeDriver (no download needed)
    service = Service(os.environ["CHROMEWEBDRIVER"])
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wake_up():
    # Random start delay (anti-pattern detection)
    start_delay = random.uniform(10, 600)
    print(f"😴 Random start delay: Sleeping for {start_delay:.1f} seconds...")
    time.sleep(start_delay)

    random.shuffle(app_urls)
    
    print(f"⏰ Waking up {len(app_urls)} Streamlit apps using pre-installed Headless Chrome...")

    driver = get_driver()

    for i, url in enumerate(app_urls):
        try:
            print(f"[{i+1}/{len(app_urls)}] 🚀 Visiting {url}...")
            driver.get(url)
            time.sleep(15)  # Streamlit needs time to fully load
            print(f"   ✅ Visited. Page Title: {driver.title}")
        except Exception as e:
            print(f"   ❌ Error on {url}: {e}")
            try:
                driver.quit()
                driver = get_driver()
            except:
                pass
        
        time.sleep(random.uniform(2, 5))

    print("🏁 Done. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    wake_up()
