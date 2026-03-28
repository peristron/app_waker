import sys
import time
import random
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# -----------------------------
# CONFIG: APP URLS (GROUPED)
# -----------------------------
# You can adjust groupings however you like. For now, let's split roughly
# evenly across 3 groups. You can use more/less groups and update the
# GitHub Actions matrix accordingly.

GROUPED_APPS = {
    1: [
        "https://csvexpl0rer.streamlit.app",
        "https://csvsplittertool.streamlit.app",
        "https://datasetexplorer.streamlit.app",
        "https://datasetexplorerv2.streamlit.app",
        "https://friendlyharanalyzer.streamlit.app",
        "https://p0dcasterapp2.streamlit.app",
        "https://physm0deller.streamlit.app",
        "https://p0dcaster.streamlit.app",
    ],
    2: [
        "https://exporterforrolesandpermissions.streamlit.app",
        "https://os-scorm-inspector.streamlit.app",
        "https://simplechartgenerator.streamlit.app",
        "https://wordcloudandsentimentanalyzer.streamlit.app",
        "https://wordcloudandsentimentanalyzer2.streamlit.app",
        "https://datasetexpl0rerupgraded.streamlit.app",
        "https://w0rdcl0udharvesterv4.streamlit.app",
        "https://signalfoundry.streamlit.app",
        "https://lineageanddependencieschecker.streamlit.app",
    ],
    3: [
        "https://datasetsunifiedexplorer.streamlit.app",
        "https://dataunifiedexplorer.streamlit.app",
        "https://refreshcsvcomparisontool.streamlit.app",
        "https://multillmchats.streamlit.app",
        "https://geospatialimpactmonitor.streamlit.app",
        "https://d2l-api-assistant.streamlit.app",
        "https://jbsrch-app.streamlit.app",
        "https://refact0redp0dcaster-2.streamlit.app",
        "https://storytellerpoc.streamlit.app",
        "https://scormifier.streamlit.app",
    ],
}

# If you call the script without a group number, this fallback list is used.
DEFAULT_APPS = [
    url for group_urls in GROUPED_APPS.values() for url in group_urls
]


USER_AGENTS = [
    # A few realistic Chrome user-agent strings on different OSes
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

    # Randomize viewport a bit
    width = random.randint(1024, 1600)
    height = random.randint(700, 1000)
    driver.set_window_size(width, height)
    print(f"[INFO] Set window size to {width}x{height}")

    return driver


def pick_app_subset(apps: List[str], max_per_run: int) -> List[str]:
    """Randomly select up to max_per_run apps from the provided list."""
    if max_per_run >= len(apps):
        # If max_per_run is >= number of apps, we still shuffle them
        random.shuffle(apps)
        return apps
    return random.sample(apps, k=max_per_run)


def interact_with_page(driver: webdriver.Chrome):
    """Perform basic interactions to look more like a real user."""
    try:
        # Simple scroll down then up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 3))
    except WebDriverException as e:
        print(f"[WARN] Interaction failed: {e}")


def wake_up(app_group: int = None, max_apps_per_run: int = 10):
    # Small random delay before starting to avoid exact cron alignment
    start_delay = random.uniform(5, 120)  # 5 seconds to 2 minutes
    print(
        f"[INFO] Starting wake_up with app_group={app_group}, "
        f"max_apps_per_run={max_apps_per_run}"
    )
    print(f"[INFO] Initial random delay: {start_delay:.1f} seconds...")
    time.sleep(start_delay)

    # Determine which apps we’re targeting this run
    if app_group is not None and app_group in GROUPED_APPS:
        apps = GROUPED_APPS[app_group][:]
        print(f"[INFO] Using app group {app_group} with {len(apps)} apps.")
    else:
        apps = DEFAULT_APPS[:]
        print(
            f"[INFO] No valid app_group provided; using DEFAULT_APPS "
            f"({len(apps)} apps)."
        )

    # Random subset selection
    apps_to_visit = pick_app_subset(apps, max_apps_per_run)
    total = len(apps_to_visit)
    print(f"[INFO] Selected {total} apps to visit this run.")

    if total == 0:
        print("[WARN] No apps selected to visit. Exiting.")
        return

    driver = None

    try:
        print("[INFO] Launching driver...")
        driver = get_driver()
        print("[INFO] Driver launched successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to start WebDriver: {e}")
        return

    # Shuffle visiting order
    random.shuffle(apps_to_visit)
    print("[INFO] Visiting apps in random order.")

    for i, url in enumerate(apps_to_visit, start=1):
        print(
            f"[INFO] [{i}/{total}] Visiting {url} at "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC"
        )
        try:
            driver.get(url)

            # Wait for Streamlit to boot
            boot_wait = random.uniform(10, 20)
            print(f"[INFO] Waiting {boot_wait:.1f} seconds for app to boot...")
            time.sleep(boot_wait)

            print(f"[INFO] Page Title: {driver.title!r}")

            # Basic interaction
            interact_with_page(driver)

        except Exception as e:
            print(f"[ERROR] Error visiting {url}: {e}")
            # Attempt to recover driver once
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

        # Random short pause between apps
        pause = random.uniform(3, 10)
        print(f"[INFO] Sleeping {pause:.1f} seconds before next app...")
        time.sleep(pause)

    print("[INFO] All selected apps visited. Closing browser.")
    try:
        driver.quit()
    except Exception:
        pass


if __name__ == "__main__":
    # Optional CLI arg: group number
    # Example: python wake_apps.py 2
    group_arg = None
    if len(sys.argv) > 1:
        try:
            group_arg = int(sys.argv[1])
        except ValueError:
            print(f"[WARN] Invalid group argument: {sys.argv[1]!r}; ignoring.")

    # You can tune max_apps_per_run; 10 is a reasonable starting point
    wake_up(app_group=group_arg, max_apps_per_run=10)
