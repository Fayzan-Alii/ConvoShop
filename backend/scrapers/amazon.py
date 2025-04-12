import re
import pandas as pd
import time
import random
import argparse
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper(product_query=None, max_results=5):
    # Handle input for product query
    if product_query is None:
        product_query = input('Enter Product Name: ')
    
    # Create URL for product search
    product = product_query.replace(" ", "+")
    daraz = f'https://www.daraz.pk/catalog/?q={product}'
    print('URL:', daraz, '\n')
    
    # Handle input for number of products to scrape
    if max_results is None:
        try:
            max_results = int(input('Enter number to take Top Level Averages: '))
        except ValueError:
            max_results = 5
            print(f"Using default value: {max_results}")
    
    # DataFrame to store data with new fields: Items Sold, Store Name, and Rating
    columns = ['Name', 'Original Price', 'Image URL', 'Product URL', 'Items Sold', 'Store Name', 'Rating']
    Web_Data = pd.DataFrame([], columns=columns)

    # Set up WebDriver for Chrome using WebDriver Manager
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # Run in headless mode for production
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(daraz)

    try:
        # Wait for the product blocks to load on the listing page
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Bm3ON")]')))

        def random_scroll(driver, iterations=3):
            """
            Randomly scroll up or down by a random number of pixels (between 100 and 700)
            with random pauses to mimic human behavior.
            """
            print("Scrolling page to load products...")
            for i in range(iterations):
                direction = random.choice([1, -1])
                pixels = random.randint(100, 700) * direction
                driver.execute_script("window.scrollBy(0, arguments[0]);", pixels)
                time.sleep(random.uniform(0.5, 1))

        # Scroll to ensure products load
        random_scroll(driver)

        index = 0
        # Loop over each product block on the listing page
        for product_elem in driver.find_elements(By.XPATH, '//div[contains(@class, "Bm3ON")]'):
            print('.', end='', flush=True)
            
            # Get product name
            try:
                name = product_elem.find_element(By.XPATH, './/a[@title]').get_attribute('title')
            except NoSuchElementException:
                name = 'Unknown'

            # Get product price
            try:
                price = product_elem.find_element(By.CLASS_NAME, 'ooOxS').text
            except NoSuchElementException:
                price = 'Unknown'

            # Get product image URL
            try:
                image_url = product_elem.find_element(By.XPATH, './/img[@type="product"]').get_attribute('src')
            except NoSuchElementException:
                image_url = 'Unknown'
            
            # Extract product URL
            product_url = "Unknown"
            try:
                a_tag = product_elem.find_element(By.XPATH, './/div[contains(@class, "Ms6aG")]//a')
                href = a_tag.get_attribute('href')
                if href:
                    if href.startswith("//"):
                        product_url = "https:" + href
                    else:
                        product_url = href
            except NoSuchElementException:
                product_url = "Unknown"
            
            # Extract the number of items sold
            items_sold = "Unknown"
            try:
                sold_elem = product_elem.find_element(By.XPATH, './/div[contains(@class, "_6uN7R")]//span[contains(@class, "_1cEkb")]/span[1]')
                items_sold = sold_elem.text.strip()
            except NoSuchElementException:
                items_sold = "Unknown"
            
            # Set store name as "Daraz" for all products
            store_name = "Daraz"
            
            # Extract rating by examining the <i> elements inside the rating container
            try:
                rating_container = product_elem.find_element(By.XPATH, './/div[contains(@class, "mdmmT")]')
                rating_icons = rating_container.find_elements(By.TAG_NAME, 'i')
                rating = 0.0
                for icon in rating_icons:
                    classes = icon.get_attribute('class')
                    # Check for full star classes
                    if "Dy1nx" in classes or "K8PID" in classes or "W1iJ5" in classes:
                        rating += 1.0
                    # Check for half star classes
                    elif "fqfC4" in classes or "B4Foa" in classes:
                        rating += 0.5
                    # Check for empty star classes (optional since they add 0)
                    elif "JhD+v" in classes:
                        rating += 0.0
            except NoSuchElementException:
                rating = 'Unknown'
            
            # Save data in DataFrame
            Web_Data.loc[index] = [name, price, image_url, product_url, items_sold, store_name, rating]
            index += 1
            if index >= max_results:
                break

        print('\nWeb Scraping Completed')
    except Exception as e:
        print(f"\nError during scraping: {e}")
    finally:
        driver.quit()

    # Save data to JSON file
    data_dict = Web_Data.to_dict(orient='records')
    with open('daraz_product_data.json', 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, indent=2)
    print(f"Scraped {len(data_dict)} products saved to daraz_product_data.json")
    
    return data_dict

# In the argument parser section:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daraz Product Scraper")
    parser.add_argument("--query", type=str, help="Product search query")
    parser.add_argument("--max_results", type=int, help="Maximum number of results to retrieve")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    args = parser.parse_args()
    
    # If arguments are provided, use them directly
    if args.query:
        result = run_scraper(product_query=args.query, max_results=args.max_results)
        
        # Save to specified output path if provided
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                print(f"Scraped {len(result)} products saved to {args.output}")
    else:
        # Otherwise, fall back to interactive mode
        run_scraper()
