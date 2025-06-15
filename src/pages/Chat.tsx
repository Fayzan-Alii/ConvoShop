import { useState, useEffect, useRef, useCallback } from 'react';
import { Send, ShoppingBag, BarChart2, AlertCircle, CheckCircle, Clock, Search, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { useTheme } from '@/lib/ThemeContext';
import { useAuth } from '@/lib/AuthContext';
import { useCart } from '@/lib/CartContext';
import { productAPI, reviewAnalysisAPI } from '@/lib/api';
import chatAPI, { Product as ScrapedProduct } from '@/lib/chatAPI';
import { v4 as uuidv4 } from 'uuid';
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/Modal';
import { Progress } from '@/components/ui/Progress';
import { Sparkles } from 'lucide-react';
import axios from 'axios';
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  products?: ScrapedProduct[];
  recommendations?: {
    type: 'price' | 'feature' | 'specification';
    content: string;
  }[];
}

interface Product {
  _id: string;
  title: string;
  price: number;
  image_url: string;
  store: string;
  specifications?: string;
  stars?: string;
  ratings?: string;
}

interface ReviewData {
  Text: string;
  "Review ID": string;
  Positive: number;
  Negative: number;
  Neutral: number;
  [key: string]: any; // For any other properties
}

interface SentimentData {
  total_reviews: number;
  positive: { count: number; percentage: number };
  negative: { count: number; percentage: number };
  neutral: { count: number; percentage: number };
  reviews: ReviewData[];
  star_distribution?: { [key: string]: number };
  total_rating_count?: number;
  average_rating?: number;
}

export function Chat() {
  const { theme } = useTheme();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your shopping assistant. What are you looking for today?",
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);

  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState<boolean>(false);
  const [productRecommendations, setProductRecommendations] = useState<ScrapedProduct[]>([]);
  const [selectedProductForRecs, setSelectedProductForRecs] = useState<ScrapedProduct | null>(null);

  // Add after your existing state declarations
  const [selectedProduct, setSelectedProduct] = useState<ScrapedProduct | null>(null);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState<'idle' | 'loading' | 'completed' | 'error'>('idle');
  const analysisStatusInterval = useRef<NodeJS.Timeout | null>(null);
  const [analysisResult, setAnalysisResult] = useState<SentimentData | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]); // Chat history state
  const [selectedChat, setSelectedChat] = useState<any>(null); // Selected chat state
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [threadId] = useState(() => uuidv4());
  const [recommendations, setRecommendations] = useState<{
    type: 'price' | 'feature' | 'specification';
    content: string;
  }[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (user) {
        const token = localStorage.getItem('token');
        if (token) {
          try {
            const { chats } = await chatAPI.getChats(token);
            setChatHistory(chats);
          } catch (error) {
            console.error('Failed to fetch chat history:', error);
          }
        }
      }
    };
    fetchChatHistory();
  }, [user]);

  //Handle Chat Selection
  const handleChatSelect = (chat: any) => {
    setSelectedChat(chat);
    setMessages(chat.messages || []); // Load messages from the selected chat
  };

  //Handle New Chat
  const handleNewChat = async () => {
    const newChat = {
      title: `New Chat ${chatHistory.length + 1}`,
      date: new Date().toLocaleString(),
      messages: [],
    };
  
    setChatHistory((prev) => [newChat, ...prev]); // Add the new chat to the history
    setSelectedChat(newChat); // Set the new chat as the active chat
    setMessages([]); // Clear the messages for the new chat
  
    // Save the new chat to the database
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await chatAPI.saveChat(newChat, token);
        const savedChat = response.chat;
        setChatHistory((prev) =>
          prev.map((chat) => (chat === newChat ? savedChat : chat))
        );
        setSelectedChat(savedChat);
      } catch (error) {
        console.error('Failed to save new chat:', error);
      }
    }
  };

  const handleShowRecommendations = async (product: ScrapedProduct) => {
    if (!product.url) {
      console.error("Product URL is required for recommendations");
      return;
    }
    
    setIsLoadingRecommendations(true);
    setSelectedProductForRecs(product);
    
    try {
      console.log(`Fetching recommendations for ${product.name} from ${product.store}`);
      const result = await chatAPI.getProductRecommendations(
        product.url, 
        product.store || 'Amazon',
        8
      );
      
      if (result.status === 'success' && result.recommendations) {
        // Convert to ScrapedProduct format
        const recs: ScrapedProduct[] = result.recommendations.map((rec: any) => ({
          name: rec.title || rec.name,
          price: rec.price,
          image: rec.image,
          url: rec.url,
          store: rec.store || product.store,
          _id: Date.now() + Math.random().toString(36).substring(2, 9)
        }));
        
        setProductRecommendations(recs);
      } else {
        setProductRecommendations([]);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setProductRecommendations([]);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  //handle submit
  
  // const handleSubmit = async (e: React.FormEvent) => {
  //   e.preventDefault();
  //   if (!message.trim()) return;
  
  //   const userMessage: Message = {
  //     id: Date.now().toString(),
  //     text: message,
  //     sender: 'user',
  //     timestamp: new Date(),
  //   };
  
  //   setMessages((prev) => [...prev, userMessage]);
  //   setMessage('');
  //   setIsTyping(true);
  
  //   try {
  //     console.log("Sending message to AI:", message);
  //     const response = await chatAPI.sendMessage(message, threadId);
  //     console.log("Raw API response received:", response);
  
  //     const aiContent = response?.messages?.[response.messages.length - 1]?.content || "I'm sorry, I couldn't generate a proper response.";
  //     const scrapedProducts: ScrapedProduct[] = response?.messages?.[response.messages.length - 1]?.products || [];
  
  //     const assistantMessage: Message = {
  //       id: (Date.now() + 1).toString(),
  //       text: aiContent,
  //       sender: 'ai',
  //       timestamp: new Date(),
  //       products: scrapedProducts.length > 0 ? scrapedProducts : undefined,
  //     };
  
  //     setMessages((prev) => [...prev, assistantMessage]);
  
  //     // Save the chat session
  //     const token = localStorage.getItem('token');
  //     if (token) {
  //       const updatedChat = {
  //         ...selectedChat,
  //         messages: [...messages, userMessage, assistantMessage],
  //       };
  //       await chatAPI.saveChat(updatedChat, token); // Ensure `_id` is included for existing chats
  //     }
  //   } catch (error) {
  //     console.error("Error communicating with AI:", error);
  //     setMessages((prev) => [
  //       ...prev,
  //       {
  //         id: (Date.now() + 1).toString(),
  //         text: "Sorry, I'm having trouble connecting right now. Please try again later.",
  //         sender: 'ai',
  //         timestamp: new Date(),
  //       },
  //     ]);
  //   } finally {
  //     setIsTyping(false);
  //   }
  // };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    const currentUserQuery = message;
    setMessage('');
    setIsTyping(true);
    
    let retries = 2;
    let success = false;
    
    while (retries >= 0 && !success) {
      try {
        console.log("Sending message to AI:", currentUserQuery);
        const response = await chatAPI.sendMessage(currentUserQuery, threadId);
        console.log("Full AI response:", JSON.stringify(response).substring(0, 500) + "...");
        
        let aiContent = "I'm sorry, I couldn't generate a proper response.";
        let scrapedProducts: ScrapedProduct[] = [];
        let newRecommendations: { type: 'price' | 'feature' | 'specification'; content: string }[] = [];
        
        if (response && response.output) {
          if (response.output.content) {
            aiContent = response.output.content;
          }
          if (response.output.products && Array.isArray(response.output.products)) {
            scrapedProducts = response.output.products;
          }
          if (response.output.recommendations && Array.isArray(response.output.recommendations)) {
            newRecommendations = response.output.recommendations;
            setRecommendations(newRecommendations);
          }
        } else if (response && response.messages) {
          if (Array.isArray(response.messages)) {
            const lastMsg = response.messages[response.messages.length - 1];
            aiContent = lastMsg.content || "";
            if (lastMsg.products && Array.isArray(lastMsg.products)) {
              scrapedProducts = lastMsg.products;
            }
          } else if (typeof response.messages === 'object') {
            const msgObj = response.messages as any;
            aiContent = msgObj.content || "";
            if (msgObj.products && Array.isArray(msgObj.products)) {
              scrapedProducts = msgObj.products;
            }
          }
        } else if (response && response.content) {
          aiContent = response.content;
        }
        
        // Remove echo check condition to preserve valid assistant response
        
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            text: aiContent,
            sender: 'ai',
            timestamp: new Date(),
            products: scrapedProducts.length > 0 ? scrapedProducts : undefined,
            recommendations: newRecommendations.length > 0 ? newRecommendations : undefined,
          },
        ]);
        
        //Save the chat session
        const token = localStorage.getItem('token');
        if (token) {
          const updatedChat = {
            ...selectedChat,
            messages: [...messages, userMessage, {
              ...userMessage,
              sender: 'ai',
              text: aiContent,
              products: scrapedProducts.length > 0 ? scrapedProducts : undefined,
              recommendations: newRecommendations.length > 0 ? newRecommendations : undefined,
            }],
          };
          await chatAPI.saveChat(updatedChat, token);
        }

        // If products were scraped, update UI products (conversion logic as needed)
        if (scrapedProducts.length > 0) {
          console.log("SUCCESS: Found products:", scrapedProducts.length);
          const uiProducts: Product[] = scrapedProducts.map(p => {
            let price = 0;
            if (typeof p.price === 'string') {
              const priceStr = p.price.replace(/[^0-9.]/g, '');
              price = priceStr ? parseFloat(priceStr) : 0;
            } else if (typeof p.price === 'number') {
              price = p.price;
            }
            return {
              _id: Date.now() + Math.random().toString(36).substring(2, 9),
              title: p.name || 'Unknown Product',
              price: price,
              image_url: p.image || 'https://via.placeholder.com/300',
              store: p.store || 'Online Store',
              specifications: p.specifications || '',
              stars: p.stars || '',
              ratings: p.ratings || ''
            };
          });
          setProducts(uiProducts);
        }
        
        success = true;
      } catch (error: any) {
        console.error(`Error communicating with AI (retries left: ${retries}):`, error);
        retries--;
        if (retries < 0) {
          setMessages((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              text: "Sorry, I'm having trouble connecting right now. Please try again later.",
              sender: 'ai',
              timestamp: new Date(),
            },
          ]);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      } finally {
        if (success || retries < 0) {
          setIsTyping(false);
        }
      }

    }
  };

  const handleAddToCart = async (productId: string) => {
    if (!user) return;
    try {
      console.log("Adding product to cart:", productId);
      await addToCart(productId);
      console.log("Product added to cart successfully");
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const handleAddScrapedToCart = async (product: ScrapedProduct) => {
    if (!user) return;
    try {
      console.log("Adding scraped product to cart:", product.name);
      let price = 0;
      if (typeof product.price === 'string') {
        const priceStr = product.price.replace(/[^0-9.]/g, '');
        price = priceStr ? parseFloat(priceStr) : 0;
      } else if (typeof product.price === 'number') {
        price = product.price;
      }
      
      const productData = {
        title: product.name || 'Unknown Product',
        price: price,
        image_url: product.image || 'https://via.placeholder.com/300',
        store: product.store || 'Online Store',
        description: product.specifications || ''
      };
      
      console.log("Creating new product in database:", productData);
      const newProduct = await productAPI.createProduct(productData);
      console.log("Product created with ID:", newProduct._id);
      
      await addToCart(newProduct._id);
      console.log("Scraped product added to cart successfully");
    } catch (error) {
      console.error('Error adding scraped product to cart:', error);
    }
  };
//----------------------------------------------------------------------
  // Add this function inside your Chat component
  const handleAddToWishlist = async (product: ScrapedProduct) => {
  if (!user) {
    alert('Please log in to add to wishlist');
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    const response = await axios.post(
      'http://localhost:8000/api/wishlist/add',
      {
        product_url: product.url || '',
        product_name: product.name || '',
        image: product.image || '',
        price: typeof product.price === 'string' ? product.price : product.price?.toString() || '',
        rating: product.stars || '',
        store: product.store || '',
        last_checked_price: typeof product.price === 'string' ? product.price : product.price?.toString() || '',
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    if (response.data && response.data.message === 'Product already in wishlist') {
      alert('⚠️ Product already in wishlist');
    } else {
      alert('✅ Product added to wishlist');
    }

  } catch (error: any) {
    if (
      error.response &&
      error.response.status === 400 &&
      error.response.data.detail === 'Product already in wishlist'
    ) {
      alert('⚠️ Product already in wishlist');
    } else {
      console.error('Error adding to wishlist:', error);
      alert('❌ Failed to add product to wishlist');
    }
  }
};

  //----------------------------------------------------------------------
  const handleAnalyzeReviews = useCallback(async (product: ScrapedProduct) => {
    if (!product.url) {
      console.error("Cannot analyze reviews: Product URL is missing");
      return;
    }
    
    console.log("🔍 Starting review analysis for:", product);
    console.log("🔍 Product URL:", product.url);
    console.log("🔍 Store:", product.store);
    
    setSelectedProduct(product);
    setShowAnalysisModal(true);
    setAnalysisStatus('loading');
    setAnalysisResult(null);
    
    try {
      // Start the analysis
      console.log("🔍 Sending analysis request to backend");
      const response = await reviewAnalysisAPI.analyzeProductReviews(product.url!, product.store || 'Unknown');
      console.log("🔍 Backend response:", response);
      
      // Poll for status updates
      if (analysisStatusInterval.current) {
        clearInterval(analysisStatusInterval.current);
      }
      
      analysisStatusInterval.current = setInterval(async () => {
        try {
          console.log("🔍 Checking analysis status...");
          const status = await reviewAnalysisAPI.checkAnalysisStatus();
          console.log("🔍 Status update:", status);
          
          if (status.status === 'completed') {
            console.log("✅ Analysis completed!");
            console.log("✅ Results:", status.sentiment_data);
            clearInterval(analysisStatusInterval.current!);
            setAnalysisStatus('completed');
            setAnalysisResult(status.sentiment_data);
          } else if (status.status === 'error') {
            console.error('❌ Analysis error:', status.message);
            clearInterval(analysisStatusInterval.current!);
            setAnalysisStatus('error');
          }
        } catch (error) {
          console.error('❌ Error checking analysis status:', error);
        }
      }, 2000);
    } catch (error) {
      console.error('❌ Error starting review analysis:', error);
      setAnalysisStatus('error');
    }
  }, []);

// Add cleanup effect
useEffect(() => {
  return () => {
    if (analysisStatusInterval.current) {
      clearInterval(analysisStatusInterval.current);
    }
  };
}, []);

  function logout(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
    event.preventDefault();
    localStorage.removeItem('token'); // Remove the token from local storage
    window.location.reload(); // Reload the page to reset the app state
  }
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
      <div className="flex gap-6">
        {/* Chat History Sidebar - UPDATED */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-1/4 min-w-[320px] max-w-[380px] hidden lg:block" 
        >
          <div className={`${theme === 'dark' ? 'bg-gray-800/80' : 'bg-white/80'} backdrop-blur-lg rounded-2xl shadow-lg p-4`}>
            <div className="flex items-center gap-2 mb-6">
              <Clock className={`w-5 h-5 ${theme === 'dark' ? 'text-indigo-400' : 'text-indigo-600'}`} />
              <h2 className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Chat History</h2>
            </div>
            
            <button
               onClick={handleNewChat}
               className={`w-full flex items-center justify-center gap-2 p-3 mb-4 rounded-xl ${theme === 'dark' ? 'bg-indigo-900 text-white' : 'bg-indigo-100 text-indigo-600'} hover:bg-indigo-200 transition`}
              >
              <Plus className="w-5 h-5" />
              New Chat
            </button>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder="Search conversations..."
                className={`w-full pl-10 pr-4 py-2 rounded-xl border ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-200 text-gray-900'} focus:outline-none focus:ring-2 focus:ring-indigo-500`}
              />
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
            <div className="space-y-2">
              {chatHistory.map((chat) => (
                <motion.button
                  key={chat.id}
                  onClick={() => handleChatSelect(chat)}
                  className={`w-full text-left p-3 rounded-xl ${theme === 'dark' ? 'hover:bg-indigo-900/30' : 'hover:bg-indigo-50'} transition-colors`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <h3 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-800'} animated-text`}>{chat.title}</h3>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{chat.date}</p>
                </motion.button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Main Chat Area */}
        <div className="flex-1">
          <div className="glass-effect rounded-2xl shadow-lg h-[calc(100vh-8rem)]">
            <div className="h-full flex flex-col">
              <div className="flex-1 overflow-y-auto p-6">
                 {/* Display logged-in user's email */}
                 {user && (
                  <div className="mb-4 text-sm text-gray-500">
                    Logged in as: <span className="font-medium">{user.email}</span>
                    <button
                      onClick={logout}
                      className="ml-4 text-red-500 hover:underline text-xs"
                    >
                      Logout
                    </button>
                  </div>
                )}
                {/* {messages.some(m => m.products && m.products.length > 0) && (
                  <div className="sticky top-0 bg-green-500 text-white text-xs px-2 py-1 rounded-md mb-2 z-10">
                    Products available: {messages.reduce((total, m) => total + (m.products?.length || 0), 0)}
                  </div>
                )} */}
                <AnimatePresence>
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                    >
                      <div className={`message-bubble ${msg.sender} max-w-2xl`}>
                        {msg.text}
                        {msg.recommendations && msg.recommendations.length > 0 && (
                          <div className="mt-4 space-y-2">
                            {msg.recommendations.map((rec, index) => (
                              <div
                                key={index}
                                className={`p-2 rounded ${
                                  rec.type === 'price'
                                    ? 'bg-green-100 dark:bg-green-900'
                                    : rec.type === 'feature'
                                    ? 'bg-blue-100 dark:bg-blue-900'
                                    : 'bg-purple-100 dark:bg-purple-900'
                                }`}
                              >
                                <p className="text-xs font-medium">
                                  {rec.type.charAt(0).toUpperCase() + rec.type.slice(1)} Recommendation:
                                </p>
                                <p className="text-xs">{rec.content}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        {msg.sender === 'ai' && msg.products && msg.products.length > 0 && (
                          <div className="mt-4 pb-2">
                            <p className="font-medium mb-2">Found {msg.products.length} products for you:</p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 py-2">
                            {msg.products.map((product, idx) => (
                              <motion.div 
                                key={idx}
                                whileHover={{ scale: 1.02 }}
                                className={`flex flex-col h-full ${theme === 'dark' ? 'bg-gray-700' : 'bg-white/90'} rounded-lg shadow overflow-hidden border ${theme === 'dark' ? 'border-gray-600' : 'border-gray-200'}`}
                              >
                                <a 
                                  href={product.url ? product.url : 
                                    (product.store === 'Amazon' ? 
                                      `https://www.amazon.com/s?k=${encodeURIComponent(product.name || '')}` : 
                                      `https://www.daraz.pk/catalog/?q=${encodeURIComponent(product.name || '')}`)
                                  } 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="block"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  {/* Product Image */}
                                  <div className="relative pt-[60%] overflow-hidden bg-gray-100">
                                    <img 
                                      src={product.image || 'https://via.placeholder.com/300?text=No+Image'}
                                      alt={product.name || 'Product'}
                                      className="absolute inset-0 w-full h-full object-contain p-2"
                                      onError={(e) => {
                                        const target = e.target as HTMLImageElement;
                                        target.src = 'https://via.placeholder.com/300?text=No+Image';
                                      }}
                                    />
                                  </div>

                                  <div className="p-3 flex-1 flex flex-col">
                                    {/* Product Name */}
                                    <h3 className="font-medium text-sm line-clamp-2 mb-2">{product.name}</h3>
                                    
                                    {/* Store */}
                                    <div className="flex items-center mt-1 mb-2">
                                      <span className={`px-2 py-1 text-xs rounded-full ${
                                        product.store === 'Amazon' 
                                          ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100' 
                                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                                      }`}>
                                        {product.store}
                                      </span>
                                    </div>
                                    
                                    {/* Price */}
                                    <p className="text-sm text-indigo-500 font-semibold mb-2">
                                      {typeof product.price === 'string' && product.price.includes('Rs.') 
                                        ? product.price 
                                        : (typeof product.price === 'number' 
                                          ? `$${product.price.toFixed(2)}` 
                                          : `$${parseFloat(product.price.toString().replace(/[^0-9.]/g, '')).toFixed(2) || '0.00'}`
                                        )}
                                    </p>
                                    
                                    {/* Stars */}
                                    <div className="flex items-center mt-auto mb-2">
                                      {product.stars && (
                                        <div className="flex items-center">
                                          <span className="text-yellow-500 mr-1">★</span>
                                          <span className="text-xs">{product.stars}</span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </a>
                                
                                {/* Button group - UPDATED */}
                                <div className="px-3 pb-3 flex space-x-1"> {/* Changed from space-x-2 to space-x-1 */}
                                  <Button 
                                    size="sm" 
                                    className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 py-1 px-1" /* Added px-1 to reduce horizontal padding */
                                    onClick={() => handleAddToWishlist(product)}
                                  >
                                    <ShoppingBag className="w-3 h-3 mr-0.5" /> {/* Changed mr-1 to mr-0.5 */}
                                    <span className="text-xs">Add</span> {/* Shortened text from "Add to Cart" to "Add" */}
                                  </Button>
                                  
                                  <Button 
                                    size="sm" 
                                    className="flex-1 bg-gradient-to-r from-teal-500 to-emerald-500 py-1 px-1" /* Added px-1 */
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      handleAnalyzeReviews(product);
                                    }}
                                    disabled={!product.url}
                                  >
                                    <BarChart2 className="w-3 h-3 mr-0.5" /> {/* Changed mr-1 to mr-0.5 */}
                                    <span className="text-xs">Reviews</span>
                                  </Button>
                                  
                                  <Button 
                                    size="sm" 
                                    className="flex-1 bg-gradient-to-r from-amber-500 to-yellow-500 py-1 px-1" /* Added px-1 */
                                    onClick={() => handleShowRecommendations(product)}
                                    disabled={!product.url}
                                  >
                                    <Sparkles className="w-3 h-3 mr-0.5" /> {/* Changed mr-1 to mr-0.5 */}
                                    <span className="text-xs">Similar</span>
                                  </Button>
                                </div>
                              </motion.div>
                            ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {isTyping && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start mb-4"
                  >
                    <div className="message-bubble ai max-w-2xl flex space-x-1">
                      <span className="w-2 h-2 rounded-full bg-white animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 rounded-full bg-white animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 rounded-full bg-white animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>
              <form onSubmit={handleSubmit} className={`border-t ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'} p-4`}>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="What are you looking for?"
                    className={`floating-input flex-1 rounded-xl border ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-200 text-gray-900'} px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500`}
                    disabled={isTyping}
                  />
                  <Button
                    type="submit"
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl px-6"
                    disabled={isTyping || !message.trim()}
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    {/* Review Analysis Modal - ADD HERE */}
    {showAnalysisModal && (
      <Modal
        isOpen={showAnalysisModal}
        onClose={() => {
          if (analysisStatusInterval.current) {
            clearInterval(analysisStatusInterval.current);
          }
          setShowAnalysisModal(false);
        }}
        size="lg"
      >
        <ModalContent>
          <ModalHeader>
            <div className="text-lg font-semibold mb-1">Review Analysis</div>
            <div className="text-sm text-gray-500 truncate">
              {selectedProduct?.name}
            </div>
          </ModalHeader>
          
          <ModalBody>
            {analysisStatus === 'loading' && (
              <div className="py-8 flex flex-col items-center">
                <Clock className="h-12 w-12 text-indigo-500 animate-pulse mb-3" />
                <h3 className="text-lg font-medium mb-2">Analyzing reviews...</h3>
                <p className="text-gray-500 mb-4 text-center">
                  This may take a minute or two as we scrape and analyze reviews
                </p>
                <Progress value={undefined} className="w-full max-w-md" />
              </div>
            )}
            
            {analysisStatus === 'error' && (
              <div className="py-8 flex flex-col items-center">
                <AlertCircle className="h-12 w-12 text-red-500 mb-3" />
                <h3 className="text-lg font-medium mb-2">Analysis Error</h3>
                <p className="text-gray-500 text-center">
                  Sorry, we couldn't complete the review analysis. This could be due to no reviews being available or a technical issue.
                </p>
              </div>
            )}
            
            {analysisStatus === 'completed' && analysisResult && (
              <div className="py-2">
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-3">Sentiment Summary</h3>
                  <div className="grid grid-cols-3 gap-3">
                    <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-green-900/30' : 'bg-green-50'}`}>
                      <div className="text-green-600 text-2xl font-bold">
                        {analysisResult.positive.percentage}%
                      </div>
                      <div className="text-sm mt-1">Positive</div>
                      <div className="text-xs text-gray-500">{analysisResult.positive.count} reviews</div>
                    </div>
                    <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-yellow-900/30' : 'bg-yellow-50'}`}>
                      <div className="text-yellow-600 text-2xl font-bold">
                        {analysisResult.neutral.percentage}%
                      </div>
                      <div className="text-sm mt-1">Neutral</div>
                      <div className="text-xs text-gray-500">{analysisResult.neutral.count} reviews</div>
                    </div>
                    <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-red-900/30' : 'bg-red-50'}`}>
                      <div className="text-red-600 text-2xl font-bold">
                        {analysisResult.negative.percentage}%
                      </div>
                      <div className="text-sm mt-1">Negative</div>
                      <div className="text-xs text-gray-500">{analysisResult.negative.count} reviews</div>
                    </div>
                  </div>
                </div>        
                {/* Add Star Distribution Section */}
                {analysisResult.star_distribution && Object.keys(analysisResult.star_distribution).length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-3">Star Rating Distribution</h3>
                    <div className="flex items-center mb-1">
                      <span className="text-yellow-500 text-lg mr-1">★</span>
                      <span className="font-medium">
                        {analysisResult.average_rating?.toFixed(1) || "N/A"} 
                        <span className="text-sm text-gray-500 ml-1">
                          ({analysisResult.total_rating_count || 0} ratings)
                        </span>
                      </span>
                    </div>
                    
                    <div className="space-y-2 mt-3">
                      {[5, 4, 3, 2, 1].map(star => {
                        const count = analysisResult.star_distribution?.[star] || 0;
                        const percentage = analysisResult.total_rating_count 
                          ? Math.round((count / analysisResult.total_rating_count) * 100)
                          : 0;
                          
                        return (
                          <div key={star} className="flex items-center">
                            <div className="w-12 text-sm">{star} star</div>
                            <div className="w-full mx-2">
                              <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                                <div 
                                  className="h-2 rounded-full bg-yellow-400"
                                  style={{ width: `${percentage}%` }} 
                                ></div>
                              </div>
                            </div>
                            <div className="w-10 text-sm text-right">{percentage}%</div>
                            <div className="w-16 text-xs text-gray-500 text-right">({count})</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}                
                {analysisResult.reviews && analysisResult.reviews.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium mb-3">Sample Reviews</h3>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                    {analysisResult.reviews.map((review: ReviewData, index: number) => {
                      // Now TypeScript knows what properties to expect
                      const highestSentiment = Object.entries(review)
                        .filter(([key]) => ['Positive', 'Negative', 'Neutral'].includes(key))
                        .reduce((a, b) => a[1] > b[1] ? a : b);
                        
                        const sentimentClass = 
                          highestSentiment[0] === 'Positive' ? 'border-l-green-500' :
                          highestSentiment[0] === 'Negative' ? 'border-l-red-500' : 'border-l-yellow-500';
                        
                        return (
                          <div 
                            key={index} 
                            className={`p-3 border-l-4 ${sentimentClass} rounded-r-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}
                          >
                            <div className="text-sm mb-2 line-clamp-3">{review.Text}</div>
                            <div className="flex space-x-3 text-xs text-gray-500">
                              <span>#{review["Review ID"]}</span>
                              <span className="flex items-center">
                                <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                                {Math.round(review.Positive * 100)}%
                              </span>
                              <span className="flex items-center">
                                <span className="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-1"></span>
                                {Math.round(review.Neutral * 100)}%
                              </span>
                              <span className="flex items-center">
                                <span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-1"></span>
                                {Math.round(review.Negative * 100)}%
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </ModalBody>
          
          <ModalFooter>
            <Button onClick={() => {
              if (analysisStatusInterval.current) {
                clearInterval(analysisStatusInterval.current);
              }
              setShowAnalysisModal(false);
            }}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    )}
    {selectedProductForRecs && (
      <Modal
        isOpen={!!selectedProductForRecs}
        onClose={() => {
          setSelectedProductForRecs(null);
          setProductRecommendations([]);
        }}
        size="xl"
      >
        <ModalContent>
          <ModalHeader>
            <div className="flex items-center justify-between w-full">
              <h3 className="text-lg font-medium">
                Similar Products to {selectedProductForRecs.name?.substring(0, 40)}{selectedProductForRecs.name?.length > 40 ? '...' : ''}
              </h3>
            </div>
          </ModalHeader>
          <ModalBody>
            {isLoadingRecommendations ? (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
                <p className="mt-4">Loading recommendations...</p>
              </div>
            ) : productRecommendations.length > 0 ? (
              <div className="grid grid-cols-2 gap-4">
                {productRecommendations.map((rec) => (
                  <div key={rec._id} className={`border rounded-lg overflow-hidden ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'}`}>
                    <a href={rec.url} target="_blank" rel="noopener noreferrer" className="block">
                      <div className="relative h-40">
                        <img 
                          src={rec.image} 
                          alt={rec.name} 
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300';
                          }}
                        />
                      </div>
                      <div className="p-3">
                        <h4 className={`text-sm font-medium line-clamp-2 ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}>
                          {rec.name}
                        </h4>
                        <div className="flex justify-between items-center mt-2">
                          <div className="text-sm font-bold text-indigo-500">
                            {typeof rec.price === 'string' && rec.price.includes('Rs.') 
                              ? rec.price 
                              : (typeof rec.price === 'number' 
                                ? `$${rec.price.toFixed(2)}` 
                                : `$${parseFloat(rec.price.toString().replace(/[^0-9.]/g, '')).toFixed(2) || '0.00'}`
                              )}
                          </div>
                          <div className={`text-xs px-2 py-1 rounded-full ${rec.store === 'Amazon' 
                            ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100' 
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'}`}>
                            {rec.store}
                          </div>
                        </div>
                      </div>
                    </a>
                    <div className="p-2 flex justify-center">
                      <Button 
                        size="sm"
                        className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 py-1"
                        onClick={() => handleAddScrapedToCart(rec)}
                      >
                        <ShoppingBag className="w-3 h-3 mr-1" />
                        <span className="text-xs">Add to Cart</span>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8">
                <AlertCircle className="w-12 h-12 text-amber-500" />
                <p className="mt-4">No recommendations found for this product</p>
              </div>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={() => {
              setSelectedProductForRecs(null);
              setProductRecommendations([]);
            }}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    )}  
    </div>
  );
}
