import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { Sparkles, FileText, Bookmark, Settings, ArrowRight, UserCheck, MapPin, Briefcase } from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 relative min-h-[85vh] text-left">
      {/* Background neon elements */}
      <div className="absolute top-1/4 left-1/3 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[130px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>

      <div className="space-y-8">
        {/* Header section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-zinc-200 pb-6">
          <div>
            <h1 className="text-3xl font-black text-text tracking-tight flex items-center gap-2 font-display">
              <Sparkles className="h-6 w-6 text-primary" />
              Candidate Dashboard
            </h1>
            <p className="text-muted text-sm mt-1.5 font-semibold">
              Manage your resumes, check matching recommendations, and trace career reports.
            </p>
          </div>
          <Link
            to="/upload"
            className="px-6 py-3.5 btn-primary rounded-xl flex items-center space-x-2 shadow-md"
          >
            <span>Scan New Resume</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Stats Widget */}
          <div className="lg:col-span-1 grid grid-cols-2 gap-4">
            <div className="p-5 rounded-3xl bg-card border border-white/5 shadow-lg flex flex-col justify-between space-y-4">
              <div className="w-10 h-10 bg-primary/20 border border-primary/40 rounded-xl flex items-center justify-center text-primary">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <span className="text-[28px] font-black text-white block leading-none">{user.resume_count || 0}</span>
                <span className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block mt-1.5">Resumes Scanned</span>
              </div>
            </div>

            <div className="p-5 rounded-3xl bg-card border border-white/5 shadow-lg flex flex-col justify-between space-y-4">
              <div className="w-10 h-10 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-emerald-400">
                <Bookmark className="h-5 w-5" />
              </div>
              <div>
                <span className="text-[28px] font-black text-white block leading-none">{user.saved_jobs_count || 0}</span>
                <span className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block mt-1.5">Saved Jobs</span>
              </div>
            </div>

            <Link
              to="/history"
              className="col-span-2 p-5 rounded-3xl bg-card border border-white/5 hover:border-white/10 transition-all flex items-center justify-between shadow-lg group cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center text-zinc-300 group-hover:bg-primary/20 group-hover:text-primary transition-all">
                  <UserCheck className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-extrabold text-white text-xs uppercase tracking-wider font-display">History Logs</h4>
                  <p className="text-[10px] text-zinc-400 font-semibold mt-0.5">View mock interviews and match metrics</p>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-zinc-400 group-hover:text-primary transition-colors" />
            </Link>
          </div>

          {/* Detailed Profile Info */}
          <div className="lg:col-span-2 p-6 rounded-3xl bg-card border border-white/5 shadow-lg space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-extrabold text-white tracking-tight font-display">{user.name || 'Anonymous Candidate'}</h2>
                  <p className="text-zinc-400 text-xs font-semibold">{user.email}</p>
                </div>
                <Link
                  to="/settings"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-300 hover:text-white transition-all cursor-pointer"
                  title="Configure Profile"
                >
                  <Settings className="h-4 w-4" />
                </Link>
              </div>

              {/* Badges/Details row */}
              <div className="flex flex-wrap gap-4 text-xs font-semibold text-zinc-300">
                <div className="flex items-center space-x-1.5">
                  <MapPin className="h-4 w-4 text-primary" />
                  <span>{user.location || 'Location Not Specified'}</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <Briefcase className="h-4 w-4 text-primary" />
                  <span>{user.experience ? `${user.experience} Experience` : 'Experience Not Specified'}</span>
                </div>
              </div>

              {/* Skills Deck */}
              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Primary Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {user.skills && user.skills.length > 0 ? (
                    user.skills.map((skill, index) => (
                      <span key={index} className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-white/5 border border-white/10 text-white rounded-lg">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-zinc-400 italic">No skills registered yet. Scan a resume to populate this section.</span>
                  )}
                </div>
              </div>

              {/* Target Roles Deck */}
              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Preferred Roles</span>
                <div className="flex flex-wrap gap-1.5">
                  {user.preferred_roles && user.preferred_roles.length > 0 ? (
                    user.preferred_roles.map((role, index) => (
                      <span key={index} className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-primary/20 border border-primary/40 text-white rounded-lg">
                        {role}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-zinc-400 italic">No preferred roles registered yet.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="border-t border-white/5 pt-4 flex justify-between items-center text-[10px] text-zinc-400 font-bold uppercase tracking-widest">
              <span>Account ID: #{user.id}</span>
              <span>Active Session</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
