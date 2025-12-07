import requests
import time

# Cleaned URLs (removed trailing slashes)
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

def wake_up():
    print(f"⏰ Waking up {len(app_urls)} apps...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for url in app_urls:
        try:
            print(f"🚀 Pinging {url}...")
            # FIRST HIT: Triggers the boot process
            requests.get(url, headers=headers, timeout=5)
        except:
            # We expect a timeout or error here if it's deep sleeping. That's fine.
            pass
        
        # Wait for the container to spin up
        time.sleep(5)
        
        try:
            # SECOND HIT: Establishes connection
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                print(f"✅ Awake: {url}")
            else:
                print(f"⚠️ Status {response.status_code}: {url}")
        except Exception as e:
            print(f"❌ Failed: {url} - {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    wake_up()
