import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from langserve import add_routes
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
# MongoDB connection
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import jwt as pyjwt
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

import operator
import re
import json
import subprocess
import os
import sys
from pathlib import Path
from fastapi import BackgroundTasks
from pydantic import BaseModel


# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")
client = MongoClient(MONGO_URI)
db = client["ConvoShop"]  # Database name
users_collection = db["users"]  # Collection name
chats_collection = db["chats"]  # Chats collection #-----------------------
    
app = FastAPI(
    title="ConvoShop AI Server",
    version="1.0",
    description="A shopping assistant with real-time product search capabilities",
)

app = FastAPI(
    title="ConvoShop AI Server",
    version="1.0",
    description="A shopping assistant with real-time product search capabilities",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#------------------------------------------------------------------------S
# Models for MongoDB authentication
class User(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str

#------------------------------------------------------------------------


# Math tools - implement these properly
@tool
def evaluate_float_expression(expr: str) -> float:
    """Evaluates a mathematical expression that has fractional parts or decimals given as a string."""
    try:
        allowed_names = {"abs": abs, "pow": pow, "round": round}
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"The use of '{name}' is not allowed")
        return float(eval(expr, {"__builtins__": {}}, allowed_names))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

@tool
def evaluate_integer_expression(expr: str) -> int:
    """Evaluates a mathematical expression given as a string."""
    try:
        allowed_names = {"abs": abs, "pow": pow, "round": round}
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"The use of '{name}' is not allowed")
        return int(eval(expr, {"__builtins__": {}}, allowed_names))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def direct_search_amazon_products(query: str, max_results: int = 5) -> list:
    """Search for products on Amazon based on the query without using LangChain tool."""
    print(f"Direct Amazon search for: {query}")
    if not query or not isinstance(query, str):
        print("Invalid query for Amazon search")
        return []
    
    # Always extract keywords for all queries
    from scraper_tools import extract_product_keywords
    keywords = extract_product_keywords(query)
    if keywords and keywords != query:
        print(f"Using extracted keywords for Amazon search: '{keywords}'")
        query = keywords
    
    try:
        current_dir = Path(__file__).parent
        amazon_script = current_dir / "scrapers" / "amazon_crawl4ai.py"
        data_dir = current_dir / "data"
        os.makedirs(data_dir, exist_ok=True)
        output_file = data_dir / "products_amazon.json"
        subprocess.run([
            sys.executable, 
            str(amazon_script), 
            "--query", query,
            "--max_results", str(max_results),
            "--output", str(output_file)
        ], check=True)
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                for p in products:
                    if 'url' not in p or not p['url']:
                        p['url'] = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
                return products
        return []
    except Exception as e:
        print(f"Error running Amazon scraper: {e}")
        return []

def direct_search_daraz_products(query: str, max_results: int = 5) -> list:
    """Search for products on Daraz based on the query without using LangChain tool."""
    print(f"Direct Daraz search for: {query}")
    if not query or not isinstance(query, str):
        print("Invalid query for Daraz search")
        return []
    
    # Always extract keywords for all queries
    from scraper_tools import extract_product_keywords
    keywords = extract_product_keywords(query)
    if keywords and keywords != query:
        print(f"Using extracted keywords for Daraz search: '{keywords}'")
        query = keywords
        
    try:
        current_dir = Path(__file__).parent
        daraz_script = current_dir / "scrapers" / "daraz_webscrapper.py"
        data_dir = current_dir / "data"
        os.makedirs(data_dir, exist_ok=True)
        output_file = data_dir / "daraz_product_data.json"
        subprocess.run([
            sys.executable, 
            str(daraz_script), 
            "--query", query,
            "--max_results", str(max_results),
            "--output", str(output_file)
        ], check=True)
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                for p in products:
                    if 'Product URL' not in p or not p['Product URL']:
                        p['Product URL'] = f"https://www.daraz.pk/catalog/?q={query.replace(' ', '+')}"
                return products
        return []
    except Exception as e:
        print(f"Error running Daraz scraper: {e}")
        return []

def direct_search_all_products(query: str, max_results: int = 10) -> list:
    """Search for products across multiple platforms without using LangChain tool."""
    print(f"Direct combined search for: {query}")
    if not query or not isinstance(query, str):
        print("Invalid query for product search")
        return []
    
    # Extract keywords from the query before searching
    from scraper_tools import extract_product_keywords
    keywords = extract_product_keywords(query)
    
    # If no keywords were extracted, use a fallback approach
    if not keywords or keywords.strip() == "":
        print("No keywords extracted, using fallback method")
        common_stop_words = ["i", "am", "looking", "to", "for", "buy", "purchase", 
                            "some", "good", "best", "want", "need", "get", "me", "show"]
        words = query.lower().split()
        keywords = " ".join([w for w in words if w not in common_stop_words and len(w) > 2])
        if not keywords:
            keywords = query  # Fall back to original query if all words filtered out
    
    print(f"Searching with keywords: '{keywords}'")
    
    # Split the max results between platforms
    per_platform = max(1, max_results // 2)
    
    # Get products from both platforms using the extracted keywords
    amazon_products = direct_search_amazon_products(keywords, per_platform)
    daraz_products = direct_search_daraz_products(keywords, per_platform)
    
    # Format all products in a consistent way
    formatted_products = []
    
    # Format Amazon products
    for p in amazon_products:
        # Extract numeric stars value from text like "4.4 out of 5 stars"
        stars_value = "0"
        if p.get("stars"):
            stars_match = re.search(r"(\d+\.?\d*)", p.get("stars", "0"))
            if stars_match:
                stars_value = stars_match.group(1)
        
        formatted_products.append({
            "name": p.get("title", "Unknown Product"),  # Map 'title' to 'name'
            "price": p.get("price", "N/A"),
            "image": p.get("image", "https://via.placeholder.com/150"),
            "url": p.get("url", f"https://www.amazon.com/s?k={keywords.replace(' ', '+')}"),
            "store": "Amazon",
            "specifications": p.get("specifications", ""),
            "stars": stars_value,  # Extract numeric value
            "ratings": p.get("ratings", "0")
        })
    
    # Format Daraz products
    for p in daraz_products:
        # Make sure stars are formatted properly
        stars_value = p.get("Stars", "0")
        if isinstance(stars_value, (int, float)):
            stars_value = str(stars_value)
        
        formatted_products.append({
            "name": p.get("Name", "Unknown Product"),
            "price": p.get("Original Price", "N/A"),
            "image": p.get("Image URL", "https://via.placeholder.com/150"),
            "url": p.get("Product URL", f"https://www.daraz.pk/catalog/?q={keywords.replace(' ', '+')}"),
            "store": "Daraz",
            "specifications": "",
            "stars": stars_value,  # Convert to string if numeric
            "ratings": p.get("Items Sold", "0")
        })
    
    print(f"Returning {len(formatted_products)} formatted products")
    if formatted_products:
        print(f"Sample product: {formatted_products[0]}")
    return formatted_products

# Import scraper tools from your scraper_tools file (if available)
from scraper_tools import search_all_products, search_amazon_products, search_daraz_products

all_tools = [
    evaluate_float_expression, 
    evaluate_integer_expression,
    search_all_products, 
    search_amazon_products, 
    search_daraz_products
]

# --- System Prompt Template ---
system_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are ConvoShop, an AI shopping assistant powered by real-time web scraping.

When a user expresses interest in buying products:
1. Use the search_all_products tool to find current options from Amazon and Daraz.
2. Present the results in a helpful, conversational way.
3. Mention key product details like price, ratings, and specifications.
4. Highlight which store offers the product (Amazon or Daraz).

For non-shopping queries like greetings or general conversation, respond naturally without using product search tools.
For calculations, use the appropriate math tools.
Keep your responses friendly, informative, and context-aware.
"""),
    ("human", "{conversation}")
])

workflow = StateGraph(state_schema=MessagesState)

# Initialize LLM with tools (assuming 'all_tools' is defined elsewhere)
llm = ChatOllama(
    model="qwen2.5:3b", 
    temperature=0.7,
    repeat_penalty=1.1
).bind_tools([])  # Bind tools as needed

system_prompt_chat = system_prompt_template | llm

# Updated chat function
async def chat(state: MessagesState):
    #================================================================================================
    messages = state["messages"]
    if not messages or len(messages) == 0:
        initial_msg = {
            "role": "assistant", 
            "content": "Hello! I'm your shopping assistant. What are you looking for today?",
            "products": None,
            "timestamp": "now"  # Replace with datetime.now() if needed
        }
        messages.append(initial_msg)
        return {"messages": [initial_msg]}
    
    # Build full conversation history as a string using "role" and "content"
    conversation_lines = []
    for m in messages:
        if isinstance(m, dict):
            role = m.get("role", "unknown")
            content = m.get("content", "")
        else:
            role = getattr(m, "role", "unknown")
            content_attr = getattr(m, "content", "")
            content = content_attr() if callable(content_attr) else content_attr
        conversation_lines.append(f"{role}: {content}")
    conversation_str = "\n".join(conversation_lines)
    print("Full conversation history:")
    print(conversation_str)
    
    # Safely retrieve the latest message's content from the last message
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        latest_message = last_msg.get("content", "")
    else:
        text_attr = getattr(last_msg, "content", "")
        latest_message = text_attr() if callable(text_attr) else text_attr
    print(f"Received message: '{latest_message}'")
    
    # Determine shopping intent (logic remains the same)
    latest_lower = latest_message.lower().strip()
    shopping_keywords = [
        "buy", "purchase", "shop", "product", "price", "cost", 
        "looking for", "find", "search", "show me", "deal", "sale",
        "cheap", "expensive", "affordable", "discount", "recommend",
        "compare", "best", "top", "review", "where can i get", "where to buy"
    ]
    product_categories = [
        "laptop", "phone", "computer", "camera", "tv", "television", "headphone",
        "earphone", "speaker", "monitor", "keyboard", "mouse", "tablet", "watch",
        "shoes", "shirt", "dress", "pants", "jacket", "furniture", "chair", "table",
        "sofa", "bed", "refrigerator", "microwave", "washing machine", "air conditioner",
        "game", "toy", "book", "novel", "smartphone", "iphone", "samsung", "android",
        "bluetooth", "wireless", "charger", "battery", "case", "cover"
    ]
    shopping_intent = any(keyword in latest_lower for keyword in shopping_keywords)
    product_mention = any(category in latest_lower for category in product_categories)
    if shopping_intent:
        print("Shopping intent detected:", [kw for kw in shopping_keywords if kw in latest_lower])
    if product_mention:
        print("Product categories mentioned:", [cat for cat in product_categories if cat in latest_lower])
    has_shopping_intent = shopping_intent or product_mention

    try:
        # Invoke the prompt chain by passing a mapping with conversation history
        response = system_prompt_chat.invoke({"conversation": conversation_str})
        print("Raw model response:", response)
        
        # Extract the assistant response from response.output.messages
        response_content = ""
        if hasattr(response, "output") and response.output and hasattr(response.output, "messages"):
            messages_list = response.output.messages if isinstance(response.output.messages, list) else []
            assistant_msgs = []
            for msg in messages_list:
                if isinstance(msg, dict):
                    role_val = (msg.get("role", "") or msg.get("type", "")).lower()
                    if role_val in ["ai", "assistant"] and msg.get("content", "").strip() != "":
                        assistant_msgs.append(msg)
                else:
                    role_val = (getattr(msg, "role", "") or getattr(msg, "type", "")).lower()
                    if role_val in ["ai", "assistant"] and getattr(msg, "content", "").strip() != "":
                        assistant_msgs.append(msg)
            if assistant_msgs:
                last_assistant = assistant_msgs[-1]
                if isinstance(last_assistant, dict):
                    response_content = last_assistant.get("content", "")
                else:
                    response_content = getattr(last_assistant, "content", "")
        elif hasattr(response, "content"):
            response_content = response.content

        if not response_content or response_content.strip() == "":
            response_content = "I'm sorry, I couldn't generate a proper response."
        
        # Process shopping intent and tool calls if any (logic unchanged)
        product_data = []
        if has_shopping_intent:
            print("Processing shopping intent...")
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"].lower()
                    try:
                        args = tool_call["args"]
                        query_str = args.get("query", latest_message) if isinstance(args, dict) else args
                        if not query_str:
                            query_str = latest_message
                        print(f"Tool call detected for '{tool_name}' with query: {query_str}")
                        if "search_all_products" in tool_name:
                            product_data = direct_search_all_products(query_str)
                        elif "search_amazon_products" in tool_name:
                            product_data = direct_search_amazon_products(query_str)
                        elif "search_daraz_products" in tool_name:
                            product_data = direct_search_daraz_products(query_str)
                        print(f"Found {len(product_data)} products")
                    except Exception as e:
                        print(f"Error processing tool call: {e}")
            elif not product_data:
                try:
                    print(f"Explicit product search triggered for: '{latest_message}'")
                    product_data = direct_search_all_products(latest_message)
                except Exception as e:
                    print(f"Error in explicit search: {e}")
        else:
            print("No shopping intent detected, skipping product search.")
        
        # Create new assistant message with keys "role" and "content"
        new_assistant_message = {
            "role": "assistant",
            "content": response_content,
            "products": product_data if product_data else None,
            "timestamp": "now"  # Replace with actual timestamp if needed
        }
        messages.append(new_assistant_message)
        return {"messages": [new_assistant_message]}
            
    except Exception as e:
        print(f"ERROR in chat function: {e}")
        error_message = {
            "role": "assistant",
            "content": "I'm sorry, I encountered an error processing your request. Could you please try again?",
            "products": None,
            "timestamp": "now"
        }
        messages.append(error_message)
        return {"messages": [error_message]}


workflow = StateGraph(state_schema=MessagesState)

# Add the entrypoint edge from START to your "model" node.
workflow.add_edge(START, "model")

# Add your node that handles chat
workflow.add_node("model", chat)

memory = MemorySaver()
chatapp = workflow.compile(checkpointer=memory)

add_routes(app, chatapp, path="/chat")

@app.get("/")
def read_root():
    return {"message": "ConvoShop AI Server is running"}

# Add these new classes
class ReviewAnalysisRequest(BaseModel):
    product_url: str
    store: str  # 'Amazon' or 'Daraz'

# Define a file to store the results that the frontend can poll
SENTIMENT_RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "sentiment_analysis_results.json")

@app.post("/api/analyze-reviews")
async def analyze_product_reviews(request: ReviewAnalysisRequest, background_tasks: BackgroundTasks):
    """Endpoint to analyze product reviews"""
    try:
        print(f"⭐ Review analysis requested for: {request.product_url}")
        print(f"⭐ Store: {request.store}")
        
        # Determine which scraper to use based on the store
        if request.store.lower() == 'amazon':
            script_path = os.path.join(os.path.dirname(__file__), "..", "amazon_review.py")
            output_file = os.path.join(os.path.dirname(__file__), "..", "amazon_reviews.txt")
        else:  # Default to Daraz
            script_path = os.path.join(os.path.dirname(__file__), "..", "daraz_review.py")
            output_file = os.path.join(os.path.dirname(__file__), "..", "daraz_reviews2.txt")
        
        # Verify script path exists
        if not os.path.exists(script_path):
            error_msg = f"Scraper script not found: {script_path}"
            print(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}
            
        print(f"⭐ Using script: {script_path}")
        print(f"⭐ Output file: {output_file}")
        
        # Run the scraper in the background
        background_tasks.add_task(
            run_review_scraper_and_analysis,
            script_path,
            request.product_url,
            output_file
        )
        
        return {"status": "success", "message": "Review analysis started in background"}
    except Exception as e:
        import traceback
        error_msg = f"Error starting review analysis: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": error_msg}
    
async def run_review_scraper_and_analysis(script_path, product_url, output_file):
    """Run the review scraper and sentiment analysis in the background"""
    try:
        print(f"📢 Starting review analysis for: {product_url}")
        print(f"📢 Using scraper: {script_path}")
        print(f"📢 Output file: {output_file}")
        
        # Import sentiment analysis function based on store type
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        if "amazon" in script_path.lower():
            print("📢 Using Amazon sentiment analysis module")
            from sentiment_analysis_amazon import process_reviews
        else:
            print("📢 Using Daraz sentiment analysis module")
            from sentiment_analysis_daraz import process_reviews
        
        # Set initial status
        with open(SENTIMENT_RESULTS_FILE, 'w') as f:
            json.dump({"status": "scraping", "message": "Scraping reviews..."}, f)
        
        # Run the scraper as a subprocess and capture output
        print(f"📢 Running scraper subprocess: {sys.executable} {script_path} --url '{product_url}' --output '{output_file}' --mode 'api'")
        process = subprocess.run(
            [
                sys.executable, 
                script_path, 
                "--url", product_url,
                "--output", output_file,
                "--mode", "api"
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print subprocess output
        print(f"📢 Scraper stdout: {process.stdout}")
        if process.stderr:
            print(f"⚠️ Scraper stderr: {process.stderr}")
        
        # Check if output file was created and has content
        if not os.path.exists(output_file):
            print(f"❌ Error: Output file not created: {output_file}")
            raise FileNotFoundError(f"Scraper did not create output file: {output_file}")
            
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                print(f"❌ Error: Output file is empty: {output_file}")
                raise ValueError("Scraper produced empty output file")
            else:
                print(f"📢 Review file content length: {len(content)} bytes")
                print(f"📢 First 100 chars: {content[:100]}...")
        
        # Update status
        with open(SENTIMENT_RESULTS_FILE, 'w') as f:
            json.dump({"status": "analyzing", "message": "Analyzing sentiment..."}, f)
        
        # Run sentiment analysis
        print("📢 Starting sentiment analysis...")
        analysis_results = process_reviews(output_file)
        print(f"📢 Sentiment analysis complete - {len(analysis_results)} reviews processed")
        
        # Calculate aggregate sentiment
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for result in analysis_results:
            max_sentiment = max(
                ("Positive", result["Positive"]), 
                ("Negative", result["Negative"]), 
                ("Neutral", result["Neutral"]), 
                key=lambda x: x[1]
            )
            
            if max_sentiment[0] == "Positive":
                positive_count += 1
            elif max_sentiment[0] == "Negative":
                negative_count += 1
            else:
                neutral_count += 1
        
        total_reviews = len(analysis_results)
        print(f"📢 Sentiment breakdown: Positive={positive_count}, Negative={negative_count}, Neutral={neutral_count}")
        
        sentiment_summary = {
            "total_reviews": total_reviews,
            "positive": {
                "count": positive_count,
                "percentage": round((positive_count / total_reviews) * 100 if total_reviews > 0 else 0, 1)
            },
            "negative": {
                "count": negative_count,
                "percentage": round((negative_count / total_reviews) * 100 if total_reviews > 0 else 0, 1)
            },
            "neutral": {
                "count": neutral_count,
                "percentage": round((neutral_count / total_reviews) * 100 if total_reviews > 0 else 0, 1)
            },
            "reviews": analysis_results[:10]  # Send only first 10 reviews for display
        }
        
        # Save final results
        with open(SENTIMENT_RESULTS_FILE, 'w') as f:
            json.dump({
                "status": "completed", 
                "message": "Analysis complete",
                "sentiment_data": sentiment_summary
            }, f)
        print("📢 Analysis complete - results saved to file")
            
    except Exception as e:
        import traceback
        error_message = f"Error during analysis: {str(e)}"
        print(f"❌ {error_message}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        # Save error status
        with open(SENTIMENT_RESULTS_FILE, 'w') as f:
            json.dump({
                "status": "error", 
                "message": error_message
            }, f)

@app.get("/api/review-analysis-status")
async def get_review_analysis_status():
    """Endpoint to check the status of the review analysis"""
    try:
        if os.path.exists(SENTIMENT_RESULTS_FILE):
            with open(SENTIMENT_RESULTS_FILE, 'r') as f:
                return json.load(f)
        else:
            return {"status": "not_started", "message": "No analysis has been started"}
    except Exception as e:
        return {"status": "error", "message": f"Error checking analysis status: {str(e)}"}


#-----------------------MongoDB-----------------------------------------------
# MongoDB Authentication Routes
@app.post("/api/auth/signup")
async def signup(user: User):
    try:
        # Check if the user already exists
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash the password and save the user
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        users_collection.insert_one({"email": user.email, "password": hashed_password})
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"Error during signup: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="An error occurred during signup")

@app.post("/api/auth/login")
async def login(user: User):
    existing_user = users_collection.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(user.password.encode("utf-8"), existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = pyjwt.encode({"id": str(existing_user["_id"]), "email": user.email}, JWT_SECRET, algorithm="HS256")
    return {"token": token}



security = HTTPBearer()

@app.get("/api/auth/me")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials  # Extract the token from the Authorization header
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = users_collection.find_one({"_id": ObjectId(payload["id"])})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": user["email"]}
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

#-----------------------MongoDB-----------------------------------------------

#==================================================================================================#
@app.post("/api/chats/save") #endpoint to save chat
async def save_chat(
    chat_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        # Decode the token to get the user ID
        token = credentials.credentials
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["id"]

        # Save the chat in the database
        chat_data["user_id"] = ObjectId(user_id)
        chats_collection.insert_one(chat_data)

        return {"message": "Chat saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#==================================================================================================#
@app.get("/api/chats")
async def get_chats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Decode the token to get the user ID
        token = credentials.credentials
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["id"]

        # Fetch all chats for the user
        chats = list(chats_collection.find({"user_id": ObjectId(user_id)}))
        for chat in chats:
            chat["_id"] = str(chat["_id"])  # Convert ObjectId to string
            chat["user_id"] = str(chat["user_id"])  # Convert user_id to string

        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#==================================================================================================#
# Define a new endpoint to fetch the formatted chat history
@app.get("/api/chats/formatted-history")
async def get_formatted_chat_history(user_id: str, chat_id: str):
    try:
        # Fetch the specific chat for the user based on user_id and chat_id
        chat = chats_collection.find_one({"user_id": ObjectId(user_id), "_id": ObjectId(chat_id)})
        if not chat:
            return {"history": []}

        # Process the chat history into the desired textual format
        formatted_history = []
        for message in chat.get("messages", []):
            # Format user messages
            if message["sender"] == "user":
                formatted_history.append({"user": message["text"]})
            # Format AI messages
            elif message["sender"] == "ai":
                ai_message = message["text"]
                # Check if products exist in the message
                if "products" in message and message["products"]:
                    product_details = []
                    for product in message["products"]:
                        product_text = (
                            f"Product Name: {product.get('name', 'N/A')}\n"
                            f"Price: {product.get('price', 'N/A')}\n"
                            f"Store: {product.get('store', 'N/A')}\n"
                            f"Specifications: {product.get('specifications', 'N/A')}\n"
                            f"Stars: {product.get('stars', 'N/A')}\n"
                            f"Ratings: {product.get('ratings', 'N/A')}\n"
                            f"URL: {product.get('url', 'N/A')}\n"
                        )
                        product_details.append(product_text)
                    # Append product details to the AI message
                    ai_message += "\n\nProducts:\n" + "\n".join(product_details)
                formatted_history.append({"system": ai_message})

        return {"history": formatted_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#==================================================================================================#
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
