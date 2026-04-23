import time
import random
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# ----------------------------------
# TIER 1: IMPORTANT APPS (ACTIVE)
# ----------------------------------
# These are the apps you care most about keeping warm.
IMPORTANT_APPS: List[str] = [
    # datahub_datasets_unified_explorer
    "https://datasetsunifiedexplorer.streamlit.app",

    # datahub_unified_explorer
    "https://dataunifiedexplorer.streamlit.app",

    # jbsrch
    "https://jbsrch-app.streamlit.app",

    # refact0red_p0dcaster
    "https://refact0redp0dcaster-2.streamlit.app",

    # signalfoundry
    "https://signalfoundry.streamlit.app",

    # multi_llm_chat
    "https://multillmchats.streamlit.app",

    # roles_and_permissions_exporter
    "https://exporterforrolesandpermissions.streamlit.app",

    # scormifier
    "https://scormifier.streamlit.app",

    # story_teller_poc
    "https://storytellerpoc.streamlit.app",

    # csvcomparison tool
    "https://refreshcsvcomparisontool.streamlit.app"
]


# ----------------------------------
# TIER 2: LOWER PRIORITY APPS (OPTIONAL)
# ----------------------------------
# These are currently ignored. You can:
#  - keep them commented out, OR
#  - uncomment and fold some into IMPORTANT_APPS (or create a second script).
#
# LOWER_PRIORITY_APPS: List[str] = [
#     "https://csvexpl0rer.streamlit.app",
#     "https://csvsplittertool.streamlit.app",
#     "https://datasetexplorer.streamlit.app",
#     "https://datasetexplorerv2.streamlit.app",
#     "https://friendlyharanalyzer.streamlit.app",
#     "https://p0dcasterapp2.streamlit.app",
#     "https://physm0deller.streamlit.app",
#     "https://p0dcaster.streamlit.app",
#     "https://os-scorm-inspector.streamlit.app",
#     "https://simplechartgenerator.streamlit.app",
#     "https://wordcloudandsentimentanalyzer.streamlit.app",
#     "https://wordcloudandsentimentanalyzer2.streamlit.app",
#     "https://datasetexpl0rerupgraded.streamlit.app",
#     "https://w0rdcl0udharvesterv4.streamlit.app",
#     "https://lineageanddependencieschecker.streamlit.app",
#     "https://refreshcsvcomparisontool.streamlit.app",
#     "https://geospatialimpactmonitor.streamlit.app",
#     "https://d2l-api-assistant.streamlit.app",
# ]


USER_AGENTS = [
    # A few realistic UA strings
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_driver() -> webdriver.Chrome:
    """Create and return a headless Chrome WebDriver with randomized UA and viewport."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    ua = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={ua}")
    print(f"[INFO] Using User-Agent: {ua}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    width = random.randint(1024, 1600)
    height = random.randint(700, 1000)
    driver.set_window_size(width, height)
    print(f"[INFO] Set window size to {width}x{height}")

    return driver


def interact_with_page(driver: webdriver.Chrome):
    """Perform basic interactions to look more like a real user."""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 3))
    except WebDriverException as e:
        print(f"[WARN] Interaction failed: {e}")


def wake_up(max_apps_per_run: int = 9):
    # Initial random delay so the pattern isn't perfectly on the cron tick
    start_delay = random.uniform(5, 120)  # 5 seconds to 2 minutes
    print(f"[INFO] Starting wake_up for IMPORTANT_APPS ({len(IMPORTANT_APPS)} total).")
    print(f"[INFO] Initial random delay: {start_delay:.1f} seconds...")
    time.sleep(start_delay)

    if not IMPORTANT_APPS:
        print("[WARN] IMPORTANT_APPS list is empty; nothing to do.")
        return

    # Random subset (for future-proofing), but by default touch all 9.
    apps = IMPORTANT_APPS[:]
    random.shuffle(apps)
    if max_apps_per_run < len(apps):
        apps = apps[:max_apps_per_run]

    total = len(apps)
    print(f"[INFO] Selected {total} important apps to visit this run.")

    driver = None
    try:
        print("[INFO] Launching driver...")
        driver = get_driver()
        print("[INFO] Driver launched successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to start WebDriver: {e}")
        return

    for i, url in enumerate(apps, start=1):
        print(
            f"[INFO] [{i}/{total}] Visiting {url} at "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC"
        )
        try:
            driver.get(url)

            boot_wait = random.uniform(10, 20)
            print(f"[INFO] Waiting {boot_wait:.1f} seconds for app to boot...")
            time.sleep(boot_wait)

            print(f"[INFO] Page Title: {driver.title!r}")
            interact_with_page(driver)

        except Exception as e:
            print(f"[ERROR] Error visiting {url}: {e}")
            # Try to recover driver once
            try:
                print("[INFO] Attempting to restart driver...")
                driver.quit()
            except Exception:
                pass
            try:
                driver = get_driver()
                print("[INFO] Driver restarted successfully.")
            except Exception as inner:
                print(f"[ERROR] Failed to restart WebDriver: {inner}")
                break

        pause = random.uniform(3, 10)
        print(f"[INFO] Sleeping {pause:.1f} seconds before next app...")
        time.sleep(pause)

    print("[INFO] Done visiting important apps. Closing browser.")
    try:
        driver.quit()
    except Exception:
        pass


if __name__ == "__main__":
    # You can tune max_apps_per_run; 9 equals "visit all important apps"
    wake_up(max_apps_per_run=9)
