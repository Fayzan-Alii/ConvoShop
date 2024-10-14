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

