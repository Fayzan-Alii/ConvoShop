from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
import socket
import random
import argparse

def random_scroll(driver, iterations=6):
    """
    Randomly scroll up or down by a random number of pixels (between 100 and 700)
    with random pauses to mimic human behavior.
    """
    print("Starting random scrolling...")
    for i in range(iterations):
        direction = random.choice([1, -1])
        pixels = random.randint(100, 700) * direction
        driver.execute_script("window.scrollBy(0, arguments[0]);", pixels)
        print(f"Random scroll {i+1}: Scrolled {pixels} pixels")
        time.sleep(random.uniform(0.5, 2))
    print("Random scrolling finished.")

def extract_reviews(driver, review_selector):
    """
    Extracts review text using the provided CSS selector.
    """
    reviews = []
    review_elements = driver.find_elements(By.CSS_SELECTOR, review_selector)
    if review_elements:
        print(f"Found {len(review_elements)} review elements using selector: '{review_selector}'")
        for element in review_elements:
            try:
                review_text = element.text.strip()
                if review_text and len(review_text) > 10 and review_text not in reviews:
                    reviews.append(review_text)
                    print(f"Added review ({len(review_text)} chars): '{review_text[:50]}...'")
            except Exception as e:
                print(f"Error extracting text: {e}")
    else:
        print("No review elements found on current page.")
    return reviews

def scrape_daraz_reviews_with_selenium(url, max_pages=1):
    """
    Scrape reviews from a Daraz product page using Selenium.
    Extracts review text using the selector:
    'div.mod-reviews div.item-content div.content'
    For the first page, if no reviews are found, the page is refreshed and random scrolling is repeated.
    Pagination is handled without refresh for subsequent pages.
    
    Args:
        url (str): URL of the Daraz product page.
        max_pages (int): Maximum number of review pages to scrape.
        
    Returns:
        list: List of review texts.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")  # Uncomment for headless mode if needed
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36")
    
    socket.setdefaulttimeout(180)
    driver_path = "./chromedriver.exe"  # Update if necessary
    
    all_reviews = []
    driver = None
    review_selector = 'div.mod-reviews div.item-content div.content'
    
    try:
        if os.path.exists(driver_path):
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"Using ChromeDriver from: {driver_path}")
        else:
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Using ChromeDriver from system PATH")
        
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        
        print(f"Navigating to: {url}")
        try:
            driver.get(url)
            print(f"Page title: {driver.title}")
        except TimeoutException:
            print("Page load timed out, but continuing...")
        except WebDriverException as e:
            print(f"WebDriver error during page load: {e}")
            if "net::ERR_CONNECTION_CLOSED" in str(e):
                print("Connection was closed. The site might be blocking automated access.")
                return all_reviews
        
        # For the first page, perform random scrolling and refresh if needed.
        print("Processing page 1:")
        random_scroll(driver, iterations=6)
        print("Waiting a few seconds after random scrolling...")
        time.sleep(5)
        
        page_reviews = extract_reviews(driver, review_selector)
        # If no reviews found on first page, refresh and try again.
        if not page_reviews:
            print("No reviews found on page 1. Refreshing page and trying again...")
            driver.refresh()
            time.sleep(5)
            random_scroll(driver, iterations=6)
            print("Waiting after refresh scrolling...")
            time.sleep(5)
            page_reviews = extract_reviews(driver, review_selector)
        
        all_reviews.extend(page_reviews)
        current_page = 1
        
        # Pagination for subsequent pages without refresh
        while current_page < max_pages:
            try:
                # Wait for and click the next page button
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "i.next-icon.next-icon-arrow-right.next-icon-medium.next-icon-last"))
                )
                print("Next page button found. Clicking it...")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)  # Wait for page load
                
                # Perform random scrolling on new page to trigger lazy loading
                random_scroll(driver, iterations=6)
                print("Waiting a few seconds after scrolling on new page...")
                time.sleep(5)
                
                page_reviews = extract_reviews(driver, review_selector)
                if not page_reviews:
                    print("No reviews found on this page. Ending pagination.")
                    break
                for review in page_reviews:
                    if review not in all_reviews:
                        all_reviews.append(review)
                current_page += 1
                print(f"Completed scraping page {current_page}")
            except TimeoutException:
                print("No next page button found. Ending pagination.")
                break
        
        return all_reviews
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return all_reviews
        
    finally:
        if driver:
            try:
                driver.quit()
                print("WebDriver successfully closed")
            except Exception as e:
                print(f"Error closing WebDriver: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daraz Review Scraper")
    parser.add_argument("--url", type=str, help="Product URL to scrape")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--mode", type=str, help="Mode (api or interactive)")
    args = parser.parse_args()
    
    # If running in API mode with URL provided
    if args.mode == "api" and args.url:
        print(f"Running in API mode for URL: {args.url}")
        output_file = args.output or "daraz_reviews2.txt"
        max_pages = 2  # Default for API mode
        
        reviews = scrape_daraz_reviews_with_selenium(args.url, max_pages)
        
        if reviews:
            with open(output_file, "w", encoding="utf-8") as f:
                for i, review in enumerate(reviews, 1):
                    f.write(f"Review #{i}:\n{review}\n{'=' * 40}\n")
            print(f"Reviews saved to '{output_file}'")
        else:
            print("No reviews found for this product.")
    else:
        print("Daraz Review Scraper")
        print("--------------------")
        print("1. Enter a custom URL")
        print("2. Use a sample URL with known reviews")
        choice = input("Enter your choice (1/2): ")
        
        if choice == "2":
            sample_urls = [
                "https://www.daraz.pk/products/hp-probook-cpu-i5-4th-generation-ram-8gb-hdd-500gb-refurbished-laptop-i120958095-s1267834271.html",
                "https://www.daraz.pk/products/dell-latitude-e5470-6th-generation-core-i5-i326396118-s1648483564.html",
                "https://www.daraz.pk/products/hp-elitebook-840-g3-6th-generation-core-i5-6300u-8gb-ram-256gb-ssd-1366x768-hd-display-fingerprint-reader-backlit-key-i338019869-s1704219607.html"
            ]
            print("\nSample URLs with reviews:")
            for i, url in enumerate(sample_urls, 1):
                print(f"{i}. {url}")
            url_choice = input("Enter URL number (1-3): ")
            try:
                url_index = int(url_choice) - 1
                if 0 <= url_index < len(sample_urls):
                    url = sample_urls[url_index]
                else:
                    url = sample_urls[0]
            except ValueError:
                url = sample_urls[0]
            print(f"\nUsing sample URL: {url}")
        else:
            url = input("\nEnter the Daraz product URL: ")
            if not url:
                url = "https://www.daraz.pk/products/4gb-4gb-16gb32gb-ssd-hdmi-wifi-os-n3060-i405246469-s2713419042.html"
        
        max_pages = input("Enter maximum number of review pages to scrape (default: 1): ")
        try:
            max_pages = int(max_pages)
        except (ValueError, TypeError):
            max_pages = 1
        
        print(f"\nStarting scraper for URL: {url}")
        print(f"Maximum pages to scrape: {max_pages}")
        
        reviews = scrape_daraz_reviews_with_selenium(url, max_pages)
        
        print(f"\nFound {len(reviews)} reviews:")
        for i, review in enumerate(reviews, 1):
            print(f"\nReview #{i}:")
            print(review)
            print("-" * 80)
        
        if reviews:
            output_file = "daraz_reviews2.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                for i, review in enumerate(reviews, 1):
                    f.write(f"Review #{i}:\n{review}\n{'=' * 40}\n")
                print(f"\nReviews saved to '{output_file}'")
        else:
            print("\nNo reviews found for this product.")

