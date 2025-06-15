import argparse
import os
import asyncio
import json
from typing import Optional
from dotenv import load_dotenv
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    CacheMode
)

# Minimal schema for product page
schema = {
    "name": "Product Page",
    "baseSelector": "body",
    "fields": [
        {"name": "price", "selector": "span.a-price-whole", "type": "text"},
    ]
}

async def get_price_from_url(url: str) -> Optional[str]:
    load_dotenv()
    browser_config = BrowserConfig(headless=True, viewport_width=1280, viewport_height=720, verbose=True)
    json_strategy = JsonCssExtractionStrategy(schema)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawler_config = CrawlerRunConfig(
            extraction_strategy=json_strategy,
            css_selector="span.a-price-whole",
            session_id="amazon_price_check",
            cache_mode=CacheMode.BYPASS
        )
        result = await crawler.arun(url=url, config=crawler_config)
        if result.success:
            products = json.loads(result.extracted_content)
            if products and isinstance(products, list):
                price = products[0].get("price")
                return price
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amazon Price Checker")
    parser.add_argument("--url", type=str, required=True, help="Amazon product URL")
    args = parser.parse_args()
    price = asyncio.run(get_price_from_url(args.url))
    if price:
        print(price)
    else:
        print("Price not found")