// import React, { useState } from 'react';
// import axios from 'axios';
// import './App.css'; // Import for styling

// function App() {
//   const [messages, setMessages] = useState([]); // State for storing chat messages
//   const [input, setInput] = useState(''); // State for user input

//   // Function to handle sending the message
//   const handleSend = async () => {
//     if (input.trim() === '') return;
    
//     const newMessages = [...messages, { user: 'Me', text: input }];
//     setMessages(newMessages); // Update the chat UI with user input

//     try {
//       const response = await axios.post('http://localhost:5000/chat', { message: input });
//       const botReply = response.data.reply || 'Sorry, I didn\'t understand that.'; // Default reply if no response
//       setMessages([...newMessages, { user: 'Bot', text: botReply }]); // Update with bot's reply
//     } catch (error) {
//       console.error("Error sending message:", error);
//       setMessages([...newMessages, { user: 'Bot', text: 'Sorry, there was an error.' }]); // Fallback message
//     }

//     setInput(''); // Clear input field after sending
//   };

//   return (
//     <div className="chatgpt-app">
//       <div className="chat-panel">
//         <div className="chat-header">
//           <h2>ChatGPT-like Chat</h2>
//         </div>
//         <div className="chat-messages">
//           {messages.map((msg, index) => (
//             <div 
//               key={index} 
//               className={`message ${msg.user === 'Me' ? 'me' : 'bot'}`}
//             >
//               <strong>{msg.user}:</strong> {msg.text}
//             </div>
//           ))}
//         </div>
//         <div className="chat-input-section">
//           <input 
//             type="text" 
//             value={input} 
//             onChange={(e) => setInput(e.target.value)} 
//             placeholder="Type a message..."
//           />
//           <button onClick={handleSend}>Send</button>
//         </div>
//       </div>
//       <div className="additional-panel">
//         <h2>Additional Panel</h2>
//         <p>This is where additional information or content can be displayed.</p>
//       </div>
//     </div>
//   );
// }

// export default App;


// import React, { useState } from 'react';
// import axios from 'axios';
// import './App.css'; // Import for styling

// function App() {
//   const [messages, setMessages] = useState([]); // State for storing chat messages
//   const [input, setInput] = useState(''); // State for user input
//   const [productSearch, setProductSearch] = useState(''); // State for product search
//   const [products, setProducts] = useState([]); // State for storing product results

//   // Function to handle sending the message
//   const handleSend = async () => {
//     if (input.trim() === '') return;
    
//     const newMessages = [...messages, { user: 'Me', text: input }];
//     setMessages(newMessages); // Update the chat UI with user input

//     try {
//       const response = await axios.post('http://localhost:5000/chat', { message: input });
//       const botReply = response.data.reply || 'Sorry, I didn\'t understand that.'; // Default reply if no response
//       setMessages([...newMessages, { user: 'Bot', text: botReply }]); // Update with bot's reply
//     } catch (error) {
//       console.error("Error sending message:", error);
//       setMessages([...newMessages, { user: 'Bot', text: 'Sorry, there was an error.' }]); // Fallback message
//     }

//     setInput(''); // Clear input field after sending
//   };

//   // Function to handle product search
//   const handleProductSearch = async () => {
//     if (productSearch.trim() === '') return;

//     try {
//       const response = await axios.post('http://localhost:5000/search', { product: productSearch });
//       setProducts(response.data.products || []); // Update product results
//     } catch (error) {
//       console.error("Error fetching products:", error);
//     }

//     setProductSearch(''); // Clear input field after search
//   };

//   return (
//     <div className="chatgpt-app">
//       <div className="chat-panel">
//         <div className="chat-header">
//           <h2>Chat and Product Search</h2>
//         </div>
//         <div className="chat-messages">
//           {messages.map((msg, index) => (
//             <div 
//               key={index} 
//               className={`message ${msg.user === 'Me' ? 'me' : 'bot'}`}
//             >
//               <strong>{msg.user}:</strong> {msg.text}
//             </div>
//           ))}
//         </div>
//         <div className="chat-input-section">
//           <input 
//             type="text" 
//             value={input} 
//             onChange={(e) => setInput(e.target.value)} 
//             placeholder="Type a message..."
//           />
//           <button onClick={handleSend}>Send</button>
//         </div>
//       </div>
//       <div className="additional-panel">
//         <h2>Product Search</h2>
//         <input 
//           type="text" 
//           value={productSearch} 
//           onChange={(e) => setProductSearch(e.target.value)} 
//           placeholder="Search for a product..."
//         />
//         <button onClick={handleProductSearch}>Search</button>
//         <div className="product-results">
//           {products.length > 0 ? (
//             products.map((product, index) => (
//               <div key={index} className="product">
//                 <h4>{product.name}</h4>
//                 <p>Price: {product.price}</p>
//                 <p>Country: {product.country}</p>
//                 <img src={product.image_url} alt={product.name} width="100" />
//               </div>
//             ))
//           ) : (
//             <p>No products found</p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;

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