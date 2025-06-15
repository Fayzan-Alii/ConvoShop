import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, ShoppingBag, User, Moon, Sun, Bell } from 'lucide-react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useTheme } from '@/lib/ThemeContext';
import { useCart } from '@/lib/CartContext';
import { useAuth } from '@/lib/AuthContext';

export function Navigation() {
  const location = useLocation();
  const { scrollY } = useScroll();
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const { totalItems } = useCart(); // kept if needed elsewhere

  const [scrolled, setScrolled] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const [hasOpenedNotifications, setHasOpenedNotifications] = useState(false);
  const [wishlistCount, setWishlistCount] = useState(0); // ✅ new state for wishlist count

  const opacity = useTransform(scrollY, [0, 100], [1, 0]);
  const translateY = useTransform(scrollY, [0, 100], [0, -100]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const fetchNotifications = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const res = await fetch('http://localhost:8000/api/notifications', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setNotificationCount(data.notifications ? data.notifications.length : 0);
      } catch {
        setNotificationCount(0);
      }
    };
    if (user) fetchNotifications();
  }, [user]);

  useEffect(() => {
    const fetchWishlistCount = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const res = await fetch('http://localhost:8000/api/wishlist', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setWishlistCount(data.wishlist ? data.wishlist.length : 0);
      } catch {
        setWishlistCount(0);
      }
    };
    if (user) fetchWishlistCount();
  }, [user]);

  const navItems = [
    { to: '/chat', icon: MessageSquare, label: 'Chat' },
    { to: '/profile', icon: User, label: 'Profile' },
    {
      to: '/notifications',
      icon: Bell,
      label: 'Notifications',
      badge: notificationCount > 0 ? notificationCount : null,
    },
    {
      to: '/cart',
      icon: ShoppingBag,
      label: 'Wishlist',
      badge: user ? wishlistCount : null, // ✅ updated
    },
  ];

  return (
    <motion.nav
      style={{ opacity, y: translateY }}
      className={`fixed top-0 left-0 right-0 ${
        theme === 'dark' ? 'bg-gray-900/90' : 'bg-white/90'
      } backdrop-blur-xl border-b ${
        theme === 'dark' ? 'border-gray-800/50' : 'border-gray-200/50'
      } py-4 px-4 z-50 transition-all duration-300`}
    >
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          <span className="neon-brand">ConvoShop</span>
        </Link>

        <div className="flex gap-3 items-center">
          <AnimatePresence mode="wait">
            {navItems.map((item) => {
              const isActive = location.pathname === item.to;
              const Icon = item.icon;
              const isBell = item.label === 'Notifications';

              const handleNavClick = () => {
                if (isBell) setHasOpenedNotifications(true);
              };

              return (
                <motion.div
                  key={item.to}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                >
                  <Link to={item.to} className="relative" onClick={handleNavClick}>
                    <motion.div
                      className={`flex items-center gap-2 px-5 py-3 rounded-xl ${
                        isActive
                          ? 'text-indigo-600'
                          : theme === 'dark'
                          ? 'text-gray-300 hover:text-indigo-600'
                          : 'text-gray-600 hover:text-indigo-600'
                      } transition-colors duration-200 shadow-lg bg-transparent`}
                      whileHover={{
                        scale: 1.03,
                        boxShadow:
                          '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.03)',
                      }}
                      whileTap={{
                        scale: 0.97,
                        backgroundColor:
                          theme === 'dark'
                            ? 'rgba(99, 102, 241, 0.2)'
                            : 'rgba(79, 70, 229, 0.2)',
                      }}
                    >
                      {isActive && (
                        <motion.div
                          className="absolute inset-0 rounded-xl bg-transparent"
                          layoutId="nav-pill"
                          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                          style={{ zIndex: 0 }}
                        />
                      )}

                      <motion.div
                        className={`relative z-10 flex items-center gap-2 ${
                          isBell && notificationCount > 0 && !hasOpenedNotifications
                            ? 'text-red-500 animate-bounce'
                            : ''
                        }`}
                        whileHover={{
                          scale: 1.05,
                          transition: { duration: 0.2 },
                        }}
                      >
                        <Icon
                          className={`w-5 h-5 ${
                            isActive
                              ? 'text-indigo-600'
                              : theme === 'dark'
                              ? 'text-gray-300'
                              : 'text-gray-600'
                          }`}
                        />
                        {item.badge && (
                          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
                            {item.badge}
                          </span>
                        )}
                        <span className={`relative z-10 font-medium ${isActive ? 'scale-105' : ''}`}>
                          {item.label}
                        </span>
                      </motion.div>
                    </motion.div>
                  </Link>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {/* User Info */}
          {user ? (
            <div className="flex items-center gap-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                <div
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl ${
                    theme === 'dark'
                      ? 'text-gray-300 hover:text-indigo-600'
                      : 'text-gray-600 hover:text-indigo-600'
                  } transition-colors duration-200 shadow-lg bg-transparent`}
                >
                  <span className="relative z-10 font-medium">
                    Welcome, {user.email.split('@')[0]}
                  </span>
                </div>
              </motion.div>
              <button
                onClick={logout}
                className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-lg shadow hover:from-pink-500 hover:to-red-500 transition-all duration-200 font-semibold"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              to="/Profile"
              className="bg-gradient-to-r from-indigo-500 to-blue-500 text-white px-4 py-2 rounded-lg shadow hover:from-blue-500 hover:to-indigo-500 transition-all duration-200 font-semibold"
            >
              Login
            </Link>
          )}

          {/* Theme toggle */}
          <motion.button
            onClick={toggleTheme}
            className="p-3 rounded-full ml-2 bg-transparent"
            whileHover={{ scale: 1.05, rotate: 180, transition: { duration: 0.3 } }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 17 }}
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-yellow-300" />
            ) : (
              <Moon className="w-5 h-5 text-indigo-600" />
            )}
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
}
