import os
import json
import subprocess
import sys
from pathlib import Path

def test_amazon_scraper(query="smartphone", max_results=3):
    """Test the Amazon scraper directly."""
    current_dir = Path(__file__).parent
    amazon_script = current_dir / "scrapers" / "amazon_crawl4ai.py"
    output_file = current_dir / "data" / "test_amazon.json"
    
    print(f"Testing Amazon scraper with query: {query}")
    
    try:
        subprocess.run([
            sys.executable, 
            str(amazon_script), 
            "--query", query,
            "--max_results", str(max_results),
            "--output", str(output_file)
        ], check=True)
        
        # Load and display results
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                print(f"Found {len(products)} Amazon products")
                for i, p in enumerate(products[:3], 1):
                    print(f"{i}. {p.get('name')} - {p.get('price')}")
                return products
    except Exception as e:
        print(f"Error testing Amazon scraper: {e}")
    
    return []

def test_daraz_scraper(query="smartphone", max_results=3):
    """Test the Daraz scraper directly."""
    current_dir = Path(__file__).parent
    daraz_script = current_dir / "scrapers" / "daraz_webscrapper.py"
    output_file = current_dir / "data" / "test_daraz.json"
    
    print(f"Testing Daraz scraper with query: {query}")
    
    try:
        subprocess.run([
            sys.executable, 
            str(daraz_script), 
            "--query", query,
            "--max_results", str(max_results),
            "--output", str(output_file)
        ], check=True)
        
        # Load and display results
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                print(f"Found {len(products)} Daraz products")
                for i, p in enumerate(products[:3], 1):
                    print(f"{i}. {p.get('Name')} - {p.get('Original Price')}")
                return products
    except Exception as e:
        print(f"Error testing Daraz scraper: {e}")
    
    return []

def test_combined_search(query="smartphone", max_results=6):
    """Test the combined product search functionality."""
    print("\nTesting combined product search...")
    
    # Get individual results
    amazon_products = test_amazon_scraper(query, max_results // 2)
    daraz_products = test_daraz_scraper(query, max_results // 2)
    
    # Format products consistently (same as in scraper_tools.py)
    formatted_products = []
    
    # Format Amazon products
    for p in amazon_products:
        formatted_products.append({
            "name": p.get("name", "Unknown Product"),
            "price": p.get("price", "N/A"),
            "image": p.get("image", "https://via.placeholder.com/150"),
            "store": "Amazon",
            "specifications": p.get("specifications", ""),
            "stars": p.get("stars", "0"),
            "ratings": p.get("ratings", "0")
        })
    
    # Format Daraz products
    for p in daraz_products:
        formatted_products.append({
            "name": p.get("Name", "Unknown Product"),
            "price": p.get("Original Price", "N/A"),
            "image": p.get("Image URL", "https://via.placeholder.com/150"),
            "store": p.get("Store Name", "Daraz"),
            "specifications": "",
            "stars": "N/A",
            "ratings": p.get("Items Sold", "0")
        })
    
    print(f"\nTotal combined products: {len(formatted_products)}")
    return formatted_products

if __name__ == "__main__":
    query = "smartphone" if len(sys.argv) < 2 else sys.argv[1]
    max_results = 6 if len(sys.argv) < 3 else int(sys.argv[2])
    
    print(f"==== Testing scrapers with query: {query}, max_results: {max_results} ====\n")
    
    # Test individual scrapers
    test_amazon_scraper(query, max_results // 2)
    print("\n" + "-" * 50 + "\n")
    test_daraz_scraper(query, max_results // 2)
    print("\n" + "-" * 50 + "\n")
    
    # Test combined search
    combined_results = test_combined_search(query, max_results)
    
    # Save combined results
    output_file = Path(__file__).parent / "data" / "test_combined.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2)
    print(f"Combined results saved to {output_file}")