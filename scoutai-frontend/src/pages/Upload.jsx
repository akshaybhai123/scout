import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import VideoUploader from '../components/VideoUploader';
import { createAthlete, uploadVideo, triggerAnalysis } from '../api/scoutApi';
import { motion } from 'framer-motion';

const Upload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sport: 'cricket',
    age: '',
    region: ''
  });
  const [isUploading, setIsUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert('Please upload a video or image');
    
    setIsUploading(true);
    try {
      // 1. Create Athlete
      const athleteRes = await createAthlete(formData);
      const athleteId = athleteRes.data.id;

      // 2. Upload Video
      const uploadData = new FormData();
      uploadData.append('file', file);
      uploadData.append('athlete_id', athleteId);
      uploadData.append('sport', formData.sport);
      
      const uploadRes = await uploadVideo(uploadData);
      const jobId = uploadRes.data.job_id;

      // 3. Trigger Analysis
      await triggerAnalysis(jobId);

      // 4. Navigate to Analysis Page
      navigate(`/analysis/${jobId}`);
    } catch (error) {
      console.error(error);
      alert('Upload failed. Check backend connection.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-12 space-y-12">
      <div className="text-center">
        <h1 className="text-5xl font-black mb-4">Start New Assessing Session</h1>
        <p className="text-slate-500">Fill in athlete details and upload performance media to begin pipeline.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="glass-card p-8 space-y-6">
          <h3 className="text-xl font-bold border-b border-white/5 pb-4">Athlete Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-500">Full Name</label>
              <input 
                type="text" 
                required
                className="input-field"
                placeholder="e.g. John Doe"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-500">Sport</label>
              <select 
                className="input-field appearance-none cursor-pointer"
                value={formData.sport}
                onChange={(e) => setFormData({...formData, sport: e.target.value})}
              >
                <option value="cricket">Cricket</option>
                <option value="badminton">Badminton</option>
                <option value="basketball">Basketball</option>
                <option value="football">Football</option>
                <option value="volleyball">Volleyball</option>
                <option value="tennis">Tennis</option>
                <option value="athletics">Athletics</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-500">Age</label>
              <input 
                type="number" 
                className="input-field"
                placeholder="e.g. 19"
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-500">Region</label>
              <input 
                type="text" 
                className="input-field"
                placeholder="e.g. New Delhi, India"
                value={formData.region}
                onChange={(e) => setFormData({...formData, region: e.target.value})}
              />
            </div>
          </div>
        </div>

        <div className="glass-card p-8">
           <h3 className="text-xl font-bold border-b border-white/5 pb-4 mb-6">Performance Media</h3>
           <VideoUploader onFileSelect={setFile} />
        </div>

        <button 
          type="submit" 
          disabled={isUploading}
          className="w-full btn-primary flex items-center justify-center gap-2 group"
        >
          {isUploading ? (
            <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
          ) : (
            <>
              Launch AI Assessment
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Upload;
