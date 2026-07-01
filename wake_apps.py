import random
import time
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
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

STREAMLIT_APP_SELECTORS = [
    "[data-testid='stAppViewContainer']",
    "[data-testid='stApp']",
    ".stApp",
]

GENERIC_TITLES = {"streamlit", "streamlit app"}


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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    ua = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={ua}")
    print(f"[INFO] Using User-Agent: {ua}")

    # On GitHub Actions ubuntu-latest, Chrome/ChromeDriver are usually available.
    # Let Selenium use the runner's installed driver instead of downloading one.
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_page_load_timeout(120)
    driver.set_script_timeout(60)

    width = random.randint(1280, 1680)
    height = random.randint(800, 1050)
    driver.set_window_size(width, height)
    print(f"[INFO] Set window size to {width}x{height}")

    return driver


def wait_for_document_ready(driver: webdriver.Chrome, timeout: int = 45) -> bool:
    """Wait until the browser reports that the document has loaded."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda active_driver: active_driver.execute_script("return document.readyState")
            == "complete"
        )
        return True
    except TimeoutException:
        print("[WARN] Document did not reach readyState=complete in time.")
        return False


def click_streamlit_wake_button(driver: webdriver.Chrome, timeout: int = 20) -> bool:
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


def wait_for_streamlit_app_shell(driver: webdriver.Chrome, timeout: int = 90) -> bool:
    """Wait for Streamlit's app container to appear."""
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        for selector in STREAMLIT_APP_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"[INFO] Streamlit app shell detected with selector: {selector}")
                    return True
            except WebDriverException:
                pass
        time.sleep(2)

    print("[WARN] Streamlit app shell was not detected before timeout.")
    return False


def page_looks_generic(driver: webdriver.Chrome) -> bool:
    """Return True when the page still looks like a generic Streamlit shell."""
    title = (driver.title or "").strip().lower()
    return title in GENERIC_TITLES


def get_body_preview(driver: webdriver.Chrome, limit: int = 500) -> str:
    """Return a short body-text preview for debugging GitHub Actions logs."""
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
    except WebDriverException:
        return ""

    body_text = " ".join(body_text.split())
    return body_text[:limit]


def interact_with_page(driver: webdriver.Chrome) -> None:
    """Perform basic interactions to help Streamlit register an active browser session."""
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element(body).click().perform()
        time.sleep(random.uniform(1, 2))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        driver.execute_script("window.scrollTo(0, Math.floor(document.body.scrollHeight / 2));")
        time.sleep(random.uniform(2, 4))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(2, 4))
    except WebDriverException as exc:
        print(f"[WARN] Interaction failed: {exc}")


def keep_session_active(driver: webdriver.Chrome, dwell_seconds: float) -> None:
    """Keep the tab open and active long enough for Streamlit to count the visit."""
    print(f"[INFO] Keeping app tab active for {dwell_seconds:.1f} seconds...")
    end_time = time.monotonic() + dwell_seconds
    interaction_count = 0

    while time.monotonic() < end_time:
        interaction_count += 1
        try:
            driver.execute_script(
                "window.scrollTo(0, (window.scrollY + 240) % "
                "Math.max(document.body.scrollHeight, 1));"
            )
            driver.execute_script("document.body.dispatchEvent(new Event('mousemove')); ")
        except WebDriverException as exc:
            print(f"[WARN] Active-session interaction failed: {exc}")
            return

        sleep_for = random.uniform(8, 14)
        remaining = end_time - time.monotonic()
        time.sleep(max(0, min(sleep_for, remaining)))

    print(f"[INFO] Completed {interaction_count} active-session interaction(s).")


def log_page_state(driver: webdriver.Chrome) -> None:
    """Log enough state to compare apps that wake successfully versus those that do not."""
    print(f"[INFO] Current URL: {driver.current_url}")
    print(f"[INFO] Page Title: {driver.title!r}")

    if page_looks_generic(driver):
        preview = get_body_preview(driver)
        print("[WARN] Page title is still generic after waiting.")
        print(f"[INFO] Body preview: {preview!r}")


def visit_app(driver: webdriver.Chrome, url: str) -> None:
    """Visit one Streamlit app and give it enough time to initialize fully."""
    driver.get(url)
    wait_for_document_ready(driver)

    clicked_wake_button = click_streamlit_wake_button(driver)
    if clicked_wake_button:
        wake_wait = random.uniform(45, 70)
        print(f"[INFO] Waiting {wake_wait:.1f} seconds after wake-up click...")
        time.sleep(wake_wait)
        wait_for_document_ready(driver)
    else:
        boot_wait = random.uniform(20, 35)
        print(f"[INFO] Waiting {boot_wait:.1f} seconds for app to boot...")
        time.sleep(boot_wait)

    app_shell_found = wait_for_streamlit_app_shell(driver)
    interact_with_page(driver)

    if page_looks_generic(driver) and app_shell_found:
        refresh_wait = random.uniform(20, 35)
        print("[INFO] App shell loaded but title is generic; refreshing once to deepen session...")
        driver.refresh()
        wait_for_document_ready(driver)
        time.sleep(refresh_wait)
        wait_for_streamlit_app_shell(driver, timeout=60)
        interact_with_page(driver)

    dwell_seconds = random.uniform(50, 80)
    keep_session_active(driver, dwell_seconds)
    log_page_state(driver)


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
    start_delay = random.uniform(5, 60)
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

        pause = random.uniform(5, 12)
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
