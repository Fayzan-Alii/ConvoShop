# import re
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama import OllamaLLM
# from dotenv import load_dotenv
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# # Ollama Llama2 LLM
# llm = OllamaLLM(model="llama2")

# # Stricter Prompt for keyword extraction
# keyword_extraction_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant. Extract the main product keywords from the user's search query(no details). The answer should be in this format: 'Main keywords are: keyword1, keyword2, keyword3'"),
#     ("user", "Extract the main product keywords from this search query(no details): {query}")
# ])

# # Chain for keyword extraction
# keyword_extraction_chain = keyword_extraction_prompt | llm

# def scrape_daraz(product_name, num_products=5):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
    
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
#     url = f'https://www.daraz.pk/catalog/?q={product_name.replace(" ", "+")}'
#     print(f"Searching URL: {url}")
#     driver.get(url)
    
#     wait = WebDriverWait(driver, 20)
#     wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Bm3ON")]')))
    
#     products = []
#     for product in driver.find_elements(By.XPATH, '//div[contains(@class, "Bm3ON")]')[:num_products]:
#         try:
#             name = product.find_element(By.XPATH, './/a[@title]').get_attribute('title')
#             price = product.find_element(By.CLASS_NAME, 'ooOxS').text
#             location = product.find_element(By.CLASS_NAME, 'oa6ri').get_attribute('title')
#             image_url = product.find_element(By.XPATH, './/img[@type="product"]').get_attribute('src')
#             product_url = product.find_element(By.XPATH, './/a[@title]').get_attribute('href')
#             products.append({"name": name, "price": price, "location": location, "image_url": image_url, "url": product_url})
#         except NoSuchElementException:
#             continue
    
#     driver.quit()
#     return products


# def find_common_words(original_query, extracted_keywords):
#     # Clean and split both the query and keywords into sets of lowercase words
#     original_words = set(re.findall(r'\b\w+\b', original_query.lower()))
#     extracted_words = set(re.findall(r'\b\w+\b', extracted_keywords.lower()))

#     # Define words to exclude
#     exclude_words = {'find', 'search', 'buy'}

#     # Find common words and exclude specific words
#     common_words = original_words.intersection(extracted_words) - exclude_words
#     return list(common_words)

# @app.route('/')
# def index():
#     return "Welcome to the Langchain Ollama Chatbot API!"

# @app.route('/search', methods=['POST'])
# def search():
#     user_query = request.json.get('product')
#     print(f"Received search request: {user_query}")
#     if not user_query:
#         return jsonify({'error': 'No search query provided'}), 400

#     try:
#         # Extract keywords using LLM
#         extracted_keywords = keyword_extraction_chain.invoke({"query": user_query})
#         print(f"Extracted keywords: {extracted_keywords}")

#         # Find common words between the original query and extracted keywords
#         common_words = find_common_words(user_query, extracted_keywords)
#         print(f"Common words: {common_words}")

#         # Join common words for the final search URL
#         search_terms = "+".join(common_words)
#         print(f"Search terms: {search_terms}")

#         # Use extracted keywords for scraping
#         products = scrape_daraz(search_terms)
#         print(f"Scraped products: {products}")
#         return jsonify({'products': products})
#     except Exception as e:
#         print(f"Error during processing: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400

#     try:
#         response = llm.invoke(user_message)
#         return jsonify({'reply': response})
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)


import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama Llama2 LLM
llm = OllamaLLM(model="llama2")

# Stricter Prompt for keyword extraction
keyword_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Extract the main product keywords from the user's search query(no details). The answer should be in this format: 'Main keywords are: keyword1, keyword2, keyword3'"),
    ("user", "Extract the main product keywords from this search query(no details): {query}")
])

# Chain for keyword extraction
keyword_extraction_chain = keyword_extraction_prompt | llm

def scrape_daraz(product_name, num_products=5):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = f'https://www.daraz.pk/catalog/?q={product_name.replace(" ", "+")}'
    print(f"Searching URL: {url}")
    driver.get(url)
    
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Bm3ON")]')))
    
    products = []
    for product in driver.find_elements(By.XPATH, '//div[contains(@class, "Bm3ON")]')[:num_products]:
        try:
            name = product.find_element(By.XPATH, './/a[@title]').get_attribute('title')
            price = product.find_element(By.CLASS_NAME, 'ooOxS').text
            location = product.find_element(By.CLASS_NAME, 'oa6ri').get_attribute('title')
            image_url = product.find_element(By.XPATH, './/img[@type="product"]').get_attribute('src')
            product_url = product.find_element(By.XPATH, './/a[@title]').get_attribute('href')
            products.append({"name": name, "price": price, "location": location, "image_url": image_url, "url": product_url})
        except NoSuchElementException:
            continue
    
    driver.quit()
    return products


# def find_common_words(original_query, extracted_keywords):
#     # Clean and split both the query and keywords into sets of lowercase words
#     original_words = set(re.findall(r'\b\w+\b', original_query.lower()))
#     extracted_words = set(re.findall(r'\b\w+\b', extracted_keywords.lower()))

#     # Define words to exclude
#     exclude_words = {'find', 'search', 'buy'}

#     # Find common words and exclude specific words
#     common_words = original_words.intersection(extracted_words) - exclude_words
#     return list(common_words)

def find_common_words(original_query, extracted_keywords):
    # Clean and split both the query and keywords into sets of lowercase words
    original_words = set(re.findall(r'\b\w+\b', original_query.lower()))
    extracted_words = re.findall(r'\b\w+\b', extracted_keywords.lower())

    # Define words to exclude
    exclude_words = {'find', 'search', 'buy'}

    # Find common words and exclude specific words, maintaining the order of extracted keywords
    common_words = [word for word in extracted_words if word in original_words and word not in exclude_words]
    return common_words

@app.get("/")
async def index():
    return {"message": "Welcome to the Langchain Ollama Chatbot API!"}

# @app.post("/search")
# async def search(request: Request):
#     data = await request.json()
#     user_query = data.get('product')
#     print(f"Received search request: {user_query}")
#     if not user_query:
#         raise HTTPException(status_code=400, detail="No search query provided")

#     try:
#         # Extract keywords using LLM
#         extracted_keywords = keyword_extraction_chain.invoke({"query": user_query})
#         print(f"Extracted keywords: {extracted_keywords}")

#         # Find common words between the original query and extracted keywords
#         common_words = find_common_words(user_query, extracted_keywords)
#         print(f"Common words: {common_words}")

#         # Join common words for the final search URL
#         search_terms = "+".join(common_words)
#         print(f"Search terms: {search_terms}")

#         # Use extracted keywords for scraping
#         products = scrape_daraz(search_terms)
#         print(f"Scraped products: {products}")
#         return {"products": products}
#     except Exception as e:
#         print(f"Error during processing: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: Request):
    data = await request.json()
    user_query = data.get('product')
    print(f"Received search request: {user_query}")
    if not user_query:
        raise HTTPException(status_code=400, detail="No search query provided")

    try:
        # Extract keywords using LLM
        extracted_keywords = keyword_extraction_chain.invoke({"query": user_query})
        print(f"Extracted keywords: {extracted_keywords}")

        # Find common words between the original query and extracted keywords
        common_words = find_common_words(user_query, extracted_keywords)
        print(f"Common words: {common_words}")

        # Join common words for the final search URL
        search_terms = "+".join(common_words)
        print(f"Search terms: {search_terms}")

        # Use extracted keywords for scraping
        products = scrape_daraz(search_terms)
        print(f"Scraped products: {products}")
        return {"products": products}
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get('message')
    if not user_message:
        raise HTTPException(status_code=400, detail="No message provided")

    try:
        response = llm.invoke(user_message)
        return {"reply": response}
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, debug=True)