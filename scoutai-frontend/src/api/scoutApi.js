import axios from 'axios';

const API_BASE_URL = 'https://scoutai-api-1kc8.onrender.com/api';

const scoutApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Athletes
export const createAthlete = (data) => scoutApi.post('/athletes/', data);
export const getAthletes = (params) => scoutApi.get('/athletes/', { params });
export const getAthlete = (id) => scoutApi.get(`/athletes/${id}`);
export const getAthleteHistory = (id) => scoutApi.get(`/athletes/${id}/history`);
export const deleteAthlete = (id) => scoutApi.delete(`/athletes/${id}`);

// Uploads
export const uploadVideo = (formData) => {
  return scoutApi.post('/upload/video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const uploadImage = (formData) => {
  return scoutApi.post('/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Analysis
export const triggerAnalysis = (jobId) => scoutApi.post('/analysis/trigger', { job_id: jobId });
export const getJobStatus = (jobId) => scoutApi.get(`/analysis/${jobId}`);
export const getResults = (jobId) => scoutApi.get(`/analysis/${jobId}/results`);

// Reports
export const getLeaderboard = (params) => scoutApi.get('/leaderboard', { params });
export const getPdfUrl = (resultId) => `${API_BASE_URL}/reports/${resultId}/pdf`;

// Chatbot
export const sendMessage = (data) => scoutApi.post('/chatbot/message', data);
export const getChatHistory = (athleteId) => scoutApi.get(`/chatbot/history/${athleteId}`);
export const getSupportedSports = () => scoutApi.get('/chatbot/sports');

export default scoutApi;
