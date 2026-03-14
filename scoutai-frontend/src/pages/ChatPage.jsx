import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { sendMessage, getSupportedSports } from '../api/scoutApi';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { role: 'bot', message: 'Hi! I\'m your ScoutAI Personal Assistant. I can help you with diet plans, training drills, and injury prevention.', suggestions: ['Cricket diet', 'Badminton warm-up', 'Basketball drills'] }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSport, setCurrentSport] = useState('cricket');
  const [sportsList, setSportsList] = useState({});
  const scrollRef = useRef(null);

  useEffect(() => {
    getSupportedSports().then(res => setSportsList(res.data));
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', message: text }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await sendMessage({ message: text, sport: currentSport });
      setMessages(prev => [...prev, { role: 'bot', message: res.data.reply, suggestions: res.data.suggestions, category: res.data.category }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', message: 'Connectivity issue with ScoutAI Engine.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col md:flex-row gap-8 py-8">
      {/* Sidebar - Context */}
      <div className="hidden md:block w-72 glass-card p-6 h-full overflow-y-auto">
        <h2 className="text-xl font-black mb-8">AI Support System</h2>
        
        <div className="space-y-8">
          <section>
            <h3 className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-4">Focus Sport</h3>
            <div className="space-y-2">
              {Object.keys(sportsList).map(s => (
                <button 
                  key={s} 
                  onClick={() => setCurrentSport(s)}
                  className={`w-full text-left p-3 rounded-xl text-sm font-bold transition-all ${
                    currentSport === s ? 'bg-primary-blue text-black' : 'hover:bg-white/5 text-slate-400'
                  }`}
                >
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </button>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-4">Popular Topics</h3>
            <div className="flex flex-wrap gap-2">
              {['Match Day Diet', 'ACL Recovery', 'Speed Drills', 'Vertical Jump'].map(topic => (
                <button key={topic} onClick={() => handleSend(topic)} className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] text-slate-300 hover:bg-white/10">{topic}</button>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-grow flex flex-col glass-card overflow-hidden">
        {/* Chat Header */}
        <div className="p-6 border-b border-white/5 flex items-center gap-4 bg-white/5">
           <div className="w-12 h-12 bg-gradient-to-br from-primary-blue to-primary-green rounded-2xl flex items-center justify-center text-black font-black">AI</div>
           <div>
              <h1 className="text-lg font-bold">ScoutAI Personal Assistant</h1>
              <p className="text-xs text-slate-500">Active context: {currentSport.toUpperCase()}</p>
           </div>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-grow overflow-y-auto p-8 space-y-6 scroll-smooth">
           {messages.map((m, i) => (
             <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
               <div className={`max-w-[75%] space-y-3 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block p-4 rounded-2xl text-base ${
                    m.role === 'user' 
                    ? 'bg-primary-blue text-black font-medium' 
                    : 'bg-white/5 border border-white/5 text-slate-200'
                  }`}>
                    {m.message.split('\n').map((line, idx) => (
                      <p key={idx} className="mb-1">{line}</p>
                    ))}
                  </div>
                  
                  {m.role === 'bot' && m.suggestions && (
                    <div className="flex flex-wrap gap-2 justify-start mt-2">
                       {m.suggestions.map(s => (
                         <button 
                          key={s} 
                          onClick={() => handleSend(s)}
                          className="px-4 py-2 bg-white/5 border border-white/10 rounded-full text-xs text-slate-400 hover:bg-primary-blue hover:text-black hover:border-primary-blue transition-all"
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
                <div className="bg-white/5 p-4 rounded-2xl text-slate-400 font-bold animate-pulse">Assistant is compiling advice...</div>
              </div>
           )}
        </div>

        {/* Chat Input */}
        <div className="p-6 border-t border-white/5 bg-black/40">
           <div className="flex gap-4">
              <input 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                className="flex-grow input-field text-lg" 
                placeholder="Ask about diet, drills, or injury prevention..." 
              />
              <button onClick={() => handleSend()} className="btn-primary flex items-center justify-center px-8">
                <span className="hidden sm:inline">Send Message</span>
                <svg className="w-5 h-5 sm:ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
              </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
