import axios from 'axios';

const CHAT_API_URL = 'http://localhost:8000';

// Define interface for product data
export interface Product {
  name: string;
  price: string | number;
  image: string;
  store: string;
  url?: string;
  specifications?: string;
  stars?: string;
  ratings?: string;
}

export interface Recommendation {
  type: 'price' | 'feature' | 'specification';
  content: string;
}

export interface ChatMessage {
  role: string;
  content: string;
  products?: Product[];
  recommendations?: Recommendation[];
}

// Define interface for LangGraph message format
interface LangGraphMessage {
  type?: string;
  content?: string;
  additional_kwargs?: {
    role?: string;
    products?: Product[];
    recommendations?: Recommendation[];
    [key: string]: any;
  };
  [key: string]: any;
}

export interface ChatResponse {
  status?: number;
  headers?: any;
  data?: any;
  messages: ChatMessage[];
  output?: any;
  content?: string;
}

const chatAPI = {
  async sendMessage(message: string, threadId: string): Promise<ChatResponse> {
    try {
      console.log("Sending message to AI:", message);
      console.log("Using thread ID:", threadId);
      
      const response = await axios.post(`${CHAT_API_URL}/chat/invoke`, {
        input: {
          messages: [{ content: message, type: "human" }]
        },
        config: {
          configurable: {
            checkpoint_id: threadId || "chat_session",
            thread_id: threadId || "default_thread"
          }
        }
      });
      
      console.log("Raw API response received:", response.status);
      const responsePreview = JSON.stringify(response.data).substring(0, 300);
      console.log(`API response preview: ${responsePreview}...`);
      
      let content = "I received your message but couldn't generate a proper response.";
      let products: Product[] = [];
      let recommendations: Recommendation[] = [];
      
      // Handle LangGraph response format
      if (response.data && response.data.output && response.data.output.messages) {
        const messages = response.data.output.messages as LangGraphMessage[];
        
        // Find the most recent AI message (with proper typing)
        const aiMessages = messages.filter((msg: LangGraphMessage) => 
          (msg.type === 'ai' || msg.additional_kwargs?.role === 'assistant')
        );
        
        if (aiMessages.length > 0) {
          const lastAiMessage = aiMessages[aiMessages.length - 1];
          content = lastAiMessage.content || "";
          
          if (lastAiMessage.additional_kwargs) {
            if (lastAiMessage.additional_kwargs.products && 
                Array.isArray(lastAiMessage.additional_kwargs.products)) {
              products = lastAiMessage.additional_kwargs.products;
              console.log(`Found ${products.length} products in AI message additional_kwargs`);
            }
            
            if (lastAiMessage.additional_kwargs.recommendations && 
                Array.isArray(lastAiMessage.additional_kwargs.recommendations)) {
              recommendations = lastAiMessage.additional_kwargs.recommendations;
            }
          }
        }
      } 
      // Handle direct message response format
      else if (response.data && response.data.messages) {
        if (Array.isArray(response.data.messages)) {
          const lastMessage = response.data.messages[response.data.messages.length - 1];
          content = lastMessage.content || "";
          if (lastMessage.products && Array.isArray(lastMessage.products)) {
            products = lastMessage.products;
            console.log(`Found ${products.length} products in messages array`);
          }
          if (lastMessage.recommendations && Array.isArray(lastMessage.recommendations)) {
            recommendations = lastMessage.recommendations;
          }
        } else if (typeof response.data.messages === 'object') {
          const messagesObj = response.data.messages as any;
          content = messagesObj.content || "";
          if (messagesObj.products && Array.isArray(messagesObj.products)) {
            products = messagesObj.products;
            console.log(`Found ${products.length} products in messages object`);
          }
        }
      } else if (response.data && response.data.content) {
        content = response.data.content;
      }
      
      if (products.length > 0) {
        console.log("Sample product structure:", {
          name: products[0].name,
          price: products[0].price,
          image: products[0].image ? products[0].image.substring(0, 30) + '...' : 'undefined',
          store: products[0].store,
          url: products[0].url || 'missing'
        });
        
        products = products.map(p => ({
          ...p,
          url: p.url || (
            p.store === 'Amazon' 
              ? `https://www.amazon.com/s?k=${encodeURIComponent(p.name || '')}` 
              : p.store === 'Daraz'
                ? `https://www.daraz.pk/catalog/?q=${encodeURIComponent(p.name || '')}`
                : `https://www.google.com/search?q=${encodeURIComponent(p.name || '')}`
          )
        }));
      } else {
        console.log("No products found in response");
      }
      
      return {
        messages: [{
          role: 'assistant',
          content: content,
          products: products.length > 0 ? products : undefined,
          recommendations: recommendations.length > 0 ? recommendations : undefined
        }],
        status: response.status,
        headers: response.headers,
        data: response.data
      };
    } catch (error: any) {
      console.error('Error sending message to AI:', error);
      if (error.response) {
        console.error('Error response status:', error.response.status);
        console.error('Error response data:', error.response.data);
      }
      return {
        messages: [{
          role: 'assistant',
          content: "I'm having trouble connecting to the backend services right now. Please make sure all servers are running.",
          products: []
        }]
      };
    }
  },

  // New method: Save chat to the backend
  async saveChat(chatData: any, token: string): Promise<any> {
    const response = await axios.post(`${CHAT_API_URL}/api/chats/save`, chatData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // New method: Fetch chats from the backend
  async getChats(token: string): Promise<any> {
    const response = await axios.get(`${CHAT_API_URL}/api/chats`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

export default chatAPI;