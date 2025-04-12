import { motion } from 'framer-motion';
import { Trash2, Plus, Minus, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useTheme } from '@/lib/ThemeContext';
import { useCart } from '@/lib/CartContext';
import { useAuth } from '@/lib/AuthContext';
import { Link } from 'react-router-dom';

export function Cart() {
  const { theme } = useTheme();
  const { user } = useAuth();
  const { 
    cartItems, 
    loading, 
    updateQuantity, 
    removeFromCart,
    totalPrice 
  } = useCart();

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
        <div className="text-center">
          <h2 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            Please sign in to view your cart
          </h2>
          <Link to="/profile">
            <Button className="mt-4">
              Sign In
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Cart Items */}
        <motion.div 
          className="flex-1"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className={`${theme === 'dark' ? 'bg-gray-800/80' : 'bg-white/80'} backdrop-blur-lg rounded-2xl shadow-lg p-6`}>
            <h2 className={`text-2xl font-bold mb-6 ${theme === 'dark' ? 'text-white' : 'text-gray-900'} animated-text`}>Shopping Cart</h2>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                <p className="mt-4 text-gray-500">Loading your cart...</p>
              </div>
            ) : cartItems.length === 0 ? (
              <div className="text-center py-8">
                <p className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                  Your cart is empty
                </p>
                <Link to="/chat">
                  <Button className="mt-4 bg-gradient-to-r from-indigo-500 to-purple-500">
                    Start Shopping
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                {cartItems.map((item) => (
                  <motion.div
                    key={item._id}
                    className="flex gap-6 items-center"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    whileHover={{ scale: 1.02 }}
                  >
                    <motion.img
                      src={item.product.image_url}
                      alt={item.product.title}
                      className="w-24 h-24 object-cover rounded-xl"
                      whileHover={{ scale: 1.1 }}
                    />
                    <div className="flex-1">
                      <h3 className={`font-semibold text-lg ${theme === 'dark' ? 'text-white' : 'text-gray-900'} animated-text`}>
                        {item.product.title}
                      </h3>
                      <p className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                        ${item.product.price.toFixed(2)}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Button
                        size="sm"
                        variant="outline"
                        className={`rounded-full w-8 h-8 p-0 ${theme === 'dark' ? 'border-gray-600 text-gray-300' : ''}`}
                        onClick={() => updateQuantity(item._id, Math.max(1, item.quantity - 1))}
                      >
                        <Minus className="w-4 h-4" />
                      </Button>
                      <span className={`w-8 text-center ${theme === 'dark' ? 'text-white' : ''}`}>
                        {item.quantity}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        className={`rounded-full w-8 h-8 p-0 ${theme === 'dark' ? 'border-gray-600 text-gray-300' : ''}`}
                        onClick={() => updateQuantity(item._id, item.quantity + 1)}
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                    <Button
                      variant="outline"
                      className={`text-red-500 ${theme === 'dark' ? 'hover:bg-red-900/20 border-gray-700' : 'hover:bg-red-50'}`}
                      onClick={() => removeFromCart(item._id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Order Summary */}
        <motion.div
          className="w-full lg:w-80"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className={`${theme === 'dark' ? 'bg-gray-800/80' : 'bg-white/80'} backdrop-blur-lg rounded-2xl shadow-lg p-6`}>
            <h2 className={`text-xl font-bold mb-6 ${theme === 'dark' ? 'text-white' : 'text-gray-900'} animated-text`}>Order Summary</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>Subtotal</span>
                <span className={`font-medium ${theme === 'dark' ? 'text-white' : ''}`}>${totalPrice.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>Shipping</span>
                <span className={`font-medium ${theme === 'dark' ? 'text-white' : ''}`}>Free</span>
              </div>
              <div className={`border-t ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'} pt-4`}>
                <div className="flex justify-between">
                  <span className={`font-semibold ${theme === 'dark' ? 'text-white' : ''}`}>Total</span>
                  <span className={`font-bold ${theme === 'dark' ? 'text-white' : ''}`}>${totalPrice.toFixed(2)}</span>
                </div>
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-500"
                disabled={cartItems.length === 0 || loading}
              >
                Checkout <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}