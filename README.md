# ConvoShop

ConvoShop is an intelligent shopping assistant with real-time product search capabilities. It uses conversational AI to help users find products, compare options, and make informed purchasing decisions.

## Features

- 💬 **Conversational Shopping Interface**: Chat naturally with the AI to find products
- 🔍 **Real-time Product Search**: Get up-to-date product information from multiple sources
- 🗄️ **Chat History**: Save and revisit your previous shopping conversations
- 🔒 **User Authentication**: Secure login to save preferences and history
- 🛒 **Shopping Cart**: Add products to cart and manage your selections

## Technologies Used

- **Backend**: FastAPI, Python, Express.js, Node.js
- **Database**: MongoDB
- **AI**: LangChain, LangGraph, Ollama
- **Web Scraping**: Playwright, BeautifulSoup4, Selenium
- **Frontend**: TypeScript, React (implied)

## Prerequisites

- Python 3.8+
- MongoDB
- Ollama (for local LLM support)
- Node.js and npm (for frontend and Express server)

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Fayzan-Alii/ConvoShop.git
cd ConvoShop
```

### 2. Set up the Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root with:

```
MONGO_URI=mongodb://localhost:27017/ConvoShop
JWT_SECRET=your_secure_jwt_secret
```

For the Node.js server:

```
PORT=5001
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/ConvoShop
JWT_SECRET=32@$RD!@EG241XE1E2@e@XR2
```

### 4. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# Using Docker (optional)
docker run -d -p 27017:27017 --name convoshop-mongo mongo:latest
```

### 5. Start Ollama

Ensure Ollama is installed and running with a compatible model:

```bash
ollama run mistral  # or another supported model
```

### 6. Run the backend servers

For the FastAPI server:
```bash
cd backend
uvicorn backend:app --reload
```
The FastAPI backend will be available at http://localhost:8000

For the Express.js server:
```bash
cd server
npm install
npm run dev
```
The Express server will be available at http://localhost:5001

### 7. Set up the frontend

```bash
npm install
npm run dev
```

The frontend will be available at http://localhost:5173 or another specified port.

## API Endpoints

### Authentication
- **POST** `/api/auth/signup`: Register a new user
- **POST** `/api/auth/login`: Log in and receive a JWT token
- **GET** `/api/auth/me`: Get current user profile (requires authentication)

### Chat
- **POST** `/chat/invoke`: Send a message to the shopping assistant
- **GET** `/api/chats`: Get user's chat history (requires authentication)
- **POST** `/api/chats/save`: Save a chat conversation (requires authentication)

### Shopping Cart
- **POST** `/cart`: Add item to cart
- **PUT** `/cart/:id`: Update cart item quantity
- **DELETE** `/cart/:id`: Remove item from cart
- **DELETE** `/cart`: Clear entire cart

## Testing with Postman

1. **Authentication**:
   - Test signup: POST to `/api/auth/signup` with JSON body `{"email": "user@example.com", "password": "password123"}`
   - Test login: POST to `/api/auth/login` with same credentials
   - For authenticated requests: Add header `Authorization: Bearer your_token_here`

2. **Chat**:
   - Test shopping assistant: POST to `/chat/invoke` with JSON body:
     ```json
     {
       "input": {
         "messages": [
           {
             "role": "human",
             "content": "I'm looking for a new laptop"
           }
         ]
       }
     }
     ```
   
3. **Save Chat History**:
   - POST to `/api/chats/save` with JSON body containing chat history and authorization token

## Project Structure

```
ConvoShop/
├── backend/            # Python FastAPI backend
├── server/             # Node.js Express backend
│   ├── .env            # Server environment variables
│   ├── package.json    # Node dependencies
│   └── server.js       # Main Express server file
├── src/                # Frontend source code
│   ├── lib/            # Utility libraries
│   │   └── api.ts      # API client functions
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Database Schema

The project uses both MongoDB:

### MongoDB Collections
- Users: Authentication and user data
- Chats: Saved conversation history
- Products: Scraped product information

