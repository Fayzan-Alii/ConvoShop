# import os
# import torch
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# app = Flask(__name__)
# CORS(app)

# # Load the pre-trained conversational model (DialoGPT)
# conv_model_name = "microsoft/DialoGPT-medium"
# conv_tokenizer = AutoTokenizer.from_pretrained(conv_model_name)
# conv_model = AutoModelForCausalLM.from_pretrained(conv_model_name)

# # Load the pre-trained QA model (SQuAD)
# qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased-distilled-squad")

# # To keep track of conversation history for the conversational model
# conversation_history = []

# @app.route('/')
# def index():
#     return "Welcome to the Chat API!"

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400

#     try:
#         # Check if the user message is a factual question or conversational
#         if "?" in user_message:  # Simple check for a question mark (can be more sophisticated)
#             # Factual query - use the QA model
#             context = "Apples are a type of fruit that grow on apple trees. They are typically red, green, or yellow."
#             qa_response = qa_pipeline({
#                 'question': user_message,
#                 'context': context
#             })
#             bot_reply = qa_response['answer']
#         else:
#             # Conversational query - use DialoGPT
#             new_user_input_ids = conv_tokenizer.encode(user_message + conv_tokenizer.eos_token, return_tensors='pt')
#             conversation_history.append(new_user_input_ids)
#             bot_input_ids = torch.cat(conversation_history, dim=-1)
#             response_ids = conv_model.generate(bot_input_ids, max_length=1000, pad_token_id=conv_tokenizer.eos_token_id, temperature=0.7, top_p=0.9)
#             bot_reply = conv_tokenizer.decode(response_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
#             conversation_history.append(conv_tokenizer.encode(bot_reply + conv_tokenizer.eos_token, return_tensors='pt'))

#         return jsonify({'reply': bot_reply})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'error': str(e)}), 500


# @app.route('/reset', methods=['POST'])
# def reset_conversation():
#     """Resets the conversation history."""
#     global conversation_history
#     conversation_history = []
#     return jsonify({'message': 'Conversation reset.'})


# if __name__ == '__main__':
#     app.run(debug=True)


# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_ollama import OllamaLLM  # Updated import
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# # Prompt Template
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant. Please respond to user queries."),
#         ("user", "Question: {question}")
#     ]
# )

# # Ollama Llama2 LLM
# llm = OllamaLLM(model="llama2")  # Updated class

# # Output parser for formatting the response
# output_parser = StrOutputParser()

# # Chain: prompt -> llm -> output_parser
# chain = prompt | llm | output_parser

# @app.route('/')
# def index():
#     return "Welcome to the Langchain Ollama Chatbot API!"

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400

#     try:
#         # Invoke the chain with the user's query
#         response = chain.invoke({"question": user_message})
#         return jsonify({'reply': response})

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app)

# Ollama Llama2 LLM
llm = OllamaLLM(model="llama2")

# Stricter Prompt for keyword extraction
keyword_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Extract the main product keywords from the user's search query(no details). The answer should be in this format: 'Main keywords are: keyword1, keyword2, keyword3'"),
    ("user", "Extract the main product keywords from this search query(no details): {query}")
])

# Chain for keyword extraction
keyword_extraction_chain = keyword_extraction_prompt | llm

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
#             products.append({"name": name, "price": price, "location": location, "image_url": image_url})
#         except NoSuchElementException:
#             continue
    
#     driver.quit()
#     return products

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
#     original_words = set(re.findall(r'\b\w+\b', original_query.lower()))  # Splitting words
#     extracted_words = set(re.findall(r'\b\w+\b', extracted_keywords.lower()))  # Extracted keywords in list form
    
#     # Find common words
#     common_words = original_words.intersection(extracted_words)
#     return list(common_words)

def find_common_words(original_query, extracted_keywords):
    # Clean and split both the query and keywords into sets of lowercase words
    original_words = set(re.findall(r'\b\w+\b', original_query.lower()))
    extracted_words = set(re.findall(r'\b\w+\b', extracted_keywords.lower()))

    # Define words to exclude
    exclude_words = {'find', 'search', 'buy'}

    # Find common words and exclude specific words
    common_words = original_words.intersection(extracted_words) - exclude_words
    return list(common_words)

@app.route('/')
def index():
    return "Welcome to the Langchain Ollama Chatbot API!"

@app.route('/search', methods=['POST'])
def search():
    user_query = request.json.get('product')
    print(f"Received search request: {user_query}")
    if not user_query:
        return jsonify({'error': 'No search query provided'}), 400

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
        return jsonify({'products': products})
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = llm.invoke(user_message)
        return jsonify({'reply': response})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)