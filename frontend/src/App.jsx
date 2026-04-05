import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useUserStore } from './store/userStore';
import Background from './components/Three/Background';
import Auth from './pages/auth/Auth';
import Chat from './pages/chat/Chat';
import Group from './pages/group/Group';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useUserStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const App = () => {
  return (
    <BrowserRouter>
      <div className="app">
        <Background />
        <Routes>
          <Route path="/login" element={<Auth />} />
          <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
          <Route path="/groups" element={<ProtectedRoute><Group /></ProtectedRoute>} />
          <Route path="/" element={<Navigate to="/chat" />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;