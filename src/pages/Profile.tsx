import { AuthForm } from '@/components/auth/AuthForm';
import { Button } from '@/components/ui/Button';
import { useTheme } from '@/lib/ThemeContext';
import { motion } from 'framer-motion';
import { User, Settings, Bell, Shield, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/AuthContext';

export function Profile() {
  const { theme } = useTheme();
  const { user, logout, loading } = useAuth();

  // Function to split text into individual characters for animation
  const SplitText = ({ text, className = "" }: { text: string, className?: string }) => {
    return (
      <span className={className}>
        {text.split("").map((char, index) => (
          <motion.span
            key={index}
            className="inline-block"
            initial={{ opacity: 1 }}
            whileHover={{
              scale: 1.2,
              color: theme === 'dark' ? '#8B5CF6' : '#4F46E5',
              y: -2,
              transition: { duration: 0.2 }
            }}
            animate={{ opacity: 1 }}
          >
            {char === " " ? "\u00A0" : char}
          </motion.span>
        ))}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: [0.5, 1, 0.5],
            scale: [0.98, 1.02, 0.98]
          }}
          transition={{ 
            repeat: Infinity,
            duration: 1.5
          }}
          className={`text-xl font-medium ${theme === 'dark' ? 'text-indigo-400' : 'text-indigo-600'} profile-font`}
        >
          Loading your profile...
        </motion.div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <h1 className={`text-3xl font-bold mb-2 profile-font profile-heading`}>
            <SplitText text="Welcome to ConvoShop" />
          </h1>
          <p className={`text-lg ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} profile-font`}>
            Sign in to elevate your shopping experience
          </p>
        </motion.div>
        <AuthForm />
      </div>
    );
  }

  const profileSections = [
    {
      title: "Account Information",
      icon: User,
      color: "from-indigo-500 to-purple-500",
      items: [
        { label: "Email", value: user.email },
        { label: "Member Since", value: new Date().toLocaleDateString() } // We could fetch this from the backend
      ]
    },
    {
      title: "Preferences",
      icon: Settings,
      color: "from-purple-500 to-pink-500",
      items: [
        { label: "Theme", value: theme === 'dark' ? "Dark Mode" : "Light Mode" },
        { label: "Language", value: "English" }
      ]
    },
    {
      title: "Notifications",
      icon: Bell,
      color: "from-pink-500 to-rose-500",
      items: [
        { label: "Price Alerts", value: "Enabled" },
        { label: "Deal Notifications", value: "Enabled" }
      ]
    },
    {
      title: "Privacy & Security",
      icon: Shield,
      color: "from-rose-500 to-orange-500",
      items: [
        { label: "Two-Factor Authentication", value: "Disabled" },
        { label: "Data Sharing", value: "Minimal" }
      ]
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 pt-24">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className={`text-4xl font-bold mb-2 profile-font profile-heading`}>
          <SplitText text="Welcome Back!" />
        </h1>
        <p className={`text-lg ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} profile-font`}>
          Manage your account and preferences
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {profileSections.map((section, index) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`${theme === 'dark' ? 'bg-gray-800/80' : 'bg-white/80'} backdrop-blur-lg rounded-xl shadow-lg p-6 profile-card profile-container`}
            whileHover={{ 
              y: -5,
              transition: { duration: 0.2 }
            }}
          >
            <div className="flex items-center mb-4">
              <div className={`p-3 rounded-lg bg-gradient-to-r ${section.color} mr-3`}>
                <section.icon className="w-5 h-5 text-white" />
              </div>
              <h2 className={`text-xl font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'} profile-font`}>
                <SplitText text={section.title} />
              </h2>
            </div>
            <div className="space-y-3">
              {section.items.map((item) => (
                <div key={item.label} className="flex justify-between">
                  <span className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} profile-font`}>{item.label}</span>
                  <span className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'} profile-font`}>{item.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-8 flex justify-center"
      >
        <Button
          variant="destructive"
          onClick={() => logout()}
          className="flex items-center gap-2 profile-font"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </Button>
      </motion.div>
    </div>
  );
}