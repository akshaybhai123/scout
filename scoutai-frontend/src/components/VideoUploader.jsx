import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

const VideoUploader = ({ onFileSelect }) => {
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0];
    if (file) {
      onFileSelect(file);
      const url = URL.createObjectURL(file);
      setPreview(url);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi'],
      'image/*': ['.jpg', '.jpeg', '.png']
    },
    maxFiles: 1
  });

  return (
    <div
      {...getRootProps()}
      className={`relative group cursor-pointer h-64 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-all ${
        isDragActive ? 'border-primary-blue bg-primary-blue/5' : 'border-white/10 hover:border-white/20'
      }`}
    >
      <input {...getInputProps()} />
      
      {preview ? (
        <div className="absolute inset-0 rounded-2xl overflow-hidden p-4">
          <video src={preview} className="w-full h-full object-cover rounded-xl" muted autoPlay loop />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="text-white font-bold">Replace File</span>
          </div>
        </div>
      ) : (
        <>
          <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <svg className="w-8 h-8 text-primary-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p className="text-white font-semibold">Drop video here or click to browse</p>
          <p className="text-slate-500 text-sm mt-1">MP4, MOV, or AVI up to 500MB</p>
        </>
      )}
    </div>
  );
};

export default VideoUploader;
