# wake_apps.py
import requests
import time

# the Streamlit App URLs

app_urls = [
    "https://csvexpl0rer.streamlit.app/",
    "https://csvsplittertool.streamlit.app/",
    "https://datasetexplorer.streamlit.app/",
    "https://datasetexplorerv2.streamlit.app/",
    "https://friendlyharanalyzer.streamlit.app/",
    "https://p0dcasterapp2.streamlit.app/",
    "https://physm0deller.streamlit.app/",
    "https://p0dcaster.streamlit.app/",
    "https://exporterforrolesandpermissions.streamlit.app/",
    "https://os-scorm-inspector.streamlit.app/",
    "https://simplechartgenerator.streamlit.app/",
    "https://wordcloudandsentimentanalyzer.streamlit.app/",
    "https://wordcloudandsentimentanalyzer2.streamlit.app/"
]

def wake_up():
    print(f"⏰ Waking up {len(app_urls)} apps...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for url in app_urls:
        try:
            # setting a timeout because sleeping apps take time to boot
            # don't actually need to wait for the full page load, just the connection
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ success: {url}")
            else:
                print(f"⚠️ status {response.status_code}: {url}")
                
        except requests.exceptions.Timeout:
            print(f"⏳ timeout (app is likely waking up): {url}")
        except Exception as e:
            print(f"❌ error waking {url}: {str(e)}")
            
        # courtesy to the API/Server
        time.sleep(1)

if __name__ == "__main__":
    wake_up()
