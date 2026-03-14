import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Analysis from './pages/Analysis';
import AthleteProfile from './pages/AthleteProfile';
import ChatPage from './pages/ChatPage';
import FitnessPage from './pages/FitnessPage';
import ComparePage from './pages/ComparePage';
import Layout from './components/Layout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/analysis/:jobId" element={<Analysis />} />
            <Route path="/athlete/:id" element={<AthleteProfile />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/fitness" element={<FitnessPage />} />
            <Route path="/compare" element={<ComparePage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
