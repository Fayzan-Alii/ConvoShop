import os
import sys
import json
import subprocess
from bson import ObjectId
from database import get_sqlite_conn, users_collection  # Adjust as needed
from notifications import send_email_notification        # Adjust as needed

def scrape_and_check_prices(user_id):
    print(f"Running scheduled price check for user {user_id}...")
    conn = get_sqlite_conn()
    wishlist = conn.execute("SELECT * FROM wishlist WHERE user_id = ?", (user_id,)).fetchall()

    for item in wishlist:
        product_url = item["product_url"]
        user_id = item["user_id"]
        old_price = float(item["last_checked_price"].replace(",", "").replace("Rs.", "").replace("$", "").strip() or 0)
        store = item["store"]
        product_name = item["product_name"]
        image = item["image"]

        price_str = ""

        try:
            current_dir = os.path.dirname(__file__)
            # Select scraper based on store
            if store.lower() == "daraz":
                script_path = os.path.join(current_dir, "scrapers", "scrape_daraz_price.py")
            else:
                script_path = os.path.join(current_dir, "scrapers", "scrape_amazon_price.py")

            # Run scraper with --url argument
            result = subprocess.run(
                [sys.executable, script_path, "--url", product_url],
                capture_output=True, text=True, check=True
            )

            output = result.stdout.strip()

            # Parse JSON output
            if output:
                try:
                    data = json.loads(output)
                    price_str = data.get("price", "")
                except Exception as e:
                    print(f"Error parsing {store} price output: {e}")
                    continue
            else:
                print(f"No output received from {store} scraper")
                continue

            # Convert to float
            if price_str and "not found" not in price_str.lower():
                try:
                    latest_price = float(price_str.replace(",", "").replace("Rs.", "").replace("$", "").strip())
                except Exception as e:
                    print(f"Could not convert price '{price_str}' to float: {e}")
                    continue
            else:
                print(f"Price not found for {product_url}")
                continue

        except subprocess.CalledProcessError as e:
            print(f"Scraper failed for {store} URL: {product_url}")
            print(f"Error output: {e.stderr}")
            continue
        except Exception as e:
            print(f"Unexpected error while scraping: {e}")
            continue

        # --- Check for price drop ---
        if latest_price < old_price:
            print(f"Price drop detected for: {product_name}")
            conn.execute(
                "INSERT INTO notifications (user_id, product_url, product_name, image, old_price, new_price, store) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, product_url, product_name, image, str(old_price), str(latest_price), store)
            )
            conn.execute(
                "UPDATE wishlist SET last_checked_price = ? WHERE id = ?",
                (str(latest_price), item["id"])
            )
            conn.commit()

            # Notify user
            user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc and "email" in user_doc:
                to_email = user_doc["email"]
                subject = f"Price Drop Alert: {product_name}"
                body = f"""
                <h3>Good news!</h3>
                <p>The price for <b>{product_name}</b> has dropped from <s>{old_price}</s> to <b>{latest_price}</b> at {store}.</p>
                <p><a href="{product_url}">View Product</a></p>
                """
                send_email_notification(to_email, subject, body)

    conn.close()
