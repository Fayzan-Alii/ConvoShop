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

def random_scroll(driver, iterations=4):
    """Randomly scroll up or down to help load dynamic content."""
    print("Scrolling page to load elements...")
    for i in range(iterations):
        direction = random.choice([1, -1])
        pixels = random.randint(200, 800) * direction
        driver.execute_script("window.scrollBy(0, arguments[0]);", pixels)
        time.sleep(random.uniform(0.5, 1.2))

def extract_star_distribution(driver):
    """
    Extracts the star rating distribution from the Daraz product page.
    Returns a dict: {5: count, 4: count, ..., 1: count}
    """
    star_distribution = {}
    try:
        # Try to find the rating distribution section
        # This matches your provided HTML structure
        rating_rows = driver.find_elements(By.CSS_SELECTOR, ".detail li")
        if not rating_rows or len(rating_rows) < 5:
            # Try alternative selectors if needed
            rating_rows = driver.find_elements(By.CSS_SELECTOR, ".pdp-review-summary li")
        if not rating_rows or len(rating_rows) < 5:
            print("Could not find star distribution rows.")
            return star_distribution

        for i, row in enumerate(rating_rows[:5]):
            # Star rating: 5 for first row, 4 for second, etc.
            star = 5 - i
            try:
                # Look for the count in a span with class 'percent'
                count_elem = row.find_element(By.CSS_SELECTOR, ".percent")
                count_text = count_elem.text.strip()
            except NoSuchElementException:
                # Fallback: get any number in the row text
                count_text = row.text.strip()
            # Extract the first number found
            match = re.search(r'(\d+)', count_text)
            count = int(match.group(1)) if match else 0
            star_distribution[star] = count
            print(f"{star} stars: {count} reviews")
    except Exception as e:
        print(f"Error extracting star distribution: {e}")
    return star_distribution

def scrape_daraz_star_distribution(url, max_attempts=2):
    """
    Scrape the star rating distribution from a Daraz product page.
    Uses random scrolling and page refresh for robustness.
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
        "total_reviews": 0,
        "average_rating": 0,
        "status": "success"
    }

    try:
        for attempt in range(max_attempts):
            print(f"\nAttempt {attempt+1} to extract star distribution...")
            driver.get(url)
            time.sleep(4)
            random_scroll(driver, iterations=4)
            time.sleep(2)
            star_distribution = extract_star_distribution(driver)
            if star_distribution and sum(star_distribution.values()) > 0:
                result["star_distribution"] = star_distribution
                result["total_reviews"] = sum(star_distribution.values())
                if result["total_reviews"] > 0:
                    weighted_sum = sum(star * count for star, count in star_distribution.items())
                    result["average_rating"] = round(weighted_sum / result["total_reviews"], 2)
                break
            else:
                print("Star distribution not found, refreshing page...")
                driver.refresh()
                time.sleep(4)
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
    print("Daraz Star Rating Distribution Scraper")
    print("=" * 40)
    url = input("Enter Daraz product URL: ").strip()
    if not url:
        url = "https://www.daraz.pk/products/x230-3rd-i5-4-gb-250-gb-i250339359-s1468089759.html?c=&channelLpJumpArgs=&clickTrackInfo=query%253Alaptop%253Bnid%253A250339359%253Bsrc%253ALazadaMainSrp%253Brn%253A4fc46c73470b7ebfcdad75bd8a1d0958%253Bregion%253Apk%253Bsku%253A250339359_PK%253Bprice%253A20999%253Bclient%253Adesktop%253Bsupplier_id%253A6005014515062%253Bbiz_source%253Ahttps%253A%252F%252Fwww.daraz.pk%252F%253Bslot%253A0%253Butlog_bucket_id%253A470687%253Basc_category_id%253A20000411%253Bitem_id%253A250339359%253Bsku_id%253A1468089759%253Bshop_id%253A703343%253BtemplateInfo%253A1103_L%2523-1_A3_C%2523&freeshipping=0&fs_ab=1&fuse_fs=&lang=en&location=Sindh&price=20999&priceCompare=skuId%3A1468089759%3Bsource%3Alazada-search-voucher%3Bsn%3A4fc46c73470b7ebfcdad75bd8a1d0958%3BoriginPrice%3A2099900%3BdisplayPrice%3A2099900%3BsinglePromotionId%3A-1%3BsingleToolCode%3AmockedSalePrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1750010024278&ratingscore=4.5131578947368425&request_id=4fc46c73470b7ebfcdad75bd8a1d0958&review=76&sale=188&search=1&source=search&spm=a2a0e.searchlist.list.0&stock=1"
        print(f"Using sample URL: {url}")

    result = scrape_daraz_star_distribution(url)
    print(f"\n{'='*50}")
    print("STAR RATING DISTRIBUTION RESULTS")
    print(f"{'='*50}")

    if result["status"] == "success" and result["star_distribution"]:
        print(f"\nProduct URL: {result['url']}")
        print(f"Total Reviews: {result['total_reviews']}")
        print(f"Average Rating: {result['average_rating']}/5")
        print("\nStar Distribution:")
        for star in sorted(result["star_distribution"].keys(), reverse=True):
            count = result["star_distribution"][star]
            percentage = (count / result["total_reviews"]) * 100 if result["total_reviews"] > 0 else 0
            print(f"  {star} ⭐: {count:4d} reviews ({percentage:5.1f}%)")
        # Save to JSON file
        output_file = "daraz_star_distribution.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {output_file}")
    else:
        print(f"Failed to extract star distribution. Status: {result['status']}")
        if "error" in result:
            print(f"Error: {result['error']}")