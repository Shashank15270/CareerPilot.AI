import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, LogOut, Menu, X } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  // Close the drawer on navigation, otherwise it stays open over the new page.
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  // Prevent the page behind the drawer from scrolling while it is open.
  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [menuOpen]);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  // Single source of truth so the desktop bar and the mobile drawer can never
  // drift out of sync — the previous markup only existed in the desktop bar.
  const links = user
    ? [
        { to: '/', label: 'Home' },
        { to: '/dashboard', label: 'Dashboard' },
        { to: '/upload', label: 'Scan & Recommendation' },
        { to: '/history', label: 'History Logs' },
        { to: '/settings', label: 'Config Panel' },
      ]
    : [
        { to: '/', label: 'Home' },
        { to: '/upload', label: 'Upload Resume' },
      ];

  return (
    <>
      <nav className="sticky top-0 z-50 w-full bg-background/85 backdrop-blur-md border-b border-zinc-200 px-4 sm:px-6 py-4 flex items-center justify-between gap-3">
        <Link
          to="/"
          className="flex items-center space-x-2 text-text font-black text-base sm:text-lg tracking-tight hover:opacity-90 transition-all min-w-0"
        >
          <Sparkles className="h-5 w-5 text-primary shrink-0" />
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-display truncate">
            CareerPilot.AI
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center space-x-6 text-xs font-extrabold uppercase tracking-wider">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`hover:text-primary transition-colors ${
                isActive(link.to) ? 'text-primary' : 'text-muted'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {user ? (
            <>
              <span className="text-text text-[10px] font-extrabold uppercase tracking-widest hidden lg:inline-block bg-surface border border-zinc-200 px-3 py-1.5 rounded-xl">
                Hi, {user?.name || user?.email?.split('@')[0] || 'there'}
              </span>
              <button
                onClick={handleLogout}
                className="hidden md:flex items-center space-x-1.5 px-4 py-2 bg-red-100/50 hover:bg-red-100 border border-red-200 text-red-700 text-[10px] font-extrabold uppercase tracking-wider rounded-xl transition-all cursor-pointer"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <div className="hidden sm:flex items-center gap-2 sm:gap-3">
              <Link
                to="/login"
                className="text-muted hover:text-text text-xs font-extrabold uppercase tracking-wider px-3 py-1.5 transition-colors whitespace-nowrap"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 btn-primary text-xs font-extrabold uppercase tracking-wider rounded-xl transition-all shadow-md whitespace-nowrap"
              >
                Sign Up
              </Link>
            </div>
          )}

          {/* Hamburger — the only way to reach the app on a phone */}
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="md:hidden p-2 -mr-1 rounded-xl border border-zinc-200 bg-surface text-text hover:bg-zinc-100 transition-colors cursor-pointer"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      {menuOpen && (
        <div className="md:hidden fixed inset-0 top-[65px] z-40">
          <div
            className="absolute inset-0 bg-black/20"
            onClick={() => setMenuOpen(false)}
            aria-hidden="true"
          />
          <div
            id="mobile-menu"
            className="relative bg-background border-b border-zinc-200 shadow-xl px-4 py-4 space-y-1 max-h-[calc(100dvh-65px)] overflow-y-auto"
          >
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`block px-4 py-3 rounded-xl text-sm font-extrabold uppercase tracking-wider transition-colors ${
                  isActive(link.to)
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted hover:bg-surface hover:text-text'
                }`}
              >
                {link.label}
              </Link>
            ))}

            <div className="pt-3 mt-2 border-t border-zinc-200 space-y-2">
              {user ? (
                <>
                  <div className="px-4 py-2 text-[10px] font-extrabold uppercase tracking-widest text-muted">
                    Signed in as {user?.name || user?.email?.split('@')[0] || 'there'}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-100/50 hover:bg-red-100 border border-red-200 text-red-700 text-xs font-extrabold uppercase tracking-wider rounded-xl transition-all cursor-pointer"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block w-full text-center px-4 py-3 bg-surface border border-zinc-200 text-text text-xs font-extrabold uppercase tracking-wider rounded-xl transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="block w-full text-center px-4 py-3 btn-primary text-xs font-extrabold uppercase tracking-wider rounded-xl shadow-md"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
