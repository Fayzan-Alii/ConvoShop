import argparse
import os
import asyncio
import json
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    CacheMode
)

# Updated Pydantic model to include URL field
class ProductData(BaseModel):
    name: str
    price: str
    stars: Optional[str]       # e.g., "4.2 out of 5 stars"
    ratings: Optional[str]     # e.g., "568"
    discounted_price: Optional[str]
    image: Optional[str]       # URL to the image
    url: Optional[str]         # URL to the product page
    specifications: Optional[str]

# Updated CSS extraction schema with product URL selector
schema = {
    "name": "Product Block",
    "baseSelector": "div[role='listitem']",
    "fields": [
        {"name": "title", "selector": "h2.a-size-medium", "type": "text"},
        {"name": "price", "selector": "span.a-price-whole", "type": "text"},
        {"name": "stars", "selector": "span.a-icon-alt", "type": "text"},
        {"name": "ratings", "selector": "span.s-review-count", "type": "text"},
        {"name": "discounted_price", "selector": "span.a-price.a-text-price", "type": "text"},
        {"name": "image", "selector": "img.s-image", "type": "attribute", "attribute": "src"},
        {"name": "url", "selector": "a.a-link-normal.s-link-style", "type": "attribute", "attribute": "href"},
        {"name": "specifications", "selector": "div.a-row.a-size-base", "type": "text"}
    ]
}

async def main(query=None, max_results=10, output_path=None):
    import urllib.parse
    encoded_query = urllib.parse.quote(query) if query else "mobile+phone"
    amazon_product_URL = f"https://www.amazon.com/s?k={encoded_query}"
    print(f"Searching Amazon for: {query}")

    load_dotenv()
    session_name = "amazon_product_search"
    browser_config = BrowserConfig(headless=True, viewport_width=1280, viewport_height=720, verbose=True)
    json_strategy = JsonCssExtractionStrategy(schema)

    all_products = []
    pages_to_crawl = min(3, (max_results + 9) // 10)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for page in range(pages_to_crawl):
            if len(all_products) >= max_results:
                break
            
            crawler_config = CrawlerRunConfig(
                extraction_strategy=json_strategy,
                css_selector="div[role='listitem']",
                session_id=session_name,
                cache_mode=CacheMode.BYPASS
            )
            
            result = await crawler.arun(url=amazon_product_URL, config=crawler_config)
            if result.success:
                products = json.loads(result.extracted_content)
                for product in products:
                    if product.get('url') and not product['url'].startswith('http'):
                        product['url'] = f"https://www.amazon.com{product['url']}"
                all_products.extend(products)
            else:
                print("Error:", result.error_message)
    
    all_products = all_products[:max_results]
    print(f"Total products found: {len(all_products)}")
    
    output_path = output_path or 'products_amazon.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2)
    print(f"Scraped data saved to {output_path}")
    
    return all_products

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amazon Product Scraper")
    parser.add_argument("--query", type=str, help="Product search query")
    parser.add_argument("--max_results", type=int, default=10, help="Maximum number of results to retrieve")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    args = parser.parse_args()
    asyncio.run(main(query=args.query, max_results=args.max_results, output_path=args.output))
