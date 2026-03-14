import React from 'react';
import { motion } from 'framer-motion';

const ScoreCard = ({ score, grade, label }) => {
  const getGradeColor = (g) => {
    switch(g?.toLowerCase()) {
      case 'elite': return 'text-primary-green';
      case 'advanced': return 'text-primary-blue';
      case 'developing': return 'text-primary-orange';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="glass-card p-8 flex flex-col items-center justify-center text-center">
      <h3 className="text-slate-400 text-sm font-medium mb-4 uppercase tracking-widest">{label || 'Talent Score'}</h3>
      
      <div className="relative w-40 h-40">
        {/* Animated Background Ring */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-white/5"
          />
          <motion.circle
            cx="80"
            cy="80"
            r="70"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray="439.6"
            initial={{ strokeDashoffset: 439.6 }}
            animate={{ strokeDashoffset: 439.6 - (439.6 * score) / 100 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className="text-primary-blue"
          />
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-black text-white leading-none">{Math.round(score)}</span>
          <span className="text-xs text-slate-500 font-bold">/ 100</span>
        </div>
      </div>

      <div className="mt-6">
        <span className={`text-2xl font-black uppercase tracking-tighter ${getGradeColor(grade)}`}>
          {grade || 'N/A'}
        </span>
      </div>
    </div>
  );
};

export default ScoreCard;
