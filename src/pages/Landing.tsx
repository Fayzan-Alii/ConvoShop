import { motion, useScroll, useTransform } from 'framer-motion';
import { MessageSquare, ShoppingBag, Bell, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { WaveBackground } from '@/components/background/WaveBackground';
import { useTheme } from '@/lib/ThemeContext';

export function Landing() {
  const { theme } = useTheme();
  const { scrollYProgress } = useScroll();
  
  // Parallax effect for sections
  const titleOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0.8]);
  const titleY = useTransform(scrollYProgress, [0, 0.2], [0, -50]);
  const featuresY = useTransform(scrollYProgress, [0.2, 0.4], [50, 0]);
  const featuresOpacity = useTransform(scrollYProgress, [0.2, 0.4], [0, 1]);

  // Regular text without effects
  const RegularText = ({ children, delay = 0 }: { children: string, delay?: number }) => (
    <span className="regular-text">
      {children.split('').map((char, index) => (
        <motion.span 
          key={index}
          className="inline-block"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + index * 0.03 }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </span>
  );

  // Special neon effect for ConvoShop
  const BrandText = ({ children, delay = 0 }: { children: string, delay?: number }) => (
    <span className="neon-brand">
      {children.split('').map((char, index) => (
        <motion.span 
          key={index}
          className={`inline-block ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + index * 0.03 }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </span>
  );

  return (
    <div className={`min-h-screen overflow-hidden ${theme === 'dark' ? 'bg-gradient-to-br from-gray-900 to-indigo-950' : 'bg-gradient-to-br from-slate-50 to-indigo-50'}`}>
      <WaveBackground />

      <div className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pt-32">
          <motion.div 
            className="flex flex-col items-center text-center"
            style={{ opacity: titleOpacity, y: titleY }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="max-w-3xl"
            >
              <motion.h1 
                className={`text-7xl font-bold mb-6 relative ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <motion.span
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <RegularText delay={0.2}>Shop Smarter with</RegularText>
                </motion.span>
                <motion.span 
                  className={`gradient-text block ${theme === 'dark' ? 'dark-gradient-text' : ''}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                > 
                  <BrandText delay={0.4}>ConvoShop</BrandText>
                </motion.span>
              </motion.h1>
              <motion.p 
                className={`text-xl ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} mb-8`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
              >
                <RegularText delay={0.6}>Your AI-powered shopping assistant that makes finding the perfect products as easy as having a conversation.</RegularText>
              </motion.p>
              <motion.div 
                className="flex gap-4 justify-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
              >
                <Link to="/chat">
                  <motion.button
                    whileHover={{ 
                      scale: 1.05,
                      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                    }}
                    whileTap={{ 
                      scale: 0.95,
                      backgroundColor: theme === 'dark' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(79, 70, 229, 0.2)'
                    }}
                    className="chat-gradient text-white px-8 py-4 rounded-2xl font-medium flex items-center gap-2 shadow-lg shadow-indigo-500/30 dark:shadow-indigo-900/30"
                  >
                    Start Shopping <ArrowRight className="w-5 h-5" />
                  </motion.button>
                </Link>
                <motion.button
                  whileHover={{ 
                    scale: 1.05,
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                  }}
                  whileTap={{ 
                    scale: 0.95,
                    backgroundColor: theme === 'dark' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(79, 70, 229, 0.2)'
                  }}
                  className={`glass-effect px-8 py-4 rounded-2xl font-medium ${theme === 'dark' ? 'text-indigo-400' : 'text-indigo-600'} ring-2 ring-indigo-400`}
                >
                  Learn More
                </motion.button>
              </motion.div>
            </motion.div>
          </motion.div>

          <motion.div
            style={{ opacity: featuresOpacity, y: featuresY }}
            className="mt-32"
          >
            <h2 className={`text-4xl font-bold text-center mb-12 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              Why Choose <span className="neon-brand">ConvoShop</span>?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 * index }}
                  whileHover={{ 
                    y: -10,
                    scale: 1.02,
                    transition: { duration: 0.2 }
                  }}
                  className="glass-effect p-8 rounded-2xl relative overflow-hidden group backdrop-blur-lg"
                >
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-r ${theme === 'dark' ? 'from-indigo-600/10 to-purple-600/10' : 'from-indigo-500/10 to-purple-500/10'} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
                  />
                  <feature.icon className={`w-12 h-12 ${theme === 'dark' ? 'text-indigo-400' : 'text-indigo-600'} mb-4 relative z-10`} />
                  <h3 className={`text-xl font-semibold mb-2 relative z-10 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    <RegularText>{feature.title}</RegularText>
                  </h3>
                  <p className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} relative z-10`}>{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

const features = [
  {
    icon: MessageSquare,
    title: "Natural Conversations",
    description: "Shop through natural conversations with our AI assistant that understands your needs perfectly."
  },
  {
    icon: ShoppingBag,
    title: "Smart Recommendations",
    description: "Get personalized product recommendations based on your preferences and shopping history."
  },
  {
    icon: Bell,
    title: "Price Alerts",
    description: "Never miss a deal with smart price tracking and instant notifications on your favorite items."
  }
];