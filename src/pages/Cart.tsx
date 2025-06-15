import { useEffect, useState } from 'react';
import { useTheme } from '@/lib/ThemeContext';
import { useAuth } from '@/lib/AuthContext';
import { Button } from '@/components/ui/Button';
import { Link } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import axios from 'axios';

export function Cart() {
  const { theme } = useTheme();
  const { user } = useAuth();

  const [wishlist, setWishlist] = useState([]);
  const [checkingPrices, setCheckingPrices] = useState(false);
  const [checkMsg, setCheckMsg] = useState<string | null>(null);

  useEffect(() => {
    const fetchWishlist = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const res = await axios.get('http://localhost:8000/api/wishlist', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setWishlist(res.data.wishlist || []);
      } catch (e) {
        setWishlist([]);
      }
    };
    fetchWishlist();
  }, []);

  const handleRemoveFromWishlist = async (product_url: string) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await axios.delete(`http://localhost:8000/api/wishlist/remove`, {
        params: { product_url },
        headers: { Authorization: `Bearer ${token}` },
      });
      setWishlist((prev) => prev.filter((item: any) => item.product_url !== product_url));
    } catch (e) {
      // Optionally show error or toast
    }
  };

  const handleCheckPrices = async () => {
    setCheckingPrices(true);
    setCheckMsg(null);
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await axios.post(
        'http://localhost:8000/api/wishlist/check-prices',
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCheckMsg('Price check started! You will get a notification if any price drops.');
    } catch (e) {
      setCheckMsg('Failed to start price check.');
    }
    setCheckingPrices(false);
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
        <div className="text-center">
          <h2 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            Please sign in to view your wishlist
          </h2>
          <Link to="/profile">
            <Button className="mt-4">Sign In</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 pt-24 space-y-12">
      <div>
        <h2
          className={`text-2xl font-bold mb-4 ${
            theme === 'dark' ? 'text-white' : 'text-gray-900'
          }`}
        >
          Your Wishlist
        </h2>

        <div className="flex justify-end mb-4">
          <Button
            onClick={handleCheckPrices}
            disabled={checkingPrices}
            className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-4 py-2 rounded shadow"
          >
            {checkingPrices ? 'Checking...' : 'Check Prices'}
          </Button>
        </div>

        {checkMsg && (
          <div className="text-center text-sm text-green-600 mb-2">{checkMsg}</div>
        )}

        {wishlist.length === 0 ? (
          <div className="text-center py-8">
            <p className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              Your wishlist is empty
            </p>
            <Link to="/chat">
              <Button className="mt-4 bg-gradient-to-r from-indigo-500 to-purple-500">
                Start Shopping
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {wishlist.map((item: any) => (
              <div
                key={item.product_url}
                className={`border rounded-lg p-4 ${
                  theme === 'dark' ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white'
                }`}
              >
                <img
                  src={item.image}
                  alt={item.product_name}
                  className="w-full h-40 object-contain mb-2"
                />
                <h3 className="font-semibold">{item.product_name}</h3>
                <p className="text-indigo-600">{item.price}</p>
                <p className="text-xs text-gray-500">{item.store}</p>
                <div className="mt-3 flex justify-between items-center">
                  <a
                    href={item.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 underline text-xs"
                  >
                    View Product
                  </a>
                  <Button
                    size="sm"
                    variant="destructive"
                    className="ml-2 flex items-center gap-1 bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1"
                    onClick={() => handleRemoveFromWishlist(item.product_url)}
                  >
                    <Trash2 className="w-4 h-4" />
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
