import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getLeaderboard } from '../api/scoutApi';
import { motion } from 'framer-motion';
import LeaderBoard from '../components/LeaderBoard';

const Dashboard = () => {
  return (
    <div className="space-y-12 pb-20">
      {/* Hero Section */}
      <section className="relative h-[500px] flex items-center overflow-hidden -mx-4 px-4 rounded-[40px] bg-gradient-to-br from-primary-blue/10 via-primary-green/5 to-transparent">
        <div className="max-w-2xl">
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-6xl md:text-7xl font-black leading-tight mb-6"
          >
            Assess Talent with <span className="scout-gradient-text">Computer Vision.</span>
          </motion.h1>
          <p className="text-slate-400 text-lg mb-10 max-w-lg">
            ScoutAI uses AI-powered pose estimation and object tracking to provide elite-level performance data for athletes and scouts.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link to="/upload" className="btn-primary">Start New Analysis</Link>
            <a href="#leaderboard" className="btn-secondary">View Leaderboard</a>
          </div>
        </div>
        
        <div className="absolute right-0 top-1/2 -translate-y-1/2 hidden lg:block w-1/2">
           {/* Abstract AI Visualization mockup */}
           <div className="relative animate-float">
             <div className="w-[500px] h-[300px] bg-primary-blue/5 rounded-3xl border border-primary-blue/20 flex items-center justify-center backdrop-blur-3xl overflow-hidden">
                <div className="absolute inset-0 opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
                {/* SVG Skeleton mockup */}
                <svg className="w-full h-full p-8 text-primary-blue opacity-50" viewBox="0 0 100 100">
                  <circle cx="50" cy="20" r="3" fill="currentColor" />
                  <line x1="50" y1="20" x2="50" y2="50" stroke="currentColor" strokeWidth="1" />
                  <line x1="50" y1="30" x2="30" y2="45" stroke="currentColor" strokeWidth="1" />
                  <line x1="50" y1="30" x2="70" y2="45" stroke="currentColor" strokeWidth="1" />
                  <line x1="50" y1="50" x2="35" y2="80" stroke="currentColor" strokeWidth="1" />
                  <line x1="50" y1="50" x2="65" y2="80" stroke="currentColor" strokeWidth="1" />
                </svg>
             </div>
             {/* Stats chips floating around */}
             <div className="absolute -top-4 -left-4 glass-card p-3 px-5 border-primary-green/20">
                <span className="text-primary-green font-black text-xl">24.5 km/h</span>
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Speed</p>
             </div>
             <div className="absolute -bottom-4 right-10 glass-card p-3 px-5 border-primary-blue/20">
                <span className="text-primary-blue font-black text-xl">88.2%</span>
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Efficiency</p>
             </div>
           </div>
        </div>
      </section>

      {/* Leaderboard Section */}
      <section id="leaderboard" className="space-y-6">
        <div className="flex items-end justify-between">
          <div>
            <h2 className="text-3xl font-black mb-2">Global Leaderboard</h2>
            <p className="text-slate-500">Top assessed athletes across all sports.</p>
          </div>
        </div>

        <div className="glass-card overflow-hidden">
          <LeaderBoard limit={10} />
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
