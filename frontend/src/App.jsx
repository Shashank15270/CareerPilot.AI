import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// Pages
import Home from './pages/Home';
import Upload from './pages/Upload';
import History from './pages/History';
import Login from './pages/Login';
import Register from './pages/Register';
import Settings from './pages/Settings';
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';
import Recommendations from './pages/Recommendations';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        {/* overflow-x-hidden is a safety net: several pages use oversized
            decorative blur circles that would otherwise cause sideways scroll. */}
        <div className="min-h-screen overflow-x-hidden bg-background text-text flex flex-col justify-between selection:bg-primary selection:text-white">
          {/* Separate boundary: the Navbar renders outside <Routes>, so an error
              here would otherwise take down every page in the app. */}
          <ErrorBoundary>
            <Navbar />
          </ErrorBoundary>
          <main className="flex-grow">
            <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Scan & Recommendations can be optional or default context support */}
              <Route path="/upload" element={<Upload />} />
              
              {/* Authenticated member pages */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/history" 
                element={
                  <ProtectedRoute>
                    <History />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                } 
              />
              
              <Route path="/recommendations" element={<Recommendations />} />

              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
            </ErrorBoundary>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}
