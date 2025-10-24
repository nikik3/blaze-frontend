import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    mobile: '',
    college: '',
    team: 'team1'
  });
  const [message, setMessage] = useState({ text: '', type: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.mobile) {
      setMessage({ text: 'Please fill all required fields!', type: 'error' });
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage({ text: 'Please enter a valid email!', type: 'error' });
      return;
    }

    const mobileRegex = /^[0-9]{10}$/;
    if (!mobileRegex.test(formData.mobile)) {
      setMessage({ text: 'Please enter a valid 10-digit mobile number!', type: 'error' });
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/register_external`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          text: `Successfully registered! Your player ID: ${data.rfid}`, 
          type: 'success' 
        });
      
        setFormData({
          name: '',
          email: '',
          mobile: '',
          college: '',
          team: 'team1'
        });

        // Auto-redirect after 3 seconds
        setTimeout(() => {
          window.location.href = '/';
        }, 3000);
      } else {
        setMessage({ text: data.error || 'Registration failed!', type: 'error' });
      }
    } catch (error) {
      setMessage({ text: 'Network error! Please try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-6"
      style={{
        backgroundImage: 'url(https://preview.redd.it/alice-in-borderland-phone-background-v0-1g48igjr72df1.jpeg?width=640&crop=smart&auto=webp&s=860967c3dd45983638e64aee253a1cdcd224d6c4)',
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      <div className="absolute inset-0 bg-black/70" />
      
      <motion.a
        href="/"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed top-8 left-8 z-50 bg-blue-900 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-full shadow-lg flex items-center gap-2"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>BACK</span>
      </motion.a>

      <motion.div 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="bg-black/80 backdrop-blur-md border-4 border-blue-600 rounded-2xl p-8 shadow-[0_0_50px_rgba(0,255,200,0.5)]">
          
          <h1 className="text-4xl font-black text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-green-500 mb-2">
            ⚡ BLAZE ⚡
          </h1>
          <h2 className="text-xl font-bold text-center text-white mb-6">
            EXTERNAL REGISTRATION
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-2">
                Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter your name"
                className="w-full p-3 bg-black/50 border-2 border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-300 mb-2">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
                className="w-full p-3 bg-black/50 border-2 border-gray-700 rounded-lg text-white focus:border-red-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-300 mb-2">
                Mobile Number *
              </label>
              <input
                type="tel"
                name="mobile"
                value={formData.mobile}
                onChange={handleChange}
                placeholder="10-digit mobile number"
                maxLength="10"
                pattern="[0-9]{10}"
                className="w-full p-3 bg-black/50 border-2 border-gray-700 rounded-lg text-white focus:border-red-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-300 mb-2">
                College/Institution (Optional)
              </label>
              <input
                type="text"
                name="college"
                value={formData.college}
                onChange={handleChange}
                placeholder="Your college name"
                className="w-full p-3 bg-black/50 border-2 border-gray-700 rounded-lg text-white focus:border-red-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-300 mb-2">
                Select Team *
              </label>
              <select
                name="team"
                value={formData.team}
                onChange={handleChange}
                className="w-full p-3 bg-black/50 border-2 border-gray-700 rounded-lg text-white focus:border-red-500 focus:outline-none"
                required
              >
                <option value="team1">♥️ TEAM HEARTS</option>
                <option value="team2">♠️ TEAM SPADES</option>
              </select>
            </div>

            {message.text && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg text-center font-bold ${
                  message.type === 'success' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-red-600 text-white'
                }`}
              >
                {message.text}
              </motion.div>
            )}

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`w-full py-3 rounded-lg font-bold text-white text-lg ${
                loading 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-blue-600 to-green-600 hover:from-red-700 hover:to-yellow-700 shadow-[0_0_20px_rgba(255,0,0,0.5)]'
              }`}
            >
              {loading ? 'REGISTERING...' : '⚡ REGISTER ⚡'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default RegistrationForm;