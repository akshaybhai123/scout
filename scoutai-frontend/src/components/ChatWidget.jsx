import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendMessage, getChatHistory } from '../api/scoutApi';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([
    { role: 'bot', message: 'Hi! I\'m your ScoutAI assistant. How can I help you today?', suggestions: ['Diet plan', 'Training tips', 'Injury prevention'] }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sport, setSport] = useState('cricket');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chat, isOpen]);

  const handleSend = async (text = message) => {
    if (!text.trim()) return;
    
    const userMsg = { role: 'user', message: text };
    setChat(prev => [...prev, userMsg]);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await sendMessage({ message: text, sport });
      setChat(prev => [...prev, { role: 'bot', message: response.data.reply, suggestions: response.data.suggestions }]);
    } catch (error) {
      setChat(prev => [...prev, { role: 'bot', message: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100]">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="mb-4 w-[350px] md:w-[400px] h-[550px] glass-card flex flex-col overflow-hidden shadow-2xl shadow-primary-blue/20"
          >
            {/* Header */}
            <div className="bg-primary-blue/10 p-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary-blue rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20"><path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" /><path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" /></svg>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">ScoutAI Support</h4>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-[10px] text-slate-400">AI Personal Assistant</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            {/* Chat Body */}
            <div ref={scrollRef} className="flex-grow overflow-y-auto p-4 space-y-4 scroll-smooth">
              {chat.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${
                    m.role === 'user' 
                    ? 'bg-primary-blue text-black font-medium' 
                    : 'bg-white/5 border border-white/5 text-slate-200'
                  }`}>
                    {m.message.split('\n').map((line, idx) => (
                      <p key={idx}>{line}</p>
                    ))}
                    
                    {m.role === 'bot' && m.suggestions && m.suggestions.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {m.suggestions.map((s, si) => (
                          <button 
                            key={si} 
                            onClick={() => handleSend(s)}
                            className="bg-white/10 hover:bg-white/20 border border-white/10 rounded-full px-3 py-1 text-[10px] transition-colors"
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/5 text-slate-400 p-2 px-4 rounded-full text-xs animate-pulse">
                    Bot is thinking...
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10 bg-black/40">
               <div className="mb-2 flex gap-2">
                 <select 
                   value={sport} 
                   onChange={(e) => setSport(e.target.value)}
                   className="text-[10px] bg-white/5 border border-white/10 rounded-md px-2 py-1 text-slate-400 outline-none"
                 >
                   <option value="cricket">Cricket</option>
                   <option value="badminton">Badminton</option>
                   <option value="basketball">Basketball</option>
                   <option value="football">Football</option>
                 </select>
               </div>
               <div className="flex gap-2">
                 <input
                   type="text"
                   value={message}
                   onChange={(e) => setMessage(e.target.value)}
                   onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                   placeholder="Ask about diet or drills..."
                   className="flex-grow bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm outline-none focus:border-primary-blue/30"
                 />
                 <button 
                   onClick={() => handleSend()}
                   className="w-10 h-10 bg-primary-blue rounded-xl flex items-center justify-center text-black"
                 >
                   <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                 </button>
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-16 h-16 bg-primary-blue rounded-full shadow-lg shadow-primary-blue/40 flex items-center justify-center text-black relative group"
      >
        <div className="absolute inset-0 rounded-full bg-primary-blue animate-ping opacity-20 group-hover:opacity-40 transition-opacity"></div>
        {isOpen ? (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
        ) : (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
        )}
      </motion.button>
    </div>
  );
};

export default ChatWidget;
