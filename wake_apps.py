import random
import time
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# ----------------------------------
# TIER 1: IMPORTANT APPS (ACTIVE)
# ----------------------------------
IMPORTANT_APPS: List[str] = [
    "https://datasetsunifiedexplorer.streamlit.app",
    "https://dataunifiedexplorer.streamlit.app",
    "https://jbsrch-app.streamlit.app",
    "https://refact0redp0dcaster-2.streamlit.app",
    "https://signalfoundry.streamlit.app",
    "https://multillmchats.streamlit.app",
    "https://exporterforrolesandpermissions.streamlit.app",
    "https://scormifier.streamlit.app",
    "https://refreshcsvcomparisontool.streamlit.app",
    "https://geospatialimpactmonitor.streamlit.app",
    "https://signalfoundryv2.streamlit.app",
    "https://d2l-api-assistant.streamlit.app",
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def dedupe_urls(urls: List[str]) -> List[str]:
    """Remove duplicates while preserving the original order."""
    return list(dict.fromkeys(urls))


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

    # On GitHub Actions ubuntu-latest, Chrome/ChromeDriver are already available.
    # Let Selenium use the runner's installed driver instead of downloading one.
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    width = random.randint(1024, 1600)
    height = random.randint(700, 1000)
    driver.set_window_size(width, height)
    print(f"[INFO] Set window size to {width}x{height}")

    return driver


def interact_with_page(driver: webdriver.Chrome) -> None:
    """Perform basic interactions to look more like a real user."""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 3))
    except WebDriverException as exc:
        print(f"[WARN] Interaction failed: {exc}")


def wake_up(max_apps_per_run: Optional[int] = None) -> None:
    start_delay = random.uniform(5, 120)
    print(f"[INFO] Starting wake_up for IMPORTANT_APPS ({len(IMPORTANT_APPS)} total).")
    print(f"[INFO] Initial random delay: {start_delay:.1f} seconds...")
    time.sleep(start_delay)

    apps = dedupe_urls(IMPORTANT_APPS)

    if not apps:
        print("[WARN] IMPORTANT_APPS list is empty; nothing to do.")
        return

    removed_duplicates = len(IMPORTANT_APPS) - len(apps)
    if removed_duplicates:
        print(f"[INFO] Removed {removed_duplicates} duplicate URL(s) from IMPORTANT_APPS.")

    random.shuffle(apps)

    if max_apps_per_run is not None and max_apps_per_run > 0:
        apps = apps[:max_apps_per_run]

    total = len(apps)
    print(f"[INFO] Selected {total} important apps to visit this run.")

    driver = None
    try:
        print("[INFO] Launching driver...")
        driver = get_driver()
        print("[INFO] Driver launched successfully.")
    except Exception as exc:
        print(f"[ERROR] Failed to start WebDriver: {type(exc).__name__}: {exc}")
        return

    for index, url in enumerate(apps, start=1):
        print(
            f"[INFO] [{index}/{total}] Visiting {url} at "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC"
        )

        try:
            driver.get(url)

            boot_wait = random.uniform(10, 20)
            print(f"[INFO] Waiting {boot_wait:.1f} seconds for app to boot...")
            time.sleep(boot_wait)

            print(f"[INFO] Current URL: {driver.current_url}")
            print(f"[INFO] Page Title: {driver.title!r}")
            interact_with_page(driver)

        except Exception as exc:
            print(f"[ERROR] Error visiting {url}: {type(exc).__name__}: {exc}")

            try:
                print("[INFO] Attempting to restart driver...")
                driver.quit()
            except Exception:
                pass

            try:
                driver = get_driver()
                print("[INFO] Driver restarted successfully.")
            except Exception as inner_exc:
                print(
                    f"[ERROR] Failed to restart WebDriver: "
                    f"{type(inner_exc).__name__}: {inner_exc}"
                )
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
    # None means "visit all deduplicated important apps"
    wake_up(max_apps_per_run=None)
