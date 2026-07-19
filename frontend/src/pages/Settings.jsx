import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { Sparkles, Save, User, MapPin, Briefcase, Plus, X, ShieldAlert, Cpu } from 'lucide-react';
import * as api from '../services/api';

export default function Settings() {
  const { user, refreshUser } = useAuth();
  
  if (!user) return null;

  // Profile States
  const [name, setName] = useState(user.name || '');
  const [location, setLocation] = useState(user.location || '');
  const [experience, setExperience] = useState(user.experience || '');
  const [skills, setSkills] = useState(user.skills || []);
  const [newSkill, setNewSkill] = useState('');
  const [preferredRoles, setPreferredRoles] = useState(user.preferred_roles || []);
  const [newRole, setNewRole] = useState('');

  // API Preferences States
  const [groqModel, setGroqModel] = useState(user.api_preferences?.groq_model || 'llama-3.3-70b-versatile');
  const [jobCountry, setJobCountry] = useState(user.api_preferences?.job_country || 'India');
  const [targetCount, setTargetCount] = useState(user.api_preferences?.target_count || 10);

  const [savingProfile, setSavingProfile] = useState(false);
  const [savingApi, setSavingApi] = useState(false);
  const [profileMessage, setProfileMessage] = useState('');
  const [apiMessage, setApiMessage] = useState('');

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMessage('');
    try {
      await api.updateProfile({
        name,
        location,
        experience,
        skills,
        preferred_roles: preferredRoles
      });
      await refreshUser();
      setProfileMessage('Profile settings saved successfully.');
    } catch (err) {
      console.error(err);
      setProfileMessage('Failed to update profile details.');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleUpdateApiSettings = async (e) => {
    e.preventDefault();
    setSavingApi(true);
    setApiMessage('');
    try {
      await api.updateProfile({
        api_preferences: {
          groq_model: groqModel,
          job_country: jobCountry,
          target_count: parseInt(targetCount, 10)
        }
      });
      await refreshUser();
      setApiMessage('API & System settings saved successfully.');
    } catch (err) {
      console.error(err);
      setApiMessage('Failed to update API settings.');
    } finally {
      setSavingApi(false);
    }
  };

  const addSkill = (e) => {
    e.preventDefault();
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  const addRole = (e) => {
    e.preventDefault();
    if (newRole.trim() && !preferredRoles.includes(newRole.trim())) {
      setPreferredRoles([...preferredRoles, newRole.trim()]);
      setNewRole('');
    }
  };

  const removeRole = (roleToRemove) => {
    setPreferredRoles(preferredRoles.filter(r => r !== roleToRemove));
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 relative min-h-[85vh] text-left">
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>
      
      <div className="space-y-8">
        <div className="border-b border-zinc-200 pb-6">
          <h1 className="text-3xl font-black text-text tracking-tight flex items-center gap-2 font-display">
            <Sparkles className="h-6 w-6 text-primary" />
            Config & Settings
          </h1>
          <p className="text-muted text-sm mt-1.5 font-semibold">
            Customize your search preferences, AI modeling parameters, and profile details.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Form 1: Profile customization */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-3xl bg-card border border-white/5 shadow-lg space-y-6 flex flex-col justify-between"
          >
            <div className="space-y-4">
              <h3 className="text-md font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <User className="h-4.5 w-4.5 text-primary" />
                Candidate Profile
              </h3>
              
              {profileMessage && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${profileMessage.includes('failed') ? 'bg-red-500/10 border border-red-500/20 text-red-400' : 'bg-primary/10 border border-primary/20 text-primary'}`}>
                  {profileMessage}
                </div>
              )}

              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Display Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full pl-9 pr-4 py-2.5 bg-white/[0.02] border border-white/5 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                      placeholder="e.g. John Doe"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Location</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                      <input
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="w-full pl-9 pr-4 py-2.5 bg-white/[0.02] border border-white/5 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                        placeholder="e.g. Mumbai, India"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Experience Level</label>
                    <div className="relative">
                      <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                      <select
                        value={experience}
                        onChange={(e) => setExperience(e.target.value)}
                        className="w-full pl-9 pr-4 py-2.5 bg-zinc-900 border border-white/5 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all appearance-none"
                      >
                        <option value="">Select Level</option>
                        <option value="Entry Level">Entry Level</option>
                        <option value="Mid Level">Mid Level</option>
                        <option value="Senior Level">Senior Level</option>
                        <option value="Lead">Lead</option>
                        <option value="Executive">Executive</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Skills Tags Setup */}
                <div className="space-y-2">
                  <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Skills Checklist</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      className="flex-grow px-3 py-2 bg-white/[0.02] border border-white/5 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                      placeholder="Add skill (e.g. FastAPI)"
                    />
                    <button
                      onClick={addSkill}
                      className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/10 flex items-center justify-center cursor-pointer"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {skills.map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-white/5 border border-white/10 text-white rounded-lg flex items-center gap-1">
                        {skill}
                        <button type="button" onClick={() => removeSkill(skill)} className="hover:text-red-400">
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Preferred Roles Setup */}
                <div className="space-y-2">
                  <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Preferred Roles</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newRole}
                      onChange={(e) => setNewRole(e.target.value)}
                      className="flex-grow px-3 py-2 bg-white/[0.02] border border-white/5 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                      placeholder="Add role (e.g. Backend Engineer)"
                    />
                    <button
                      onClick={addRole}
                      className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/10 flex items-center justify-center cursor-pointer"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {preferredRoles.map((role, i) => (
                      <span key={i} className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-primary/5 border border-primary/10 text-primary rounded-lg flex items-center gap-1">
                        {role}
                        <button type="button" onClick={() => removeRole(role)} className="hover:text-red-400">
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={savingProfile}
                  className="w-full py-3.5 btn-primary font-bold text-xs uppercase tracking-wider rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center space-x-1.5 shadow-md cursor-pointer disabled:opacity-50 mt-4"
                >
                  <Save className="h-4 w-4" />
                  <span>{savingProfile ? 'Saving Details...' : 'Save Profile Changes'}</span>
                </button>
              </form>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-3xl bg-card border border-white/5 shadow-lg space-y-6 flex flex-col justify-between"
          >
            <div className="space-y-4">
              <h3 className="text-md font-bold text-white uppercase tracking-wider flex items-center gap-2 font-display">
                <Cpu className="h-4.5 w-4.5 text-primary" />
                System & AI config
              </h3>

              {apiMessage && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${apiMessage.includes('failed') ? 'bg-red-500/10 border border-red-500/20 text-red-400' : 'bg-primary/20 border border-primary/40 text-white'}`}>
                  {apiMessage}
                </div>
              )}

              <form onSubmit={handleUpdateApiSettings} className="space-y-4">
                <div className="space-y-4">
                  {/* API controls */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Groq AI Inference Model</label>
                    <select
                      value={groqModel}
                      onChange={(e) => setGroqModel(e.target.value)}
                      className="w-full px-3 py-2 bg-white/[0.02] border border-white/10 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all cursor-pointer"
                    >
                      <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Recommended)</option>
                      <option value="llama-3.1-8b-instant">llama-3.1-8b-instant (Fast)</option>
                      <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Preferred Job Aggregation Location</label>
                    <input
                      type="text"
                      value={jobCountry}
                      onChange={(e) => setJobCountry(e.target.value)}
                      className="w-full px-3 py-2 bg-white/[0.02] border border-white/10 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                      placeholder="e.g. India"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 font-extrabold uppercase tracking-widest block">Query Recommendation Limit (K)</label>
                    <input
                      type="number"
                      min={3}
                      max={20}
                      value={targetCount}
                      onChange={(e) => setTargetCount(e.target.value)}
                      className="w-full px-3 py-2 bg-white/[0.02] border border-white/10 focus:border-primary/50 text-white text-xs font-semibold rounded-xl outline-none transition-all"
                      placeholder="e.g. 10"
                    />
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white/[0.01] border border-white/5 flex items-start space-x-3 text-zinc-400 text-xs">
                  <ShieldAlert className="h-5 w-5 text-yellow-400 shrink-0 mt-0.5" />
                  <p className="leading-relaxed font-sans">
                    These parameters customize client query limits and routing paths to target specific LLM architectures. Be sure to configure matching API keys inside your backend environment.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={savingApi}
                  className="w-full py-3.5 btn-primary font-bold text-xs uppercase tracking-wider rounded-xl hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center space-x-1.5 shadow-md cursor-pointer disabled:opacity-50 mt-4"
                >
                  <Save className="h-4 w-4" />
                  <span>{savingApi ? 'Saving Registry...' : 'Save System Settings'}</span>
                </button>
              </form>
            </div>
          </motion.div>
          
        </div>
      </div>
    </div>
  );
}
