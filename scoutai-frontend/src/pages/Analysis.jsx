import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { getJobStatus } from '../api/scoutApi';
import { motion, AnimatePresence } from 'framer-motion';

const Analysis = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const queryClient = useQueryClient();
  
  useEffect(() => {
    let interval;
    const poll = async () => {
      try {
        const res = await getJobStatus(jobId);
        setStatus(res.data);
        if (res.data.status === 'complete') {
          clearInterval(interval);
          // Invalidate leaderboard to show new result immediately
          queryClient.invalidateQueries(['leaderboard']);
          setTimeout(() => navigate(`/athlete/${res.data.athlete_id}`), 2000);
        } else if (res.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (e) {
        console.error(e);
      }
    };

    poll();
    interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [jobId, navigate]);

  const stages = [
    { id: 'ingestion', label: 'Ingesting to Cloud Storage', minProgress: 0 },
    { id: 'offload', label: 'Offloading to Hugging Face AI', minProgress: 20 },
    { id: 'ai', label: 'AI Processing (YOLOv8 + Pose)', minProgress: 40 },
    { id: 'finalizing', label: 'Finalizing Evaluation', minProgress: 90 }
  ];

  if (!status) return null;

  return (
    <div className="max-w-2xl mx-auto py-20 flex flex-col items-center">
      <div className="relative w-64 h-64 mb-12">
        {/* Animated Progress Ring */}
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="128" cy="128" r="120" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-white/5" />
          <motion.circle
            cx="128"
            cy="128"
            r="120"
            stroke="currentColor"
            strokeWidth="4"
            fill="transparent"
            strokeDasharray="753.6"
            strokeDashoffset={753.6 - (753.6 * status.progress) / 100}
            className="text-primary-blue"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-6xl font-black text-white">{status.progress}%</span>
          <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest mt-1">Analyzing</span>
        </div>
      </div>

      <div className="text-center mb-16">
        <h2 className="text-3xl font-black mb-2 text-white">Pipeline in Progress</h2>
        <p className="text-slate-500">Our CV models are crunching the frames. This usually takes 30-60s.</p>
      </div>

      <div className="w-full space-y-4">
        {stages.map((stage, i) => (
          <div key={stage.id} className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
            status.progress >= stage.minProgress 
            ? 'bg-primary-blue/5 border-primary-blue/20 text-white' 
            : 'bg-white/5 border-white/5 text-slate-500'
          }`}>
             <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
               status.progress >= stage.minProgress ? 'bg-primary-blue text-black' : 'bg-white/10 text-slate-400'
             }`}>
               {status.progress >= stage.minProgress + 15 ? (
                 <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
               ) : (i + 1)}
             </div>
             <span className="font-bold flex-grow">{stage.label}</span>
             {status.progress >= stage.minProgress && status.progress < (stages[i+1]?.minProgress || 100) && (
                <div className="flex gap-1">
                  <span className="w-1 h-1 bg-primary-blue rounded-full animate-bounce"></span>
                  <span className="w-1 h-1 bg-primary-blue rounded-full animate-bounce delay-100"></span>
                  <span className="w-1 h-1 bg-primary-blue rounded-full animate-bounce delay-200"></span>
                </div>
             )}
          </div>
        ))}
      </div>

      <AnimatePresence>
        {status.status === 'failed' && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }} 
            animate={{ opacity: 1, scale: 1 }}
            className="mt-8 p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-xl w-full text-center font-bold"
          >
            Assessment Failed. Please try a shorter video or different format.
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Analysis;
