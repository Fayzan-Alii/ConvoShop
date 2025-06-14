import json
import time
import random
import argparse
import os
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def random_scroll(driver, iterations=5):
    """Perform random scrolling on the page to trigger dynamic content loading"""
    print(f"Performing {iterations} random scrolls to load content...")
    
    # Get page height
    page_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(iterations):
        # Random scroll position
        scroll_position = random.randint(300, page_height - 500)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        print(f"Scroll {i+1}: Scrolled to position {scroll_position}")
        time.sleep(random.uniform(0.8, 1.5))
        
        # Every other scroll, go all the way to bottom
        if i % 2 == 0:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom of page")
            time.sleep(1.5)
            
        # And back up a bit
        if i % 3 == 0:
            up_position = max(0, scroll_position - random.randint(200, 600))
            driver.execute_script(f"window.scrollTo(0, {up_position});")
            print(f"Scrolled back up to {up_position}")
            time.sleep(1)

def scrape_amazon_recommendations(product_url, max_results=10):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    recommendations = []
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts and len(recommendations) == 0:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts} - Scraping recommendations from: {product_url}")
        
        try:
            # Load the page (or refresh if not the first attempt)
            if attempt == 1:
                driver.get(product_url)
            else:
                print(f"Refreshing page for attempt {attempt}")
                driver.refresh()
                
            # Initial wait for page load
            time.sleep(5)
            
            # Perform random scrolling to load dynamic content
            random_scroll(driver, iterations=5 + attempt)  # More scrolls on later attempts
            
            # Try to find "Frequently Bought Together" section first
            print("Looking for 'Frequently Bought Together' section...")
            cards = driver.find_elements(By.CSS_SELECTOR, "div.a-cardui._p13n-desktop-sims-fbt_fbt-desktop_new-detail-faceout-box___WyNy")
            print(f"Found {len(cards)} recommendation cards in FBT section")
            
            # Process "Frequently Bought Together" cards
            if cards:
                for card in cards:
                    try:
                        # Skip "This item" card
                        title_container = card.find_elements(By.CSS_SELECTOR, "div._p13n-desktop-sims-fbt_fbt-mobile_title-component-overflow3__3p-Qn")
                        if title_container and "This item:" in title_container[0].text:
                            continue
                            
                        # Title
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, "div[id^='ProductTitle-']")
                            title = title_elem.text.strip().replace("This item: ", "")
                        except Exception:
                            try:
                                # Alternative title selector
                                title_elem = card.find_element(By.CSS_SELECTOR, "div._p13n-desktop-sims-fbt_fbt-mobile_title-component-overflow3__3p-Qn")
                                title = title_elem.text.strip().replace("This item: ", "")
                            except Exception:
                                title = ""
                                
                        # Product link
                        try:
                            link_elem = card.find_element(By.CSS_SELECTOR, "a.a-link-normal, a._p13n-desktop-sims-fbt_fbt-desktop_image-link__17L3C")
                            url = link_elem.get_attribute("href")
                        except Exception:
                            url = ""
                            
                        # Image
                        try:
                            img_elem = card.find_element(By.CSS_SELECTOR, "img.a-dynamic-image")
                            image = img_elem.get_attribute("src")
                        except Exception:
                            image = ""
                            
                        # Price
                        try:
                            price_elem = card.find_element(By.CSS_SELECTOR, "span.a-price > span.a-offscreen")
                            price = price_elem.text.strip()
                            if not price:
                                # Alternative price selector
                                price_elem = card.find_element(By.CSS_SELECTOR, "span.a-price")
                                price = price_elem.text.strip() 
                        except Exception:
                            price = ""
                            
                        if title or url or image:
                            recommendations.append({
                                "title": title,
                                "url": url,
                                "image": image,
                                "price": price,
                                "store": "Amazon"  # Add store name
                            })
                            print(f"Added recommendation: {title[:50]}...")
                            
                        if len(recommendations) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error processing card: {e}")
                        continue
            
            # If no recommendations found yet, try alternative sections
            if len(recommendations) == 0:
                print("No FBT recommendations found. Trying other recommendation sections...")
                
                # Looking for other common recommendation widgets
                alternative_sections = [
                    # "Customers who bought this also bought" section
                    {"selector": "div[data-cel-widget*='desktop-dp-sims_purchase-similarities-sims-feature']", 
                     "item_selector": "li.a-carousel-card", 
                     "name": "Purchase similarities"},
                    
                    # "Products related to this item" section
                    {"selector": "#similarities_feature_div, #SimilarToConsider", 
                     "item_selector": "li.a-carousel-card", 
                     "name": "Similar products"},
                     
                    # "Compare with similar items"
                    {"selector": "#comparison_table_feature_div", 
                     "item_selector": "tr.comparison_table_row_model", 
                     "name": "Comparison table"},
                     
                    # Generic product carousel
                    {"selector": ".a-carousel-container", 
                     "item_selector": ".a-carousel-card", 
                     "name": "Generic carousel"}
                ]
                
                for section in alternative_sections:
                    try:
                        print(f"Looking for {section['name']} section...")
                        containers = driver.find_elements(By.CSS_SELECTOR, section['selector'])
                        
                        for container in containers:
                            items = container.find_elements(By.CSS_SELECTOR, section['item_selector'])
                            print(f"Found {len(items)} items in {section['name']} section")
                            
                            for item in items[:max_results]:
                                product_data = {
                                    "title": "",
                                    "url": "",
                                    "image": "",
                                    "price": "",
                                    "store": "Amazon"
                                }
                                
                                # Title
                                try:
                                    title_elem = item.find_element(By.CSS_SELECTOR, "a[title], .a-size-base, .a-truncate-full")
                                    if title_elem.get_attribute("title"):
                                        product_data["title"] = title_elem.get_attribute("title")
                                    else:
                                        product_data["title"] = title_elem.text.strip()
                                except Exception:
                                    pass
                                    
                                # URL
                                try:
                                    link_elem = item.find_element(By.CSS_SELECTOR, "a[href*='/dp/']")
                                    product_data["url"] = link_elem.get_attribute("href")
                                except Exception:
                                    pass
                                    
                                # Image
                                try:
                                    img_elem = item.find_element(By.CSS_SELECTOR, "img")
                                    product_data["image"] = img_elem.get_attribute("src")
                                except Exception:
                                    pass
                                    
                                # Price
                                try:
                                    price_elem = item.find_element(By.CSS_SELECTOR, "span.a-price, .a-color-price")
                                    product_data["price"] = price_elem.text.strip()
                                except Exception:
                                    pass
                                
                                # Verify we have at least basic product info
                                if product_data["title"] and (product_data["url"] or product_data["image"]):
                                    # Check if this isn't a timestamp/video (common Amazon issue)
                                    if not (len(product_data["title"]) <= 5 and ":" in product_data["title"]):
                                        recommendations.append(product_data)
                                        print(f"Added recommendation: {product_data['title'][:50]}...")
                                        
                                if len(recommendations) >= max_results:
                                    break
                                    
                            if len(recommendations) >= max_results:
                                break
                                
                    except Exception as e:
                        print(f"Error processing {section['name']} section: {e}")
                        
                    if len(recommendations) >= max_results:
                        break
                        
        except Exception as e:
            print(f"Error during attempt {attempt}: {e}")
    
    # Cleanup
    driver.quit()
        
    return recommendations

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Scrape Amazon product recommendations')
        parser.add_argument("--url", required=True, help="Product URL to scrape recommendations from")
        parser.add_argument("--output", required=True, help="Output JSON file path")
        parser.add_argument("--max_results", type=int, default=10, help="Maximum number of recommendations to fetch")
        args = parser.parse_args()
        
        # Simplify URL by removing query params
        product_url = args.url
        if "?" in product_url:
            product_url = product_url.split("?")[0]
        
        # Scrape recommendations
        recommendations = scrape_amazon_recommendations(product_url, args.max_results)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save to file
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(recommendations, f, indent=2)
        
        print(f"Scraped {len(recommendations)} recommendations and saved to {args.output}")
        
    except Exception as e:
        print(f"Critical error in script: {e}")
        traceback.print_exc()
        sys.exit(1)