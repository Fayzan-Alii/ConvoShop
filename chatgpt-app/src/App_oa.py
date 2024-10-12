import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Read the API key from the text file
#with open('api_key.txt', 'r') as file:
#    api_key = file.read().strip()  # Read and strip any extra whitespace

# Set the environment variable for OpenAI API key
#os.environ['OPENAI_API_KEY'] = api_key

# Confirm the environment variable is set
print(f"OPENAI_API_KEY is set: {os.environ['OPENAI_API_KEY']}")
# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return "Welcome to the Chat API!"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Use the updated API method with the new completions API
        response = openai.completions.create(
            model="gpt-3.5-turbo",  
            prompt=user_message,
            max_tokens=150
        )
        
        # Extract the bot's reply from the API response
        bot_reply = response.choices[0].text.strip()
        
        return jsonify({'reply': bot_reply})
    
    except Exception as e:
        # Print the full error details for debugging
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

# import os
# from flask import Flask, request, jsonify
# import openai
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Set OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# @app.route('/')
# def index():
#     return "Welcome to the Chat API!"

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400
#     # Add your chat logic here
#     return jsonify({'response': 'This is a placeholder response'})

# if __name__ == '__main__':
#     app.run(debug=True)