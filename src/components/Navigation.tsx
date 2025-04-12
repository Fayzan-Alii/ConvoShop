import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, ShoppingBag, User, Moon, Sun } from 'lucide-react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useTheme } from '@/lib/ThemeContext';
import { useCart } from '@/lib/CartContext';
import { useAuth } from '@/lib/AuthContext';

export function Navigation() {
  const location = useLocation();
  const { scrollY } = useScroll();
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth(); // Added `logout` from useAuth
  const { totalItems } = useCart();
  const [scrolled, setScrolled] = useState(false);

  // Transform values for scroll effects
  const opacity = useTransform(scrollY, [0, 100], [1, 0]);
  const translateY = useTransform(scrollY, [0, 100], [0, -100]);

  // Check if scrolled for mobile
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 20;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrolled]);

  const navItems = [
    {
      to: '/chat',
      icon: MessageSquare,
      label: 'Chat',
    },
    {
      to: '/profile',
      icon: User,
      label: 'Profile',
    },
    {
      to: '/cart',
      icon: ShoppingBag,
      label: 'Cart',
      badge: user ? totalItems : null,
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
              return (
                <motion.div
                  key={item.to}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                >
                  <Link to={item.to} className="relative">
                    <motion.div
                      className={`flex items-center gap-2 px-5 py-3 rounded-xl ${
                        isActive
                          ? 'text-indigo-600' // same active color in both themes
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
                          transition={{
                            type: 'spring',
                            stiffness: 200,
                            damping: 20,
                          }}
                          style={{ zIndex: 0 }}
                        />
                      )}
                      <motion.div
                        className="relative z-10 flex items-center gap-2"
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

                        {(item.badge ?? 0) > 0 && (
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

          {/* Display user info and logout button */}
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
                className="text-sm text-red-500 hover:underline"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link to="/login" className="text-sm text-blue-500 hover:underline">
              Login
            </Link>
          )}

          {/* Theme toggle button */}
          <motion.button
            onClick={toggleTheme}
            className={`p-3 rounded-full ml-2 bg-transparent`}
            whileHover={{
              scale: 1.05,
              rotate: 180,
              transition: { duration: 0.3 },
            }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 17 }}
          >
            {theme === 'dark' ? (
              // In dark mode, show Sun (for switching to light) in yellow
              <Sun className="w-5 h-5 text-yellow-300" />
            ) : (
              // In light mode, show Moon (for switching to dark) in indigo/violet
              <Moon className="w-5 h-5 text-indigo-600" />
            )}
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
}