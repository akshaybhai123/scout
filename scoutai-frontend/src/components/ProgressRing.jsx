import React from 'react';
import { motion } from 'framer-motion';

const ProgressRing = ({ progress, size = 120, strokeWidth = 8, label = "" }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center gap-4">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-white/5"
        />
        {/* Progress Circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
          strokeLinecap="round"
          fill="transparent"
          className="text-primary-blue drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]"
        />
      </svg>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
        <span className="text-3xl font-black text-white">{Math.round(progress)}%</span>
      </div>
      {label && <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>}
    </div>
  );
};

export default ProgressRing;
