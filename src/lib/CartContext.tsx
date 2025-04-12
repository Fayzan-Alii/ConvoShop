import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { cartAPI } from './api';
import { useAuth } from './AuthContext';

interface CartProduct {
  _id: string;
  title: string;
  price: number;
  image_url: string;
  store: string;
}

export interface CartItem {
  _id: string;
  product: CartProduct;
  quantity: number;
}

interface CartContextType {
  cartItems: CartItem[];
  loading: boolean;
  error: string | null;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeFromCart: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  totalItems: number;
  totalPrice: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cartItems.reduce(
    (sum, item) => sum + item.product.price * item.quantity, 
    0
  );

  // Fetch cart items when user changes
  useEffect(() => {
    const fetchCartItems = async () => {
      if (!user) {
        setCartItems([]);
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        const data = await cartAPI.getCartItems();
        setCartItems(data);
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to fetch cart items');
      } finally {
        setLoading(false);
      }
    };

    fetchCartItems();
  }, [user]);

  const addToCart = async (productId: string, quantity: number = 1) => {
    if (!user) return;

    setLoading(true);
    setError(null);
    
    try {
      const newItem = await cartAPI.addToCart(productId, quantity);
      setCartItems(prev => {
        const exists = prev.find(item => item._id === newItem._id);
        if (exists) {
          return prev.map(item => 
            item._id === newItem._id ? newItem : item
          );
        }
        return [...prev, newItem];
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to add item to cart');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: string, quantity: number) => {
    if (!user || quantity < 1) return;

    setLoading(true);
    setError(null);
    
    try {
      const updatedItem = await cartAPI.updateCartItem(itemId, quantity);
      setCartItems(prev => 
        prev.map(item => item._id === itemId ? updatedItem : item)
      );
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update quantity');
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId: string) => {
    if (!user) return;

    setLoading(true);
    setError(null);
    
    try {
      await cartAPI.removeFromCart(itemId);
      setCartItems(prev => prev.filter(item => item._id !== itemId));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to remove item from cart');
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    if (!user) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all(cartItems.map(item => cartAPI.removeFromCart(item._id)));
      setCartItems([]);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to clear cart');
    } finally {
      setLoading(false);
    }
  };

  return (
    <CartContext.Provider 
      value={{ 
        cartItems, 
        loading, 
        error,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        totalItems,
        totalPrice
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
