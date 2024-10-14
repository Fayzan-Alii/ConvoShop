import React, { useState } from 'react';
import axios from 'axios';
import './App.css';


function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [products, setProducts] = useState([]);

  const handleSend = async () => {
    if (input.trim() === '') return;
    
    const newMessages = [...messages, { user: 'Me', text: input }];
    setMessages(newMessages);

    const isProductSearch = input.toLowerCase().includes('find') || 
                            input.toLowerCase().includes('search') || 
                            input.toLowerCase().includes('buy');

    try {
      if (isProductSearch) {
        console.log('Sending product search request:', input);
        const response = await axios.post('http://localhost:5000/search', { product: input });
        console.log('Received product search response:', response.data);
        setProducts(response.data.products || []);
        console.log('Updated products state:', response.data.products || []);
      } else {
        const response = await axios.post('http://localhost:5000/chat', { message: input });
        const botReply = response.data.reply || 'Sorry, I didn\'t understand that.';
        setMessages([...newMessages, { user: 'Bot', text: botReply }]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages([...newMessages, { user: 'Bot', text: 'Sorry, there was an error.' }]);
    }

    setInput('');
  };

  return (
    <div className="chatgpt-app">
      <div className="chat-panel">
        <div className="chat-header">
          <h2>ConvoShop</h2>
          
        </div>
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`message ${msg.user === 'Me' ? 'me' : 'bot'}`}
            >
              <strong>{msg.user}:</strong> {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input-section">
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            placeholder="Type a message or search for products..."
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
      <div className="additional-panel">
        <h2>Product Results</h2>
        <div className="product-results">
          {products.length > 0 ? (
            products.map((product, index) => (
              <a 
                key={index} 
                href={product.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="product"
              >
                <div className="product-container">
                  <h4>{product.name}</h4>
                  <p>Price: {product.price}</p>
                  <p>Location: {product.location}</p>
                  <img src={product.image_url} alt={product.name} width="100" />
                </div>
              </a>
            ))
          ) : (
            <p>No products found</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;