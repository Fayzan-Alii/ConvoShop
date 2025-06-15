import axios from 'axios';
import { useEffect, useState } from 'react';
import { useTheme } from '@/lib/ThemeContext';
import { useAuth } from '@/lib/AuthContext';

export function Notifications() {
  const { theme } = useTheme();
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchNotifications = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const res = await axios.get('http://localhost:8000/api/notifications', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setNotifications(res.data.notifications || []);
      } catch (e) {
        setNotifications([]);
      }
    };
    fetchNotifications();
  }, []);

  const handleRemove = async (id: number) => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await axios.delete('http://localhost:8000/api/notifications/remove', {
        params: { notification_id: id },
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications((prev) => prev.filter((n: any) => n.id !== id));
    } catch (e) {
      console.error('Failed to remove notification', e);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
        <div className="text-center">
          <h2 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            Please sign in to view your notifications
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 pt-24">
      <h2 className={`text-2xl font-bold mb-6 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
        Notifications
      </h2>

      {notifications.length === 0 ? (
        <div className="text-center py-8">
          <p className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
            No notifications yet.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map((n: any) => (
            <div
              key={n.id}
              className={`border rounded-lg p-4 flex items-center gap-4 ${
                theme === 'dark' ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white'
              }`}
            >
              <img
                src={n.image}
                alt={n.product_name}
                className="w-20 h-20 object-contain rounded"
              />
              <div className="flex-1">
                <div className="font-semibold">{n.product_name}</div>
                <div className="text-sm mt-1">
                  <span className="text-green-600 font-bold">Price dropped!</span>{' '}
                  <span className="line-through text-gray-400">{n.old_price}</span>{' '}
                  <span className="text-indigo-600 font-bold">{n.new_price}</span>
                </div>
                <div className="text-xs mt-1 text-gray-500">{n.store}</div>
                <a
                  href={n.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline text-xs"
                >
                  View Product
                </a>
              </div>
              <div className="flex flex-col items-end gap-2">
                <div className="text-xs text-gray-400">
                  {new Date(n.created_at).toLocaleString()}
                </div>
                <button
                  onClick={() => handleRemove(n.id)}
                  className="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded transition"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
