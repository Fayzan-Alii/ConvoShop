import re
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define star ratings (if applicable)
stars_value = {
    'c3dn4k c1dtTC': 0,
    'c3dn4k c1Zozd': 0.1,
    'c3dn4k cbDGcO': 0.2,
    'c3dn4k c3fsPU': 0.3,
    'c3dn4k c1e2gb': 0.4,
    'c3dn4k c3An30': 0.5,
    'c3dn4k c3DcGB': 0.6,
    'c3dn4k c1wCjy': 0.7,
    'c3dn4k c17YMy': 0.8,
    'c3dn4k cF1vkb': 0.9,
    'c3dn4k c3EEAg': 1
}

# DataFrame to store data
Web_Data = pd.DataFrame([], columns=['Name', 'Original Price', 'Seller Country', 'Image URL'])

# User input
product = input('Enter Product Name: ').replace(" ", "+")
daraz = f'https://www.daraz.pk/catalog/?q={product}'
print('URL:', daraz, '\n')

no_of_product = int(input('Enter number to take Top Level Averages: '))

# Set up WebDriver for Chrome using WebDriver Manager
options = Options()
options.add_argument("--start-maximized")  # Optional: Maximize the browser window

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(daraz)

# Wait for the page to load
wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Bm3ON")]')))

# Scrape product details
index = 0
for product in driver.find_elements(By.XPATH, '//div[contains(@class, "Bm3ON")]'):
    print('*', end='')

    # Get product name
    try:
        name = product.find_element(By.XPATH, './/a[@title]').get_attribute('title')
    except NoSuchElementException:
        name = 'Unknown'

    # Get product price
    try:
        price = product.find_element(By.CLASS_NAME, 'ooOxS').text
    except NoSuchElementException:
        price = 'Unknown'

    # Get seller country
    try:
        country = product.find_element(By.CLASS_NAME, 'oa6ri').get_attribute('title')
    except NoSuchElementException:
        country = 'Unknown'

    # Get product image URL
    try:
        image_url = product.find_element(By.XPATH, './/img[@type="product"]').get_attribute('src')
    except NoSuchElementException:
        image_url = 'Unknown'

    # Store data
    Web_Data.loc[index] = [name, price, country, image_url]
    index += 1
    if index >= no_of_product:  # Stop after collecting required number of products
        break

print('Web Scraping Ended :)')
driver.quit()

# Save data to CSV (optional)
Web_Data.to_csv('daraz_product_data.csv', index=False)