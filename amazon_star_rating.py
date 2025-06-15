import time
import random
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scroll_to_bottom(driver, step=600, pause=0.7):
    """Scrolls to the bottom of the page in steps."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    current = 0
    while current < last_height:
        driver.execute_script(f"window.scrollTo(0, {current});")
        time.sleep(pause)
        current += step
        last_height = driver.execute_script("return document.body.scrollHeight")
    # Final scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)

def wait_for_histogram(driver, timeout=10):
    """Waits for the histogram table to be present."""
    for _ in range(timeout * 2):
        rows = driver.find_elements(By.CSS_SELECTOR, "#histogramTable li")
        if rows and len(rows) >= 5:
            return True
        time.sleep(0.5)
    return False

def extract_amazon_star_distribution(driver):
    """
    Extracts the star rating distribution from the Amazon product page.
    Returns a dict: {5: percent, 4: percent, ..., 1: percent}
    """
    star_distribution = {}
    try:
        histogram_rows = driver.find_elements(By.CSS_SELECTOR, "#histogramTable li")
        if not histogram_rows or len(histogram_rows) < 5:
            print("Could not find star distribution rows.")
            return star_distribution

        for row in histogram_rows[:5]:
            try:
                star = None
                percent = None
                try:
                    aria_label = row.find_element(By.CSS_SELECTOR, "a").get_attribute("aria-label")
                    match = re.search(r'(\d+)\s+percent of reviews have (\d) stars?', aria_label)
                    if match:
                        percent = int(match.group(1))
                        star = int(match.group(2))
                except Exception:
                    text = row.text
                    match = re.search(r'(\d)\s*star', text)
                    if match:
                        star = int(match.group(1))
                        percent_match = re.search(r'(\d+)%', text)
                        percent = int(percent_match.group(1)) if percent_match else 0
                    else:
                        continue

                if star is not None:
                    try:
                        percent_elem = row.find_elements(By.CSS_SELECTOR, "span")
                        for elem in percent_elem[::-1]:
                            txt = elem.text.strip()
                            if txt.endswith("%"):
                                percent = int(txt.replace("%", ""))
                                break
                        if percent is None:
                            bar = row.find_element(By.CSS_SELECTOR, "[role='progressbar']")
                            percent = int(bar.get_attribute("aria-valuenow"))
                    except Exception:
                        pass
                    if percent is not None:
                        star_distribution[star] = percent
                        print(f"{star} stars: {percent}%")
            except Exception as e:
                print(f"Error extracting a row: {e}")
    except Exception as e:
        print(f"Error extracting star distribution: {e}")
    return star_distribution

def scrape_amazon_star_distribution(url, max_attempts=2):
    """
    Scrape the star rating distribution from an Amazon product page.
    Scrolls to the end, waits for selectors, refreshes if needed.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    result = {
        "url": url,
        "star_distribution": {},
        "status": "success"
    }

    try:
        for attempt in range(max_attempts):
            print(f"\nAttempt {attempt+1} to extract star distribution...")
            driver.get(url)
            time.sleep(4)
            scroll_to_bottom(driver)
            found = wait_for_histogram(driver, timeout=10)
            if not found:
                print("Histogram not found, refreshing and trying again...")
                driver.refresh()
                time.sleep(4)
                scroll_to_bottom(driver)
                found = wait_for_histogram(driver, timeout=10)
            if found:
                star_distribution = extract_amazon_star_distribution(driver)
                if star_distribution and sum(star_distribution.values()) > 0:
                    result["star_distribution"] = star_distribution
                    break
                else:
                    print("Star distribution not found after scrolling, refreshing page...")
            else:
                print("Histogram still not found after refresh.")
        else:
            result["status"] = "no_data"
    except Exception as e:
        print(f"Error during scraping: {e}")
        result["status"] = "error"
        result["error"] = str(e)
    finally:
        driver.quit()
        print("WebDriver closed.")

    return result

if __name__ == "__main__":
    print("Amazon Star Rating Distribution Scraper")
    print("=" * 40)
    url = input("Enter Amazon product URL: ").strip()
    if not url:
        url = "https://www.amazon.com/dp/B0F8N161W3"
        print(f"Using sample URL: {url}")

    result = scrape_amazon_star_distribution(url)
    print(f"\n{'='*50}")
    print("STAR RATING DISTRIBUTION RESULTS")
    print(f"{'='*50}")

    if result["status"] == "success" and result["star_distribution"]:
        print(f"\nProduct URL: {result['url']}")
        print("\nStar Distribution:")
        for star in sorted(result["star_distribution"].keys(), reverse=True):
            percent = result["star_distribution"][star]
            print(f"  {star} ⭐: {percent}% of reviews")
        # Save to JSON file
        output_file = "amazon_star_distribution.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {output_file}")
    else:
        print(f"Failed to extract star distribution. Status: {result['status']}")
        if "error" in result:
            print(f"Error: {result['error']}")