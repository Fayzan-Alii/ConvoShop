import json
import time
import random
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

def scroll_to_bottom(driver):
    """Scroll to the very bottom of the page and wait for content to load"""
    print("Scrolling to the very bottom of the page...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Give time for content to load

def random_scroll(driver, iterations=4):
    """
    Randomly scroll the page to trigger lazy loading and mimic human behavior.
    Also scrolls to the very bottom during each attempt.
    """
    print("Scrolling page to load recommendations...")
    for i in range(iterations):
        # Random scroll
        direction = random.choice([1, -1])
        pixels = random.randint(300, 800) * direction
        driver.execute_script("window.scrollBy(0, arguments[0]);", pixels)
        print(f"Random scroll {i+1}: Scrolled {pixels} pixels")
        time.sleep(random.uniform(1.0, 2.0))
        
        # Every iteration, also scroll completely to the bottom
        scroll_to_bottom(driver)

def scrape_daraz_recommendations(product_url, max_results=10):
    """
    Scrape product recommendations from a Daraz product page.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")  # Larger window size
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    recommendations = []
    refresh_attempts = 0
    max_refresh_attempts = 3
    
    print(f"Scraping recommendations from: {product_url}")
    
    while refresh_attempts <= max_refresh_attempts:
        try:
            # Load the page (first time or refresh)
            if refresh_attempts == 0:
                driver.get(product_url)
            else:
                print(f"Refresh attempt {refresh_attempts}/{max_refresh_attempts}")
                driver.refresh()
            
            # Wait longer for initial page load
            time.sleep(6)
            
            # First scroll to bottom of page to load all content
            scroll_to_bottom(driver)
            
            # Scroll back to middle
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # More random scrolling to ensure everything loads
            random_scroll(driver, iterations=6)
            
            # Try multiple possible selectors for recommendations
            possible_selectors = [
                "div.recommend-product-list", 
                "div.mod-recommendation", 
                "div[data-spm='recommendation']",
                "div.pdp-recommend",
                "div[data-module='recommendation']",
                "div.feature-recommendation"
            ]
            
            recommendation_section = None
            section_selector_used = None
            
            for selector in possible_selectors:
                print(f"Trying to find recommendations with selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    print(f"Found recommendation section with selector: {selector}")
                    recommendation_section = elements[0]
                    section_selector_used = selector
                    break
            
            # If we didn't find any recommendation section, try refreshing (if attempts remain)
            if not recommendation_section:
                if refresh_attempts < max_refresh_attempts:
                    refresh_attempts += 1
                    print(f"No recommendation section found. Refreshing page ({refresh_attempts}/{max_refresh_attempts})...")
                    continue
                else:
                    print("Could not find recommendation section after maximum refresh attempts")
                    print("Saving page HTML for debugging...")
                    with open("daraz_debug.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("Page HTML saved to daraz_debug.html")
                    return []
            
            # Found a recommendation section, so proceed with extraction
            # Find products based on which selector worked
            if section_selector_used == "div.recommend-product-list":
                rec_items = recommendation_section.find_elements(By.CSS_SELECTOR, "div.recommend-product-item")
            else:
                # Try different item selectors based on parent
                rec_items = recommendation_section.find_elements(By.CSS_SELECTOR, "a[href*='products']")
                if not rec_items:
                    rec_items = recommendation_section.find_elements(By.CSS_SELECTOR, "div.card-product")
                if not rec_items:
                    rec_items = recommendation_section.find_elements(By.CSS_SELECTOR, "div.item")
            
            print(f"Found {len(rec_items)} recommendation items")
            
            for item in rec_items[:max_results]:
                try:
                    # Extract product info
                    product_data = {}
                    
                    # Title - try multiple selectors
                    try:
                        for title_selector in ["h6.product-title", "div.title", ".product-title", "[data-spm='title']"]:
                            try:
                                title_elem = item.find_element(By.CSS_SELECTOR, title_selector)
                                product_data["title"] = title_elem.text.strip()
                                break
                            except NoSuchElementException:
                                continue
                        
                        # If still no title found, try getting it from alt text of image
                        if "title" not in product_data:
                            img = item.find_element(By.CSS_SELECTOR, "img")
                            product_data["title"] = img.get_attribute("alt")
                    except:
                        product_data["title"] = "Unknown Title"
                    
                    # Price - try multiple selectors
                    try:
                        for price_selector in ["div.product-price", ".price", "[data-spm='price']"]:
                            try:
                                price_elem = item.find_element(By.CSS_SELECTOR, price_selector)
                                price_text = price_elem.text.strip()
                                price_text = price_text.replace("Rs. ", "").strip()
                                product_data["price"] = price_text
                                break
                            except NoSuchElementException:
                                continue
                    except:
                        product_data["price"] = "Unknown"
                    
                    # Image URL
                    try:
                        img_elem = item.find_element(By.CSS_SELECTOR, "img")
                        product_data["image"] = img_elem.get_attribute("src")
                    except:
                        product_data["image"] = "Unknown"
                    
                    # Product URL
                    try:
                        # If item itself is a link
                        if item.tag_name == "a":
                            url = item.get_attribute("href")
                        else:
                            link_elem = item.find_element(By.CSS_SELECTOR, "a")
                            url = link_elem.get_attribute("href")
                        product_data["url"] = url
                    except:
                        product_data["url"] = "Unknown"
                    
                    # Store (always "Daraz" for Daraz products)
                    product_data["store"] = "Daraz"
                    
                    print(f"Added recommendation: {product_data['title'][:50]}...")
                    recommendations.append(product_data)
                    
                except Exception as e:
                    print(f"Error extracting product data: {e}")
                    continue
            
            # If we get here and have recommendations, we're done
            if recommendations:
                break
            else:
                # No recommendations found, refresh and try again
                if refresh_attempts < max_refresh_attempts:
                    refresh_attempts += 1
                    print(f"No recommendations found. Refreshing page ({refresh_attempts}/{max_refresh_attempts})...")
                    continue
        
        except Exception as e:
            print(f"Error during scraping: {e}")
            # Save page source for debugging
            with open("daraz_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Error page HTML saved to daraz_error.html")
            
            # Try again with refresh if attempts remain
            if refresh_attempts < max_refresh_attempts:
                refresh_attempts += 1
                print(f"Error occurred. Refreshing page ({refresh_attempts}/{max_refresh_attempts})...")
                continue
            else:
                break
    
    # Close the driver after all attempts
    driver.quit()
    return recommendations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Daraz product recommendations')
    parser.add_argument("--url", required=True, help="Product URL to scrape recommendations from")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--max_results", type=int, default=10, help="Maximum number of recommendations to fetch")
    args = parser.parse_args()
    
    # Simplify URL by removing query params
    product_url = args.url
    if "?" in product_url:
        product_url = product_url.split("?")[0]
    
    # Scrape recommendations
    recommendations = scrape_daraz_recommendations(product_url, args.max_results)
    
    # Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"Scraped {len(recommendations)} recommendations and saved to {args.output}")