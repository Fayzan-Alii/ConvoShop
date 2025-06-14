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
    
    # Expanded stop words list
    stop_words = [
        "i", "am", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did",
        "have", "has", "had", "will", "would", "shall", "should", "may", "might", "must", "can", "could",
        "my", "your", "his", "her", "its", "our", "their", "me", "him", "us", "them", "you", "he", "she", "it", "we", "they",
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as", "of", "from", "like", "so", "than", "that", "this", "these", "those", "which", "who", "whom", "whose", "where", "when", "how", "what", "why",
        "buy", "purchase", "find", "get", "shop", "shopping", "search", "looking", "want", "need", "show", "recommend", "suggest", "order", "choose", "select", "pick", "see", "view", "compare", "help", "tell", "give", "provide", "offer", "list", "display", "check", "explore", "discover", "browse",
        "please", "thanks", "thank", "ok", "okay", "hi", "hello", "hey", "regards", "dear",
        "some", "any", "few", "many", "more", "most", "all", "each", "every", "either", "neither", "both", "other", "another", "several", "various", "lot", "lots", "plenty", "bit", "bits", "piece", "pieces", "kind", "kinds", "type", "types", "sort", "sorts", "option", "options", "choice", "choices", "range", "ranges", "variety", "varieties", "brand", "brands", "model", "models", "version", "versions", "series",
        "cheap", "cheapest", "expensive", "cost", "costs", "price", "prices", "rate", "rates", "rating", "ratings", "review", "reviews", "deal", "deals", "discount", "discounts", "offer", "offers", "sale", "sales", "promo", "promotion", "promotions", "bargain", "bargains", "value", "worth", "affordable", "budget", "premium", "luxury", "best", "good", "great", "top", "better", "new", "latest", "old", "older", "previous", "current", "recent", "upcoming", "available", "availability", "stock", "instock", "outofstock", "sold", "unsold", "shipping", "delivery", "return", "returns", "refund", "guarantee", "warranty"
    ]
    
    # Expanded multi-word phrases
    multi_word_phrases = [
        "looking for", "show me", "tell me about", "i want", "i need", "can you", "could you", "would you", "how much", "how about", "what about", "where can i", "where to", "let me know", "i would like", "i'd like", "i am looking for", "i'm looking for", "i wish to", "i'd love to", "i hope to", "i am interested in", "i'm interested in", "can i get", "could i get", "would i get", "please show", "please find", "please suggest", "please recommend", "help me find", "help me choose", "help me pick", "help me select", "help me get", "help me buy", "help me purchase", "can you show", "could you show", "would you show", "can you find", "could you find", "would you find", "can you recommend", "could you recommend", "would you recommend", "can you suggest", "could you suggest", "would you suggest", "can you help", "could you help", "would you help"
    ]
    
    for phrase in multi_word_phrases:
        query_lower = query_lower.replace(phrase, " ")
    
    # Expanded product categories
    product_categories = [
        "laptop", "notebook", "ultrabook", "chromebook", "macbook", "surface", "thinkpad", "ideapad", "zenbook", "pavilion", "envy", "spectre", "inspiron", "alienware", "predator", "rog", "vivobook", "swift", "aspire", "legion", "omen", "xps", "elitebook", "probook",
        "phone", "smartphone", "mobile", "cellphone", "android", "iphone", "ipad", "tablet", "phablet", "galaxy", "note", "pixel", "oneplus", "xiaomi", "redmi", "realme", "oppo", "vivo", "nokia", "motorola", "sony", "asus", "lenovo", "huawei", "tecno", "infinix", "blackberry", "htc", "meizu", "nubia", "honor", "google", "samsung", "apple",
        "computer", "desktop", "pc", "imac", "all-in-one", "mini pc", "workstation", "server",
        "camera", "dslr", "mirrorless", "point and shoot", "action camera", "webcam", "camcorder", "gopro", "instax", "polaroid",
        "tv", "television", "oled", "qled", "led", "lcd", "plasma", "monitor", "display", "screen", "projector",
        "headphone", "headset", "earphone", "earbud", "airpods", "buds", "speaker", "soundbar", "woofer", "microphone", "mic",
        "keyboard", "mouse", "trackpad", "stylus", "pen", "printer", "scanner", "router", "modem", "switch", "hub", "adapter", "charger", "battery", "powerbank", "cable", "connector", "memory", "ram", "ssd", "hdd", "hard drive", "flash drive", "usb", "sd card", "graphics card", "gpu", "rtx", "gtx", "rx", "motherboard", "cpu", "processor", "chip", "core", "intel", "amd", "nvidia",
        "watch", "smartwatch", "fitness band", "tracker", "fitbit", "garmin", "amazfit", "mi band", "apple watch", "galaxy watch",
        "refrigerator", "fridge", "microwave", "oven", "stove", "range", "cooktop", "dishwasher", "washing machine", "dryer", "air conditioner", "ac", "heater", "fan", "vacuum", "blender", "mixer", "juicer", "toaster", "grill", "coffee maker", "espresso", "kettle", "water dispenser", "purifier", "geyser", "freezer",
        "sofa", "couch", "bed", "mattress", "table", "desk", "chair", "stool", "bench", "cabinet", "wardrobe", "dresser", "shelf", "bookshelf", "cupboard", "drawer", "nightstand", "side table", "tv stand", "dining table", "coffee table", "recliner", "ottoman",
        "shoes", "sneakers", "boots", "sandals", "heels", "slippers", "shirt", "t-shirt", "tee", "polo", "dress", "skirt", "pants", "trousers", "jeans", "shorts", "jacket", "coat", "blazer", "sweater", "hoodie", "suit", "tie", "belt", "cap", "hat", "scarf", "gloves", "socks", "bag", "backpack", "handbag", "wallet", "watch", "jewelry", "ring", "necklace", "bracelet", "earrings", "sunglasses", "glasses",
        "toy", "game", "console", "ps5", "playstation", "xbox", "switch", "nintendo", "board game", "puzzle", "lego", "drone", "robot", "bike", "bicycle", "scooter", "skateboard", "helmet", "treadmill", "dumbbell", "yoga mat", "tent", "sleeping bag", "camping", "outdoor", "sports", "fitness", "gym", "equipment", "tool", "kit", "set", "bundle", "subscription", "gift", "voucher", "card"
    ]
    
    # Expanded descriptors
    descriptors = [
        "gaming", "wireless", "bluetooth", "smart", "4k", "8k", "ultra", "hd", "full hd", "qhd", "uhd", "hdr", "oled", "qled", "led", "lcd", "curved", "touch", "touchscreen", "portable", "lightweight", "thin", "slim", "compact", "mini", "pro", "plus", "max", "air", "lite", "budget", "premium", "basic", "advanced", "professional", "student", "business", "home", "office", "waterproof", "dustproof", "shockproof", "noise cancelling", "active", "passive", "fast", "quick", "high speed", "high performance", "energy saving", "eco", "eco-friendly", "rechargeable", "solar", "wirefree", "dual", "triple", "quad", "octa", "gen", "series", "edition", "classic", "modern", "vintage", "retro", "limited", "special", "exclusive", "new", "latest", "old", "previous", "recent", "upcoming"
    ]
    
    # Expanded model prefixes
    model_prefixes = [
        "s", "a", "m", "x", "z", "rtx", "gtx", "rx", "hd", "pro", "gen", "series", "model", "version", "type", "mark", "mk", "g", "p", "t", "f", "e", "h", "u", "v", "w", "y", "z", "q", "l", "c", "d", "b", "n", "plus", "max", "mini", "ultra", "edge", "neo", "prime", "core", "note", "flip", "fold", "tab", "pad", "air", "fit", "watch", "band"
    ]
    
    # Check if any product category is mentioned
    found_categories = [cat for cat in product_categories if cat in query_lower]
    
    words = query_lower.split()
    important_words = []
    
    if found_categories:
        for cat in found_categories:
            if cat in words:
                cat_index = words.index(cat)
                for i in range(max(0, cat_index-2), min(len(words), cat_index+5)):
                    if words[i] not in stop_words and len(words[i]) > 2 and words[i] not in important_words:
                        important_words.append(words[i])
            else:
                important_words.append(cat)
        for desc in descriptors:
            if desc in query_lower and desc not in important_words:
                important_words.append(desc)
    else:
        important_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Add any words containing numbers (e.g., "s24", "rtx3080")
    for word in words:
        if any(char.isdigit() for char in word) and word not in important_words:
            important_words.append(word)
    
    # Handle split model numbers (e.g., "s 24", "rtx 4090", "iphone 15")
    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        prefix_match = (current_word in model_prefixes or len(current_word) == 1) and next_word.isdigit()
        product_version_match = (current_word.isalpha() and current_word not in stop_words and next_word.isdigit() and len(next_word) <= 4)
        if prefix_match or product_version_match:
            if current_word not in important_words:
                important_words.append(current_word)
            if next_word not in important_words:
                important_words.append(next_word)
    
    result = " ".join(important_words)
    if not result:
        important_words = [word for word in words if len(word) > 3]
        result = " ".join(important_words)
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