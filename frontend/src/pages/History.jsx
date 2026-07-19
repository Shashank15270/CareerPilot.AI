import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Briefcase, Trash2, Calendar, FileText, Sparkles, Clock,
  ArrowRight, Award, UserCheck, TrendingUp, RefreshCw, AlertCircle
} from 'lucide-react'
import api from '../services/api'

export default function History() {
  const [activeTab, setActiveTab] = useState('saved-jobs') // 'saved-jobs' | 'resumes' | 'recommendations' | 'interviews' | 'career-coach'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState([])
  const [selectedInterview, setSelectedInterview] = useState(null)
  const [interviewHistoryDetails, setInterviewHistoryDetails] = useState([])
  const [loadingDetails, setLoadingDetails] = useState(false)

  const tabs = [
    { id: 'saved-jobs', name: 'Saved Jobs', icon: Briefcase },
    { id: 'resumes', name: 'Resume History', icon: FileText },
    { id: 'recommendations', name: 'Recommendations', icon: Clock },
    { id: 'interviews', name: 'Mock Interviews', icon: Award },
    { id: 'career-coach', name: 'Career Reports', icon: TrendingUp },
  ]

  useEffect(() => {
    fetchHistoryData()
  }, [activeTab])

  const fetchHistoryData = async () => {
    setLoading(true)
    setError('')
    setData([])
    setSelectedInterview(null)
    setInterviewHistoryDetails([])

    try {
      let result = []
      if (activeTab === 'saved-jobs') {
        result = await api.getSavedJobs()
      } else if (activeTab === 'resumes') {
        result = await api.getResumeHistory()
      } else if (activeTab === 'recommendations') {
        result = await api.getRecommendationHistory()
      } else if (activeTab === 'interviews') {
        result = await api.getInterviewHistory()
      } else if (activeTab === 'career-coach') {
        result = await api.getCareerCoachHistory()
      }
      setData(result)
    } catch (err) {
      console.error(err)
      setError('Failed to load history data. Make sure the database is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleUnsaveJob = async (jobId) => {
    try {
      await api.unsaveJob(jobId)
      setData((prev) => prev.filter((job) => job.id !== jobId))
    } catch (err) {
      console.error(err)
      alert('Failed to unsave job.')
    }
  }

  const handleViewInterviewDetails = async (session) => {
    setSelectedInterview(session)
    setLoadingDetails(true)
    setInterviewHistoryDetails([])
    try {
      const details = await api.getInterviewHistoryDetails(session.id)
      setInterviewHistoryDetails(details)
    } catch (err) {
      console.error(err)
      alert('Failed to load interview history details.')
    } finally {
      setLoadingDetails(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    try {
      const d = new Date(dateString)
      return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (e) {
      return dateString
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-12 relative min-h-[85vh] text-left">
      {/* Glow highlight */}
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-primary/5 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>
      
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-black text-text tracking-tight flex items-center gap-2 font-display">
            <Sparkles className="h-7 w-7 text-primary" />
            History Dashboard
          </h1>
          <p className="text-muted text-sm mt-1.5 font-semibold">
            View your saved jobs, previous resume evaluations, mock interview session logs, and long-term career reports.
          </p>
        </div>

        {/* Tab Selector Nav List */}
        <div className="flex border-b border-zinc-200 overflow-x-auto gap-2 py-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-5 py-3 border-b-2 font-bold text-xs uppercase tracking-wider whitespace-nowrap cursor-pointer transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'border-primary text-primary bg-primary/10 rounded-t-xl'
                    : 'border-transparent text-muted hover:text-text hover:bg-zinc-100'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </div>

        {/* Main Content Area */}
        <div className="mt-8">
          {loading && (
            <div className="py-20 flex flex-col items-center justify-center space-y-4">
              <RefreshCw className="h-10 w-10 text-primary animate-spin" />
              <p className="text-sm font-semibold text-white/70">Fetching history from database...</p>
            </div>
          )}

          {error && !loading && (
            <div className="max-w-md mx-auto p-6 rounded-2xl bg-red-500/10 border border-red-500/25 flex flex-col items-center space-y-3 text-red-400 text-center">
              <AlertCircle className="h-8 w-8 text-red-400" />
              <h4 className="font-bold text-white">Database Error</h4>
              <p className="text-xs">{error}</p>
              <button
                onClick={fetchHistoryData}
                className="px-4 py-2 bg-red-500 text-white font-semibold text-xs rounded-xl shadow-lg hover:opacity-90 transition-all cursor-pointer"
              >
                Retry Request
              </button>
            </div>
          )}

          {!loading && !error && (
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                {/* 1. Saved Jobs Tab */}
                {activeTab === 'saved-jobs' && (
                  <div className="space-y-4">
                    {data.length === 0 ? (
                      <EmptyState message="You haven't bookmarked any jobs yet. Browse recommendations and save jobs to see them here!" />
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {data.map((job) => (
                          <div
                            key={job.id}
                            className="p-5 rounded-2xl glass-card border border-white/5 hover:border-white/10 transition-all flex flex-col justify-between"
                          >
                            <div className="space-y-2">
                              <div className="flex justify-between items-start gap-4">
                                <div>
                                  <h3 className="font-bold text-white text-base leading-snug">{job.title}</h3>
                                  <p className="text-muted text-xs font-semibold">{job.company}</p>
                                </div>
                                <button
                                  onClick={() => handleUnsaveJob(job.id)}
                                  className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500 hover:text-white transition-all cursor-pointer"
                                  title="Unsave Job"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                              <p className="text-xs text-muted/80 line-clamp-3 leading-relaxed font-sans">
                                {job.description}
                              </p>
                            </div>
                            
                            <div className="flex justify-between items-center border-t border-white/5 pt-3 mt-4 text-[10px] text-muted uppercase font-bold">
                              <span>Location: {job.location || 'N/A'}</span>
                              {job.url && (
                                <a
                                  href={job.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:underline flex items-center gap-0.5"
                                >
                                  Apply <ArrowRight className="h-3 w-3" />
                                </a>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* 2. Resume History Tab */}
                {activeTab === 'resumes' && (
                  <div className="space-y-4">
                    {data.length === 0 ? (
                      <EmptyState message="No resume upload logs found in the database. Scan a resume to store it permanently." />
                    ) : (
                      <div className="space-y-3">
                        {data.map((resume) => (
                          <div
                            key={resume.id}
                            className="p-4 rounded-xl bg-white/[0.01] border border-white/5 flex items-center justify-between gap-4 hover:bg-white/[0.02] transition-all"
                          >
                            <div className="flex items-center space-x-3.5">
                              <div className="p-2.5 rounded-lg bg-primary/10 border border-primary/20 text-primary">
                                <FileText className="h-5 w-5" />
                              </div>
                              <div>
                                <h4 className="font-semibold text-white text-sm truncate max-w-xs sm:max-w-md">
                                  {resume.file_path.substring(resume.file_path.lastIndexOf('/') + 1)}
                                </h4>
                                <p className="text-[10px] text-muted flex items-center gap-1.5 mt-0.5">
                                  <Calendar className="h-3 w-3" />
                                  Uploaded: {formatDate(resume.created_at)}
                                </p>
                              </div>
                            </div>
                            <div className="text-[10px] text-muted font-bold bg-white/5 border border-white/10 px-2.5 py-1 rounded-md uppercase font-mono">
                              DB ID: {resume.id}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Recommendations History Tab */}
                {activeTab === 'recommendations' && (
                  <div className="space-y-4">
                    {data.length === 0 ? (
                      <EmptyState message="No recommendation session logs found. Perform a search to record matching queries." />
                    ) : (
                      <div className="space-y-4">
                        {data.map((rec) => (
                          <div
                            key={rec.id}
                            className="p-5 rounded-2xl bg-white/[0.01] border border-white/5 space-y-3 hover:border-white/10 transition-all"
                          >
                            <div className="flex justify-between items-start text-xs">
                              <div>
                                <span className="text-[10px] text-muted uppercase font-bold tracking-wider">Search Keyword / Query:</span>
                                <h4 className="font-bold text-white text-sm mt-0.5">
                                  {rec.query ? `"${rec.query}"` : "All/General Recommendations"}
                                </h4>
                              </div>
                              <span className="text-muted flex items-center gap-1">
                                <Calendar className="h-3.5 w-3.5" />
                                {formatDate(rec.created_at)}
                              </span>
                            </div>

                            <div className="border-t border-white/5 pt-3">
                              <span className="text-[9px] text-muted uppercase font-bold tracking-widest block mb-2">Top matched matches:</span>
                              <div className="flex flex-wrap gap-2">
                                {rec.results_json?.slice(0, 3).map((job, idx) => (
                                  <div
                                    key={idx}
                                    className="px-2.5 py-1.5 rounded-lg bg-white/[0.02] border border-white/5 text-[11px] text-white/90"
                                  >
                                    <span className="font-semibold text-primary">{Math.round(job.similarity_score * 100)}%</span> - {job.title} ({job.company})
                                  </div>
                                ))}
                                {rec.results_json?.length > 3 && (
                                  <div className="px-2 py-1 text-[10px] text-muted font-bold flex items-center">
                                    + {rec.results_json.length - 3} more
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* 4. Mock Interviews Tab */}
                {activeTab === 'interviews' && (
                  <div className="space-y-6">
                    {data.length === 0 ? (
                      <EmptyState message="No mock interview logs found. Start a mock interview session inside job cards to record answers." />
                    ) : (
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        
                        {/* Interview Session Cards list */}
                        <div className="lg:col-span-1 space-y-3 max-h-[60vh] overflow-y-auto pr-2">
                          <span className="text-[10px] text-muted uppercase font-bold tracking-widest block mb-1">Select Interview Session:</span>
                          {data.map((session) => (
                            <div
                              key={session.id}
                              onClick={() => handleViewInterviewDetails(session)}
                              className={`p-4 rounded-2xl border text-left cursor-pointer transition-all ${
                                selectedInterview?.id === session.id
                                  ? 'bg-primary/10 border-primary/40'
                                  : 'bg-white/[0.01] border-white/5 hover:border-white/10'
                              }`}
                            >
                              <h4 className="font-bold text-white text-sm">{session.job_title}</h4>
                              <p className="text-xs text-muted/70 font-semibold">{session.job_company}</p>
                              <div className="flex justify-between items-center text-[10px] text-muted mt-3 font-semibold pt-1 border-t border-white/5">
                                <span>{session.questions_json?.length || 0} Questions</span>
                                <span className={session.completed ? 'text-green-400' : 'text-yellow-400'}>
                                  {session.completed ? 'Completed' : 'In Progress'}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Question-by-Question detailed scorecard panel */}
                        <div className="lg:col-span-2 bg-white/[0.01] border border-white/5 rounded-3xl p-6 min-h-[40vh] flex flex-col">
                          {!selectedInterview ? (
                            <div className="flex-grow flex flex-col items-center justify-center text-center text-muted p-6">
                              <Award className="h-10 w-10 text-muted/40 mb-3" />
                              <p className="text-sm font-semibold">No session selected</p>
                              <p className="text-xs max-w-xs mt-1">Click a session on the left to inspect detailed scorecard metrics.</p>
                            </div>
                          ) : (
                            <div className="space-y-6 flex-grow flex flex-col">
                              {/* Session Header */}
                              <div className="border-b border-white/5 pb-4">
                                <h3 className="text-lg font-bold text-white">Scorecard: {selectedInterview.job_title}</h3>
                                <p className="text-xs text-muted font-medium mt-0.5">{selectedInterview.job_company} • {formatDate(selectedInterview.created_at)}</p>
                              </div>

                              {loadingDetails ? (
                                <div className="flex-grow flex flex-col items-center justify-center py-10 space-y-2">
                                  <RefreshCw className="h-7 w-7 text-primary animate-spin" />
                                  <span className="text-xs text-muted">Retrieving answer scorecard details...</span>
                                </div>
                              ) : interviewHistoryDetails.length === 0 ? (
                                <div className="flex-grow flex flex-col items-center justify-center text-center text-muted py-10">
                                  <p className="text-xs">No questions have been answered in this session yet.</p>
                                </div>
                              ) : (
                                <div className="space-y-4 flex-grow overflow-y-auto max-h-[50vh] pr-2">
                                  {interviewHistoryDetails.map((historyItem, idx) => (
                                    <div
                                      key={historyItem.id}
                                      className="p-4 bg-zinc-900/60 border border-white/5 rounded-xl space-y-2.5"
                                    >
                                      <div className="flex justify-between items-start gap-4 text-xs font-bold">
                                        <span className="text-white">Q{idx + 1}: {historyItem.question}</span>
                                        <span className="px-2.5 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary text-[10px] font-extrabold font-mono">
                                          Score: {historyItem.score}/100
                                        </span>
                                      </div>
                                      <p className="text-xs text-muted font-sans italic">"Answer: {historyItem.answer}"</p>
                                      
                                      {/* Specific dimensions score metrics */}
                                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center pt-1">
                                        {[
                                          { name: "Technical", val: historyItem.evaluation_json?.technical_accuracy?.score },
                                          { name: "Communication", val: historyItem.evaluation_json?.communication?.score },
                                          { name: "Confidence", val: historyItem.evaluation_json?.confidence?.score },
                                          { name: "Completeness", val: historyItem.evaluation_json?.completeness?.score },
                                          { name: "Problem Solving", val: historyItem.evaluation_json?.problem_solving?.score }
                                        ].map((dim, i) => (
                                          <div key={i} className="p-1.5 bg-white/[0.01] border border-white/5 rounded-lg">
                                            <span className="text-[8px] text-muted uppercase font-bold block">{dim.name}</span>
                                            <span className="text-xs font-bold text-white">{dim.val || 'N/A'}</span>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                      </div>
                    )}
                  </div>
                )}

                {/* 5. Career Reports Tab */}
                {activeTab === 'career-coach' && (
                  <div className="space-y-4">
                    {data.length === 0 ? (
                      <EmptyState message="No career reports found. Generate career advice in the sidebar to cache progression plans." />
                    ) : (
                      <div className="space-y-4">
                        {data.map((report) => (
                          <div
                            key={report.id}
                            className="p-5 rounded-2xl bg-white/[0.01] border border-white/5 space-y-4 hover:border-white/10 transition-all text-left"
                          >
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-[10px] text-primary uppercase font-extrabold tracking-widest bg-primary/10 border border-primary/20 px-2.5 py-1 rounded-md flex items-center gap-1.5">
                                <Sparkles className="h-3.5 w-3.5 text-primary" />
                                AI Career Advice Roadmap
                              </span>
                              <span className="text-muted flex items-center gap-1.5">
                                <Calendar className="h-3.5 w-3.5" />
                                {formatDate(report.created_at)}
                              </span>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                              <div className="p-4 rounded-xl bg-white/[0.01] border border-white/5 space-y-2">
                                <span className="text-[9px] text-muted uppercase font-bold tracking-wider block">Target Career Path:</span>
                                <div className="space-y-1">
                                  {report.report_json?.career_path?.map((step, i) => (
                                    <div key={i} className="flex items-center space-x-2 text-xs text-white">
                                      <span className="w-4 h-4 rounded-full bg-white/5 text-[10px] font-bold flex items-center justify-center">{i+1}</span>
                                      <span>{step}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              <div className="p-4 rounded-xl bg-white/[0.01] border border-white/5 space-y-2">
                                <span className="text-[9px] text-muted uppercase font-bold tracking-wider block">Benchmark Salary Growth:</span>
                                <p className="text-xs text-muted leading-relaxed font-sans">
                                  {report.report_json?.expected_salary_growth}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  )
}

function EmptyState({ message }) {
  return (
    <div className="py-16 text-center text-muted max-w-sm mx-auto space-y-4">
      <div className="w-12 h-12 rounded-full bg-white/[0.01] border border-white/5 flex items-center justify-center mx-auto">
        <Clock className="h-5 w-5 text-primary/45" />
      </div>
      <p className="text-xs leading-relaxed max-w-xs mx-auto">
        {message}
      </p>
    </div>
  )
}
