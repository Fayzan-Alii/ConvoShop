import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { motion } from 'framer-motion';
import { useTheme } from '@/lib/ThemeContext';
import { wrapTextInSpans } from '@/lib/utils';
import { useAuth } from '@/lib/AuthContext';

export function AuthForm() {
  const { theme } = useTheme();
  const { login, register, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    
    try {
      if (isSignUp) {
        await register(email, password);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setFormError(err.response?.data?.message || 'Authentication failed');
    }
  };

  // Split text into individual characters for animation
  const AnimatedTitle = ({ text }: { text: string }) => (
    <div className="inline-block">
      {text.split('').map((char, index) => (
        <motion.span
          key={index}
          className="inline-block"
          whileHover={{
            scale: 1.2,
            color: theme === 'dark' ? '#8B5CF6' : '#4F46E5',
            y: -2,
            transition: { duration: 0.2 }
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </div>
  );

  return (
    <motion.div 
      className={`w-full max-w-md p-8 space-y-6 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} rounded-xl shadow-lg profile-font`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h2 
        className={`text-3xl font-bold text-center ${theme === 'dark' ? 'text-white' : 'text-gray-900'} profile-heading`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <AnimatedTitle text={isSignUp ? 'Create Account' : 'Welcome Back'} />
      </motion.h2>
      
      {(error || formError) && (
        <motion.div 
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {error || formError}
        </motion.div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <label htmlFor="email" className={`block text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`mt-1 block w-full rounded-md ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500 floating-input`}
            required
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <label htmlFor="password" className={`block text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`mt-1 block w-full rounded-md ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500 floating-input`}
            required
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-500"
            disabled={loading}
          >
            {loading ? 'Loading...' : isSignUp ? 'Sign Up' : 'Sign In'}
          </Button>
        </motion.div>
      </form>
      <motion.div 
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className={`text-sm ${theme === 'dark' ? 'text-indigo-400 hover:text-indigo-300' : 'text-indigo-600 hover:text-indigo-500'}`}
        >
          {wrapTextInSpans(isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up")}
        </button>
      </motion.div>
    </motion.div>
  );
}