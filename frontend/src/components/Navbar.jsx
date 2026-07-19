import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, LogOut, User, History, Upload, Settings, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 w-full bg-background/85 backdrop-blur-md border-b border-zinc-200 px-6 py-4 flex items-center justify-between">
      <Link to="/" className="flex items-center space-x-2 text-text font-black text-lg tracking-tight hover:opacity-90 transition-all">
        <Sparkles className="h-5 w-5 text-primary" />
        <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-display">Antigravity AI</span>
      </Link>
      
      <div className="hidden md:flex items-center space-x-6 text-xs font-extrabold uppercase tracking-wider">
        <Link
          to="/"
          className={`hover:text-primary transition-colors ${
            isActive('/') ? 'text-primary' : 'text-muted'
          }`}
        >
          Home
        </Link>
        {user ? (
          <>
            <Link
              to="/dashboard"
              className={`hover:text-primary transition-colors ${
                isActive('/dashboard') ? 'text-primary' : 'text-muted'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/upload"
              className={`hover:text-primary transition-colors ${
                isActive('/upload') ? 'text-primary' : 'text-muted'
              }`}
            >
              Scan & Recommendation
            </Link>
            <Link
              to="/history"
              className={`hover:text-primary transition-colors ${
                isActive('/history') ? 'text-primary' : 'text-muted'
              }`}
            >
              History Logs
            </Link>
            <Link
              to="/settings"
              className={`hover:text-primary transition-colors ${
                isActive('/settings') ? 'text-primary' : 'text-muted'
              }`}
            >
              Config Panel
            </Link>
          </>
        ) : (
          <Link
            to="/upload"
            className="text-muted hover:text-primary transition-colors"
          >
            Upload Resume
          </Link>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {user ? (
          <div className="flex items-center space-x-3">
            <span className="text-text text-[10px] font-extrabold uppercase tracking-widest hidden lg:inline-block bg-surface border border-zinc-200 px-3 py-1.5 rounded-xl">
              Hi, {user.name || user.email.split('@')[0]}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1.5 px-4 py-2 bg-red-100/50 hover:bg-red-100 border border-red-200 text-red-700 text-[10px] font-extrabold uppercase tracking-wider rounded-xl transition-all cursor-pointer"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-3">
            <Link
              to="/login"
              className="text-muted hover:text-text text-xs font-extrabold uppercase tracking-wider px-3 py-1.5 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 btn-primary text-xs font-extrabold uppercase tracking-wider rounded-xl transition-all shadow-md"
            >
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
