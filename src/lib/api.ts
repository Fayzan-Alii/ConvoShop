import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with credentials support
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

// MongoDB Authentication API
export const userAPI = {
  // Register a new user
  register: async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/signup`, { // Updated path
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    return response.json();
  },

  // Login a user
  login: async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, { // Updated path
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      throw new Error('Login failed');
    }
    return response.json();
  },

  // Get the logged-in user's profile
  getProfile: async (token: string) => {
    const response = await fetch(`${API_URL}/auth/me`, { // Updated path
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    return response.json();
  },
};


// Product API
export const productAPI = {
  getProducts: async () => {
    const response = await api.get('/products');
    return response.data;
  },
  
  getProduct: async (id: string) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },
  
  createSampleProducts: async () => {
    const response = await api.post('/products/sample');
    return response.data;
  },
  
  // New method to create a product from scraped data
  createProduct: async (productData: {
    title: string;
    price: number;
    image_url: string;
    store: string;
    description?: string;
    category?: string;
  }) => {
    try {
      const response = await api.post('/products', productData);
      return response.data;
    } catch (error) {
      console.error('Error creating product:', error);
      // If there's an error, create a temporary product object with an ID
      // This allows the cart to still work even if the server is down
      return {
        _id: 'temp_' + Date.now(),
        ...productData,
        createdAt: new Date().toISOString(),
      };
    }
  },
  
  // Search products by keyword
  searchProducts: async (keyword: string) => {
    const response = await api.get(`/products/search?q=${encodeURIComponent(keyword)}`);
    return response.data;
  },
};

// Cart API
export const cartAPI = {
  getCartItems: async () => {
    const response = await api.get('/cart');
    return response.data;
  },
  
  addToCart: async (productId: string, quantity?: number) => {
    const response = await api.post('/cart', { productId, quantity });
    return response.data;
  },
  
  updateCartItem: async (id: string, quantity: number) => {
    const response = await api.put(`/cart/${id}`, { quantity });
    return response.data;
  },
  
  removeFromCart: async (id: string) => {
    const response = await api.delete(`/cart/${id}`);
    return response.data;
  },
  
  // New method to clear cart
  clearCart: async () => {
    const response = await api.delete('/cart');
    return response.data;
  },
};


//============================================================================================
//save chat and get chats
export const chatAPI = {
  saveChat: async (chatData: any, token: string) => {
    const response = await fetch('http://localhost:8000/api/chats/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(chatData),
    });
    if (!response.ok) {
      throw new Error('Failed to save chat');
    }
    return response.json();
  },

  getChats: async (token: string) => {
    const response = await fetch('http://localhost:8000/api/chats', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch chats');
    }
    return response.json();
  },
};
//============================================================================================

// Order API (future expansion)
export const orderAPI = {
  createOrder: async (cartItems: any[]) => {
    const response = await api.post('/orders', { items: cartItems });
    return response.data;
  },
  
  getOrders: async () => {
    const response = await api.get('/orders');
    return response.data;
  },
  
  getOrder: async (id: string) => {
    const response = await api.get(`/orders/${id}`);
    return response.data;
  },
};

export const reviewAnalysisAPI = {
  analyzeProductReviews: async (productUrl: string, store: string) => {
    try {
      const response = await axios.post(`${API_URL}/analyze-reviews`, {
        product_url: productUrl,
        store: store
      });
      return response.data;
    } catch (error) {
      console.error('Error starting review analysis:', error);
      throw error;
    }
  },
  
  checkAnalysisStatus: async () => {
    try {
      const response = await axios.get(`${API_URL}/review-analysis-status`);
      return response.data;
    } catch (error) {
      console.error('Error checking analysis status:', error);
      throw error;
    }
  }
};

export default api;