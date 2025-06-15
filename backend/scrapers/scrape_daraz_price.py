import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def get_price_from_url(product_url: str) -> str:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(product_url)
    price = None
    try:
        # Daraz product price is usually in this class
        price_elem = driver.find_element(By.CLASS_NAME, 'pdp-price')
        price = price_elem.text.strip()
    except NoSuchElementException:
        price = "Price not found"
    finally:
        driver.quit()
    return price

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daraz Price Checker")
    parser.add_argument("--url", type=str, required=True, help="Daraz product URL")
    args = parser.parse_args()
    price = get_price_from_url(args.url)
    print(price)