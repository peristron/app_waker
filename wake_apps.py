import random
import time
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ----------------------------------
# TIER 1: IMPORTANT APPS (ACTIVE)
# ----------------------------------
IMPORTANT_APPS: List[str] = [
    "https://pocragb4datav2.streamlit.app",
    "https://refact0redp0dcaster-2.streamlit.app",
    "https://signalfoundry.streamlit.app",
    "https://signalfoundryv2.streamlit.app",
    "https://multillmchats.streamlit.app",
    "https://pocragb4data.streamlit.app",
    "https://geospatialimpactmonitor.streamlit.app",
    "https://exporterforrolesandpermissions.streamlit.app",
    "https://bulkapirunner.streamlit.app",
    "https://physm0deller.streamlit.app",
    "https://storytellerpoc.streamlit.app",
    "https://physm0d3113r.streamlit.app",
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


STREAMLIT_WAKE_BUTTON_XPATH = (
    "//button["
    "contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
    "'get this app back up')"
    "]"
)

STREAMLIT_SLEEP_TEXT_XPATH = (
    "//*[contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
    "'this app has gone to sleep')]"
)


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

    # On GitHub Actions ubuntu-latest, Chrome/ChromeDriver are usually available.
    # Let Selenium use the runner's installed driver instead of downloading one.
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_page_load_timeout(90)

    width = random.randint(1024, 1600)
    height = random.randint(700, 1000)
    driver.set_window_size(width, height)
    print(f"[INFO] Set window size to {width}x{height}")

    return driver


def click_streamlit_wake_button(driver: webdriver.Chrome, timeout: int = 15) -> bool:
    """Click Streamlit's wake-up button if the app is currently asleep."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, STREAMLIT_SLEEP_TEXT_XPATH))
        )
        print("[INFO] Streamlit sleep screen detected.")
    except TimeoutException:
        return False

    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, STREAMLIT_WAKE_BUTTON_XPATH))
        )
        print("[INFO] Clicking Streamlit wake-up button...")
        button.click()
        return True
    except TimeoutException:
        print("[WARN] Sleep screen found, but wake-up button was not clickable in time.")
        return False
    except WebDriverException as exc:
        print(f"[WARN] Normal wake-button click failed: {exc}")

    try:
        button = driver.find_element(By.XPATH, STREAMLIT_WAKE_BUTTON_XPATH)
        print("[INFO] Trying JavaScript click for Streamlit wake-up button...")
        driver.execute_script("arguments[0].click();", button)
        return True
    except WebDriverException as exc:
        print(f"[WARN] JavaScript wake-button click also failed: {exc}")
        return False


def interact_with_page(driver: webdriver.Chrome) -> None:
    """Perform basic interactions to look more like a real user."""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 3))
    except WebDriverException as exc:
        print(f"[WARN] Interaction failed: {exc}")


def visit_app(driver: webdriver.Chrome, url: str) -> None:
    """Visit one Streamlit app and wake it if Streamlit shows the sleep screen."""
    driver.get(url)

    clicked_wake_button = click_streamlit_wake_button(driver)
    if clicked_wake_button:
        wake_wait = random.uniform(30, 45)
        print(f"[INFO] Waiting {wake_wait:.1f} seconds after wake-up click...")
        time.sleep(wake_wait)
    else:
        boot_wait = random.uniform(10, 20)
        print(f"[INFO] Waiting {boot_wait:.1f} seconds for app to boot...")
        time.sleep(boot_wait)

    print(f"[INFO] Current URL: {driver.current_url}")
    print(f"[INFO] Page Title: {driver.title!r}")
    interact_with_page(driver)


def restart_driver(driver: Optional[webdriver.Chrome]) -> Optional[webdriver.Chrome]:
    """Restart the browser after a failed app visit."""
    if driver is not None:
        try:
            print("[INFO] Attempting to close current driver...")
            driver.quit()
        except Exception:
            pass

    try:
        print("[INFO] Attempting to restart driver...")
        new_driver = get_driver()
        print("[INFO] Driver restarted successfully.")
        return new_driver
    except Exception as exc:
        print(f"[ERROR] Failed to restart WebDriver: {type(exc).__name__}: {exc}")
        return None


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
            visit_app(driver, url)
        except Exception as exc:
            print(f"[ERROR] Error visiting {url}: {type(exc).__name__}: {exc}")
            driver = restart_driver(driver)
            if driver is None:
                break

        pause = random.uniform(3, 10)
        print(f"[INFO] Sleeping {pause:.1f} seconds before next app...")
        time.sleep(pause)

    print("[INFO] Done visiting important apps. Closing browser.")
    try:
        if driver is not None:
            driver.quit()
    except Exception:
        pass


if __name__ == "__main__":
    # None means "visit all deduplicated important apps"
    wake_up(max_apps_per_run=None)
