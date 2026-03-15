import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import ChatWidget from './ChatWidget';

const Navbar = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = React.useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Assess Performance', path: '/upload' },
    { name: 'Fitness Tracker', path: '/fitness' },
    { name: 'Compare', path: '/compare' },
    { name: 'Support', path: '/chat' },
  ];

  const closeMenu = () => setIsOpen(false);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-[60] bg-background/80 backdrop-blur-lg border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
          <Link to="/" onClick={closeMenu} className="flex items-center gap-2 group">
            <img src="/logo.png" alt="ScoutAI Logo" className="w-10 h-10 object-contain rounded-xl group-hover:rotate-12 transition-transform shadow-lg shadow-primary-blue/20" />
            <span className="text-2xl font-black tracking-tighter text-white">
              SCOUT<span className="text-primary-blue">AI</span>
            </span>
          </Link>

          {/* Desktop Nav (Horizontal) */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors hover:text-primary-blue ${
                  location.pathname === item.path ? 'text-primary-blue' : 'text-slate-400'
                }`}
              >
                {item.name}
              </Link>
            ))}
            <Link to="/upload" className="btn-primary py-2 px-5 text-sm">
              Launch Analysis
            </Link>
          </div>

          {/* Mobile menu Toggle */}
          <button 
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 text-white hover:bg-white/5 rounded-xl transition-colors"
          >
            {isOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu (Vertical Sidebar Overlay) */}
      <motion.div
        initial={false}
        animate={isOpen ? "open" : "closed"}
        className={`fixed inset-0 z-[55] md:hidden ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}
      >
        {/* Backdrop */}
        <motion.div 
          variants={{
            open: { opacity: 1 },
            closed: { opacity: 0 }
          }}
          onClick={closeMenu}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />
        
        {/* Sidebar */}
        <motion.div 
          variants={{
            open: { x: 0 },
            closed: { x: "100%" }
          }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="absolute top-0 right-0 bottom-0 w-[80%] max-w-sm bg-background border-l border-white/5 p-8 pt-28 space-y-6"
        >
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={closeMenu}
              className={`block text-2xl font-bold transition-colors ${
                location.pathname === item.path ? 'text-primary-blue' : 'text-slate-400 hover:text-white'
              }`}
            >
              {item.name}
            </Link>
          ))}
          <div className="pt-6 border-t border-white/5">
            <Link 
              to="/upload" 
              onClick={closeMenu}
              className="w-full btn-primary py-4 text-center block"
            >
              Launch Analysis
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-20 px-4 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>
      <footer className="py-12 border-t border-white/5 bg-black/20">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <img src="/logo.png" alt="ScoutAI Logo" className="w-8 h-8 object-contain rounded-lg shadow-md shadow-primary-blue/10" />
            <span className="text-lg font-bold text-white tracking-tighter">
              SCOUT<span className="text-primary-blue">AI</span>
            </span>
          </div>
          <p className="text-slate-500 text-sm">
            © 2026 ScoutAI. Democratizing sports talent assessment.
          </p>
          <div className="flex gap-6">
             <a href="#" className="text-slate-500 hover:text-white transition-colors">Privacy</a>
             <a href="#" className="text-slate-500 hover:text-white transition-colors">Terms</a>
             <a href="#" className="text-slate-500 hover:text-white transition-colors">Safety</a>
          </div>
        </div>
      </footer>
      <ChatWidget />
    </div>
  );
};

export default Layout;
