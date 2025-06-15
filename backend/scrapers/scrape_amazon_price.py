import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scroll_to_bottom(driver, step=600, pause=0.7):
    last_height = driver.execute_script("return document.body.scrollHeight")
    current = 0
    while current < last_height:
        driver.execute_script(f"window.scrollTo(0, {current});")
        time.sleep(pause)
        current += step
        last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)

def wait_for_price(driver, timeout=10):
    for _ in range(timeout * 2):
        price_elem = driver.find_elements(By.CSS_SELECTOR, ".a-price .a-price-whole")
        if price_elem:
            return True
        time.sleep(0.5)
    return False

def extract_amazon_price(driver):
    try:
        price_whole = driver.find_element(By.CSS_SELECTOR, ".a-price .a-price-whole").text.strip()
        price_fraction = driver.find_element(By.CSS_SELECTOR, ".a-price .a-price-fraction").text.strip()
        price_symbol = driver.find_element(By.CSS_SELECTOR, ".a-price-symbol").text.strip()
        return f"{price_symbol}{price_whole}.{price_fraction}"
    except NoSuchElementException:
        return None

def scrape_amazon_price(url, max_attempts=2):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    result = {
        "url": url,
        "price": None,
        "status": "success"
    }

    try:
        for attempt in range(max_attempts):
            driver.get(url)
            time.sleep(4)
            scroll_to_bottom(driver)
            found = wait_for_price(driver, timeout=10)
            if not found:
                driver.refresh()
                time.sleep(4)
                scroll_to_bottom(driver)
                found = wait_for_price(driver, timeout=10)
            if found:
                price = extract_amazon_price(driver)
                if price:
                    result["price"] = price
                    break
        else:
            result["status"] = "no_data"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    finally:
        driver.quit()

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amazon Product Price Scraper")
    parser.add_argument("--url", required=True, help="Amazon product URL to scrape")
    args = parser.parse_args()

    result = scrape_amazon_price(args.url)

    # Output JSON for subprocess use
    print(json.dumps(result))
