import subprocess
import json
import os
import sys
import re
from langchain_core.tools import tool

@tool
def has_shopping_intent(query: str) -> bool:
    """Determine if a query has shopping intent before triggering scrapers."""
    # Convert to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Keywords that indicate product search intent
    shopping_indicators = ["buy", "purchase", "find", "get", "shop", "show me",
                          "shopping", "search", "looking for", "price", "cost",
                          "affordable", "cheap", "expensive", "product", "item",
                          "recommend", "suggestion", "brand", "model", "latest"]
    
    # Common question patterns that are NOT shopping related
    non_shopping_patterns = [
        r"^who are you",
        r"^what is your name",
        r"^how are you",
        r"^what can you do",
        r"^tell me about yourself",
        r"^hello",
        r"^hi\b",
        r"^hey\b",
        r"^help\b",
        r"^introduce yourself",
        r"^what are you",
        r"^who created you",
        r"^what do you know",
        r"^who made you",
    ]
    
    # First check if it matches any non-shopping patterns
    for pattern in non_shopping_patterns:
        if re.search(pattern, query_lower):
            print(f"Query '{query}' matches non-shopping pattern: {pattern}")
            return False
    
    # Check if it has any shopping keywords
    has_intent = any(indicator in query_lower for indicator in shopping_indicators)
    
    # Product categories that often indicate shopping intent even without explicit indicators
    product_categories = [
        "laptop", "phone", "computer", "camera", "tv", "television", "headphone",
        "earphone", "speaker", "monitor", "keyboard", "mouse", "tablet", "watch",
        "shoes", "shirt", "dress", "pants", "jacket", "furniture", "chair", "table",
        "sofa", "bed", "refrigerator", "microwave", "oven", "dishwasher", "vacuum"
    ]
    
    # Check if query contains product categories
    contains_product = any(category in query_lower for category in product_categories)
    
    # Debug output
    if has_intent or contains_product:
        print(f"Query '{query}' has shopping intent: {has_intent or contains_product}")
        if has_intent:
            matched = [ind for ind in shopping_indicators if ind in query_lower]
            print(f"Shopping indicators matched: {matched}")
        if contains_product:
            matched = [cat for cat in product_categories if cat in query_lower]
            print(f"Product categories matched: {matched}")
    else:
        print(f"Query '{query}' has NO shopping intent detected")
    
    return has_intent or contains_product

@tool
def extract_product_keywords(query: str) -> str:
    """Extract product keywords from a user query."""
    query_lower = query.lower().strip()
    
    # Comprehensive list of words to filter out
    stop_words = [
        "i", "am", "is", "are", "the", "a", "an", "and", "or", "but", "in", "on", "at", 
        "to", "for", "with", "by", "about", "as", "of", "from", "like", "so", "me",
        "buy", "purchase", "find", "get", "shop", "shopping", "search", "looking", 
        "want", "need", "show", "what", "can", "could", "would", "should", "may", "might",
        "recommend", "best", "good", "great", "top", "better", "options", "choice", "choices",
        "help", "please", "thanks", "thank", "you", "your", "some", "any", "few", "many"
    ]
    
    # Handle multi-word phrases that should be removed
    multi_word_phrases = ["looking for", "show me", "tell me about", "i want", "i need", 
                          "can you", "could you", "would you", "how much", "how about", 
                          "what about", "where can i", "where to"]
    
    for phrase in multi_word_phrases:
        query_lower = query_lower.replace(phrase, " ")
    
    # Product categories that should be preserved
    product_categories = [
        "laptop", "phone", "computer", "camera", "tv", "television", "headphone",
        "earphone", "speaker", "monitor", "keyboard", "mouse", "tablet", "watch",
        "shoes", "shirt", "dress", "pants", "jacket", "furniture", "chair", "table",
        "sofa", "bed", "refrigerator", "microwave", "washing machine", "oven", "dishwasher",
        "smartphone", "iphone", "samsung", "android", "macbook", "dell", "hp", "lenovo",
        "acer", "asus", "msi", "gaming", "wireless", "bluetooth", "airpods", "battery"
    ]
    
    # Check if any product category is mentioned
    found_categories = [cat for cat in product_categories if cat in query_lower]
    
    # If we found product categories, prioritize them in the result
    if found_categories:
        # Add potential descriptors like "gaming" before product categories
        descriptors = ["gaming", "wireless", "bluetooth", "smart", "4k", "ultra", "hd", 
                      "budget", "premium", "lightweight", "portable", "professional"]
        
        # Extract words around the found categories
        words = query_lower.split()
        important_words = []
        
        for cat in found_categories:
            if cat in words:
                cat_index = words.index(cat)
                # Add words before and after the category if they're meaningful
                for i in range(max(0, cat_index-2), min(len(words), cat_index+2)):
                    if words[i] not in stop_words and len(words[i]) > 2 and words[i] not in important_words:
                        important_words.append(words[i])
            else:
                important_words.append(cat)
        
        # Add any descriptors that appear in the query
        for desc in descriptors:
            if desc in query_lower and desc not in important_words:
                important_words.append(desc)
        
        result = " ".join(important_words)
    else:
        # Just extract meaningful words if no specific product category is found
        words = query_lower.split()
        important_words = [word for word in words if word not in stop_words and len(word) > 2]
        result = " ".join(important_words)
    
    # If no keywords were extracted, use a simple fallback
    if not result:
        words = query_lower.split()
        important_words = [word for word in words if len(word) > 3]  # Just filter by length
        result = " ".join(important_words)
    
    # If still empty, use the original query as last resort
    if not result:
        result = query_lower
    
    print(f"Extracted keywords: '{result}' from query: '{query}'")
    return result

@tool
def search_amazon_products(product_query: str, max_results: int = 5) -> list:
    """Search for products on Amazon based on the query."""
    # Check shopping intent first
    if not has_shopping_intent(product_query):
        print(f"Skipping Amazon search for non-shopping query: '{product_query}'")
        return []
        
    # Handle case when product_query is passed as a dict or JSON string
    if isinstance(product_query, dict):
        if "product_query" in product_query:
            product_query = product_query["product_query"]
    elif isinstance(product_query, str) and product_query.startswith('{'):
        try:
            import json
            query_obj = json.loads(product_query)
            if isinstance(query_obj, dict) and "product_query" in query_obj:
                product_query = query_obj["product_query"]
        except:
            pass  # Keep original query if JSON parsing fails
            
    print(f"Searching Amazon for: {product_query}")
    
    try:
        # Get path to amazon_crawl4ai.py in the scrapers directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        amazon_script = os.path.join(current_dir, "scrapers", "amazon_crawl4ai.py")
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(current_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, "products_amazon.json")
        
        # Run the amazon scraper with the query
        subprocess.run([
            sys.executable, 
            amazon_script, 
            "--query", product_query,
            "--max_results", str(max_results),
            "--output", output_file
        ], check=True)
        
        # Load results from the JSON file
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                
                # Transform products to standard format and include URL
                transformed_products = []
                for p in products:
                    transformed_products.append({
                        "name": p.get("name", "Unknown Product"),
                        "price": p.get("price", "N/A"),
                        "image": p.get("image", "https://via.placeholder.com/150"),
                        "url": p.get("url", ""),  # Include the URL field
                        "store": "Amazon",
                        "specifications": p.get("specifications", ""),
                        "stars": p.get("stars", "0"),
                        "ratings": p.get("ratings", "0")
                    })
                return transformed_products
        
        return []
    except Exception as e:
        print(f"Error running Amazon scraper: {e}")
        return []

@tool
def search_daraz_products(product_query: str, max_results: int = 5) -> list:
    """Search for products on Daraz based on the query."""
    # Check shopping intent first
    if not has_shopping_intent(product_query):
        print(f"Skipping Daraz search for non-shopping query: '{product_query}'")
        return []
        
    print(f"Searching Daraz for: {product_query}")
    
    try:
        # Get path to daraz_webscrapper.py in the scrapers directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        daraz_script = os.path.join(current_dir, "scrapers", "daraz_webscrapper.py")
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(current_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, "daraz_product_data.json")
        
        # Run the daraz scraper with the query
        subprocess.run([
            sys.executable, 
            daraz_script, 
            "--query", product_query,
            "--max_results", str(max_results),
            "--output", output_file
        ], check=True)
        
        # Load results from the JSON file
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                
                # Transform products to standard format and include URL if available
                transformed_products = []
                for p in products:
                    transformed_products.append({
                        "name": p.get("Name", "Unknown Product"),
                        "price": p.get("Original Price", "N/A"),
                        "image": p.get("Image URL", "https://via.placeholder.com/150"),
                        "url": p.get("Product URL", ""),  # Include the URL field if available
                        "store": p.get("Store Name", "Daraz"),
                        "specifications": "",
                        "stars": "N/A",
                        "ratings": p.get("Items Sold", "0")
                    })
                return transformed_products
        
        return []
    except Exception as e:
        print(f"Error running Daraz scraper: {e}")
        return []

@tool
def search_all_products(query: str, max_results: int = 10) -> list:
    """Search for products across multiple platforms."""
    # First check if the query has shopping intent
    if not has_shopping_intent(query):
        print(f"Skipping product search for non-shopping query: '{query}'")
        return []
    
    # Extract keywords if we're getting a conversational query
    if len(query.split()) > 3:
        keywords = extract_product_keywords(query)
        print(f"Extracted keywords: '{keywords}' from query: '{query}'")
    else:
        keywords = query
    
    # Split the max results between platforms
    per_platform = max(1, max_results // 2)
    
    # Get products from both platforms
    amazon_products = search_amazon_products(keywords, per_platform)
    daraz_products = search_daraz_products(keywords, per_platform)
    
    # Format all products in a consistent way
    formatted_products = []
    
    # Format Amazon products (URLs already included from the transformer above)
    formatted_products.extend(amazon_products)
    
    # Format Daraz products (URLs already included from the transformer above)
    formatted_products.extend(daraz_products)
    
    print(f"Total combined products found: {len(formatted_products)}")
    return formatted_products