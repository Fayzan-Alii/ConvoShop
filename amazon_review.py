import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dotenv import load_dotenv
import argparse
# Load environment variables from .env file
load_dotenv()

# Get Amazon credentials from environment variables
AMAZON_EMAIL = os.getenv("AMAZON_EMAIL")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")

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

def amazon_login(driver, email, password):
    """
    Automates Amazon login if the sign-in page appears.
    After signing in, if a prompt asking for phone verification appears,
    the function clicks the "Not now" link.
    """
    try:
        # Wait for the email input to be present.
        email_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.clear()
        email_field.send_keys(email)
        print("Email entered.")

        # Click the 'Continue' button.
        continue_button = driver.find_element(By.CSS_SELECTOR, "span#continue input#continue, span#continue")
        continue_button.click()
        print("Clicked Continue button.")

        # Wait for the password field and enter password.
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.clear()
        password_field.send_keys(password)
        print("Password entered.")

        # Click the 'Sign in' button.
        sign_in_button = driver.find_element(By.ID, "signInSubmit")
        sign_in_button.click()
        print("Clicked Sign in button.")

        # Wait a bit for any post-login prompts to appear.
        time.sleep(3)

        # If a "Not now" prompt appears (for example, phone verification), click it.
        try:
            not_now_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#ap-account-fixup-phone-skip-link"))
            )
            not_now_link.click()
            print("Clicked 'Not now' link for phone verification.")
        except TimeoutException:
            print("No 'Not now' prompt found; proceeding.")
        
        # Allow time for the login process to complete.
        time.sleep(5)
    except Exception as e:
        print("Login prompt not detected or error during login:", e)

def extract_amazon_review_details(driver, container_selector, title_selector, rating_selector, date_selector, review_text_selector):
    """
    Extracts review details from each review container.
    """
    reviews = []
    containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
    if containers:
        print(f"Found {len(containers)} review containers using selector: '{container_selector}'")
        for container in containers:
            try:
                try:
                    title = container.find_element(By.CSS_SELECTOR, title_selector).text.strip()
                except Exception as e:
                    title = ""
                    print(f"Title not found: {e}")
                try:
                    rating = container.find_element(By.CSS_SELECTOR, rating_selector).text.strip()
                except Exception as e:
                    rating = ""
                    print(f"Rating not found: {e}")
                try:
                    review_date = container.find_element(By.CSS_SELECTOR, date_selector).text.strip()
                except Exception as e:
                    review_date = ""
                    print(f"Review date not found: {e}")
                try:
                    review_text = container.find_element(By.CSS_SELECTOR, review_text_selector).text.strip()
                except Exception as e:
                    review_text = ""
                    print(f"Review text not found: {e}")
                if review_text and len(review_text) > 10:
                    review = {
                        "title": title,
                        "rating": rating,
                        "date": review_date,
                        "review_text": review_text
                    }
                    reviews.append(review)
                    print(f"Added review: '{title[:50]}...'")
            except Exception as e:
                print(f"Error processing review container: {e}")
    else:
        print("No review containers found on current page.")
    return reviews

def scrape_amazon_reviews_with_selenium(url, max_pages=1):
    """
    Scrapes Amazon reviews. It navigates to the "See more reviews" page,
    logs in using environment variables if needed, and then paginates through reviews.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")  # Uncomment for headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36")
    
    driver_path = "./chromedriver.exe"  # Update this path if needed
    all_reviews = []
    driver = None

    container_selector = "span.a-list-item"
    title_selector = "a[data-hook='review-title'] span"
    rating_selector = "i[data-hook='review-star-rating'] span"
    date_selector = "span[data-hook='review-date']"
    review_text_selector = "span[data-hook='review-body']"
    see_all_reviews_selector = "a[data-hook='see-all-reviews-link-foot']"

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
            return all_reviews

        # Check for "See more reviews" link.
        try:
            see_all_reviews = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, see_all_reviews_selector))
            )
            if see_all_reviews:
                reviews_href = see_all_reviews.get_attribute("href")
                if reviews_href.startswith("/"):
                    reviews_href = "https://www.amazon.com" + reviews_href
                print("Navigating to the 'See more reviews' page:", reviews_href)
                driver.get(reviews_href)
                time.sleep(5)
        except TimeoutException:
            print("No 'See more reviews' link found; proceeding with current page.")

        # If login is needed, automatically log in.
        if AMAZON_EMAIL and AMAZON_PASSWORD:
            try:
                driver.find_element(By.ID, "ap_email")
                print("Login form detected; initiating login sequence.")
                amazon_login(driver, AMAZON_EMAIL, AMAZON_PASSWORD)
            except Exception:
                print("No login form detected; continuing without login.")

        print("Processing page 1:")
        random_scroll(driver, iterations=6)
        time.sleep(5)
        page_reviews = extract_amazon_review_details(driver, container_selector, title_selector, rating_selector, date_selector, review_text_selector)
        if not page_reviews:
            print("No reviews found on page 1. Refreshing page and trying again...")
            driver.refresh()
            time.sleep(5)
            random_scroll(driver, iterations=6)
            time.sleep(5)
            page_reviews = extract_amazon_review_details(driver, container_selector, title_selector, rating_selector, date_selector, review_text_selector)
        all_reviews.extend(page_reviews)
        current_page = 1

        next_button_selector = "li.a-last a"
        while current_page < max_pages:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
                )
                print("Next page button found. Clicking it...")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
                random_scroll(driver, iterations=6)
                time.sleep(5)
                page_reviews = extract_amazon_review_details(driver, container_selector, title_selector, rating_selector, date_selector, review_text_selector)
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
    parser = argparse.ArgumentParser(description="Amazon Review Scraper")
    parser.add_argument("--url", type=str, help="Product URL to scrape")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--mode", type=str, help="Mode (api or interactive)")
    args = parser.parse_args()
    
    # If running in API mode with URL provided
    if args.mode == "api" and args.url:
        print(f"Running in API mode for URL: {args.url}")
        output_file = args.output or "amazon_reviews.txt"
        max_pages = 2  # Default for API mode
        
        reviews = scrape_amazon_reviews_with_selenium(args.url, max_pages)
        
        if reviews:
            with open(output_file, "w", encoding="utf-8") as f:
                for i, review in enumerate(reviews, 1):
                    f.write(f"Review #{i}:\n")
                    f.write(review.get("review_text", "") + "\n")
                    f.write("=" * 40 + "\n")
            print(f"Reviews saved to '{output_file}'")
        else:
            print("No reviews found for this product.")
    else:
        print("Amazon Review Scraper")
        print("---------------------")
        print("1. Enter a custom URL")
        print("2. Use a sample URL with known reviews")
        choice = input("Enter your choice (1/2): ")
        
        if choice == "2":
            sample_urls = [
                "https://www.amazon.com/product-reviews/B0DP3GDTCF",
                "https://www.amazon.com/product-reviews/B08N5WRWNW"
            ]
            print("\nSample URLs with reviews:")
            for i, url in enumerate(sample_urls, 1):
                print(f"{i}. {url}")
            url_choice = input("Enter URL number (1/2): ")
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
            url = input("\nEnter the Amazon product reviews URL: ")
            if not url:
                url = "https://www.amazon.com/product-reviews/B0DP3GDTCF"
        
        max_pages = input("Enter maximum number of review pages to scrape (default: 1): ")
        try:
            max_pages = int(max_pages)
        except (ValueError, TypeError):
            max_pages = 1

        print(f"\nStarting scraper for URL: {url}")
        print(f"Maximum pages to scrape: {max_pages}")
        
        reviews = scrape_amazon_reviews_with_selenium(url, max_pages)
        
        print(f"\nFound {len(reviews)} reviews:")
        for i, review in enumerate(reviews, 1):
            print(f"Review #{i}:")
            print(review.get("review_text", ""))
            print("-" * 80)

        if reviews:
            output_file = "amazon_reviews.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                for i, review in enumerate(reviews, 1):
                    f.write(f"Review #{i}:\n")
                    f.write(review.get("review_text", "") + "\n")
                    f.write("=" * 40 + "\n")
            print(f"\nReviews saved to '{output_file}'")
        else:
            print("\nNo reviews found for this product.")
