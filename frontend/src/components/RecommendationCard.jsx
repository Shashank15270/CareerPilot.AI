import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MapPin, Briefcase, DollarSign, ExternalLink, ChevronDown, ChevronUp, Globe,
  Sparkles, CheckCircle2, AlertTriangle, Play, HelpCircle,
  UserCheck, BookOpen, Award, TrendingUp, Calendar, Send,
  RefreshCw, X, FileText, Check, ArrowRight, Bookmark
} from 'lucide-react'
import {
  getResumeReview,
  getJobAnalysis,
  getSkillGap,
  prepareInterview,
  getCareerCoach,
  saveJob,
  unsaveJob,
  getSavedJobs
} from '../services/api'

export default function RecommendationCard({ job, index }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [savedDbId, setSavedDbId] = useState(null)
  const [savingJob, setSavingJob] = useState(false)

  useEffect(() => {
    const checkSavedStatus = async () => {
      try {
        const savedList = await getSavedJobs()
        const matched = savedList.find(sj => sj.url === job.url)
        if (matched) {
          setIsSaved(true)
          setSavedDbId(matched.id)
        }
      } catch (e) {
        console.error("Error loading saved status:", e)
      }
    }
    checkSavedStatus()
  }, [job.url])

  const handleToggleSave = async (e) => {
    e.stopPropagation()
    if (savingJob) return
    setSavingJob(true)
    try {
      if (isSaved) {
        let dbIdToDelete = savedDbId
        if (!dbIdToDelete) {
          const savedList = await getSavedJobs()
          const matched = savedList.find(sj => sj.url === job.url)
          if (matched) dbIdToDelete = matched.id
        }
        if (dbIdToDelete) {
          await unsaveJob(dbIdToDelete)
          setIsSaved(false)
          setSavedDbId(null)
        }
      } else {
        const savedRecord = await saveJob(job)
        setIsSaved(true)
        setSavedDbId(savedRecord.id)
      }
    } catch (err) {
      console.error(err)
      alert("Error bookmarking job details.")
    } finally {
      setSavingJob(false)
    }
  }

  // Career Coach Panel States
  const [activePanel, setActivePanel] = useState(null) // 'review' | 'analysis' | 'gap' | 'prep' | 'coach'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [panelData, setPanelData] = useState(null)

  // Interview Prep Sub-category state
  const [prepTab, setPrepTab] = useState('technical')



  const {
    title,
    company,
    location,
    employment_type,
    salary,
    similarity_score,
    source,
    url,
    description
  } = job

  // Prefer the backend's composite match_score (skills 60% / experience 25% /
  // location 15%) over the raw embedding similarity. The composite is what the
  // ranking actually uses, so showing similarity_score made the displayed
  // number disagree with the ordering of the list.
  const matchPercentage = Math.round(
    (job.match_score ?? similarity_score ?? 0) * 100
  )

  // Determine progress bar stroke color and glowing colors
  const getProgressColor = (score) => {
    if (score >= 80) return 'stroke-green-500 text-green-400'
    if (score >= 60) return 'stroke-blue-500 text-blue-400'
    if (score >= 35) return 'stroke-indigo-500 text-indigo-400'
    return 'stroke-accent text-accent'
  }

  // SVG parameters for circular indicator
  const radius = 24
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (matchPercentage / 100) * circumference

  // Helper to open panels and request data
  const handleOpenPanel = async (panelType) => {
    setActivePanel(panelType)
    setLoading(true)
    setError('')
    setPanelData(null)

    try {
      let data = null
      if (panelType === 'review') {
        // Send the job so the ATS score reflects THIS posting.
        data = await getResumeReview({
          title: job.title,
          company: job.company,
          description: job.description,
          similarity_score: job.similarity_score ?? 0,
        })
      } else if (panelType === 'analysis') {
        data = await getJobAnalysis(job)
      } else if (panelType === 'gap') {
        data = await getSkillGap(job)
      } else if (panelType === 'prep') {
        data = await prepareInterview(job)
        // Set default prepTab based on what's available
        if (data.technical_questions && data.technical_questions.length > 0) setPrepTab('technical')
        else if (data.behavioral_questions && data.behavioral_questions.length > 0) setPrepTab('behavioral')
        else if (data.coding_questions && data.coding_questions.length > 0) setPrepTab('coding')
        else setPrepTab('hr')
      } else if (panelType === 'coach') {
        data = await getCareerCoach()
      }
      setPanelData(data)
    } catch (err) {
      console.error(err)
      const detail = err.response?.data?.detail;
      const errorMsg = typeof detail === 'string' ? detail : (Array.isArray(detail) ? detail[0]?.msg : "Failed to retrieve insights from Grok AI Career Coach. Please verify that your API key is correctly configured.");
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }



  // Close active panel
  const handleClosePanel = () => {
    setActivePanel(null)
    setPanelData(null)
    setError('')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: 'easeOut' }}
      whileHover={{ y: -4 }}
      className="rounded-2xl glass-card p-4 sm:p-6 shadow-xl relative overflow-hidden group hover:border-white/10 transition-all duration-300"
    >
      {/* Subtle top border glow */}
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6 mb-6">
        
        {/* Job Details */}
        <div className="text-left space-y-3 flex-grow">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-lg sm:text-xl font-bold text-white tracking-wide break-words group-hover:text-primary transition-colors">
                {title}
              </h3>
              <button
                onClick={handleToggleSave}
                disabled={savingJob}
                className={`p-1.5 rounded-lg border transition-all cursor-pointer ${
                  isSaved
                    ? 'bg-primary/20 border-primary/30 text-primary'
                    : 'bg-white/5 border-white/10 text-muted hover:text-white'
                }`}
                title={isSaved ? "Unsave Job" : "Save Job"}
              >
                <Bookmark className="h-4 w-4" fill={isSaved ? "currentColor" : "none"} />
              </button>
            </div>
            <p className="text-muted font-medium text-sm flex items-center space-x-1.5 mt-1">
              <span>{company}</span>
              {source && (
                <>
                  <span className="text-white/10">•</span>
                  <span className="text-xs px-2 py-0.5 bg-white/5 border border-white/10 rounded-md flex items-center gap-1 font-mono">
                    <Globe className="h-3 w-3" />
                    {source}
                  </span>
                </>
              )}
            </p>
          </div>

          {/* Metadata Badges */}
          <div className="flex flex-wrap gap-3.5 text-xs text-muted">
            {location && (
              <div className="flex items-center space-x-1.5 bg-white/[0.02] border border-white/5 px-2.5 py-1.5 rounded-lg">
                <MapPin className="h-4 w-4 text-primary" />
                <span>{location}</span>
              </div>
            )}
            {employment_type && (
              <div className="flex items-center space-x-1.5 bg-white/[0.02] border border-white/5 px-2.5 py-1.5 rounded-lg">
                <Briefcase className="h-4 w-4 text-accent" />
                <span>{employment_type}</span>
              </div>
            )}
            {salary && (
              <div className="flex items-center space-x-1.5 bg-white/[0.02] border border-white/5 px-2.5 py-1.5 rounded-lg">
                <DollarSign className="h-4 w-4 text-green-500" />
                <span>{salary}</span>
              </div>
            )}
          </div>
        </div>

        {/* Circular Progress Similarity Gauge */}
        <div className="flex-shrink-0 flex flex-col items-center">
          <div className="relative w-16 h-16">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="32"
                cy="32"
                r={radius}
                className="stroke-white/5"
                strokeWidth="4"
                fill="transparent"
              />
              <motion.circle
                cx="32"
                cy="32"
                r={radius}
                className={`transition-all duration-1000 ${getProgressColor(matchPercentage)}`}
                strokeWidth="4"
                fill="transparent"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1, delay: index * 0.08 }}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-bold text-white tracking-tighter">
                {matchPercentage}%
              </span>
            </div>
          </div>
          <span className="text-[10px] text-muted uppercase tracking-wider font-semibold mt-1.5">
            Match Score
          </span>
        </div>
      </div>

      {/* Actions and Expandable Details */}
      <div className="border-t border-white/5 pt-4 mt-4 text-left">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-1.5 text-xs text-muted hover:text-white transition-colors cursor-pointer"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                <span>Hide Description</span>
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                <span>View Details</span>
              </>
            )}
          </button>

          {url && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20 text-xs text-primary font-semibold hover:bg-primary hover:text-white transition-all duration-300"
            >
              <span>Apply Now</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden mt-3"
            >
              <div
                className="text-sm text-muted/90 leading-relaxed bg-white/[0.01] border border-white/5 p-4 rounded-xl font-sans job-description-html mb-4"
                dangerouslySetInnerHTML={{ __html: description }}
              />

              {/* Career Coach Action Buttons Group */}
              <div className="border-t border-white/5 pt-4 mt-4">
                <h4 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-primary animate-pulse" />
                  AI Career Coach Assistant
                </h4>
                <div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-2.5">
                  <button
                    onClick={() => handleOpenPanel('review')}
                    className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-primary/30 text-xs text-white hover:text-primary transition-all duration-200 cursor-pointer"
                  >
                    <FileText className="h-3.5 w-3.5 text-primary" />
                    <span>Analyze Resume</span>
                  </button>
                  <button
                    onClick={() => handleOpenPanel('analysis')}
                    className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-primary/30 text-xs text-white hover:text-primary transition-all duration-200 cursor-pointer"
                  >
                    <HelpCircle className="h-3.5 w-3.5 text-accent" />
                    <span>Why This Match?</span>
                  </button>
                  <button
                    onClick={() => handleOpenPanel('gap')}
                    className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-primary/30 text-xs text-white hover:text-primary transition-all duration-200 cursor-pointer"
                  >
                    <AlertTriangle className="h-3.5 w-3.5 text-yellow-500" />
                    <span>Skill Gap</span>
                  </button>
                  <button
                    onClick={() => handleOpenPanel('prep')}
                    className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-primary/30 text-xs text-white hover:text-primary transition-all duration-200 cursor-pointer"
                  >
                    <BookOpen className="h-3.5 w-3.5 text-green-500" />
                    <span>Prepare Interview</span>
                  </button>
                  <button
                    onClick={() => handleOpenPanel('coach')}
                    className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-primary/30 text-xs text-white hover:text-primary transition-all duration-200 cursor-pointer"
                  >
                    <TrendingUp className="h-3.5 w-3.5 text-indigo-500" />
                    <span>Career Advice</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* AI CAREER COACH INLINE PANEL */}
      <AnimatePresence>
        {activePanel && (
          <div className="mt-4 pt-4 border-t border-white/5">
            
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="relative w-full bg-white/[0.02] border border-white/10 rounded-2xl overflow-hidden flex flex-col max-h-[70vh]"
            >
              
              {/* Modal Header */}
              <div className="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-white/5 bg-white/[0.01]">
                <div className="flex items-center space-x-2 text-left">
                  <Sparkles className="h-5 w-5 text-primary animate-pulse" />
                  <div>
                    <h3 className="font-extrabold text-white tracking-wide">
                      {activePanel === 'review' && "AI Resume Review"}
                      {activePanel === 'analysis' && "AI Match Explanation"}
                      {activePanel === 'gap' && "Skill Gap Analysis"}
                      {activePanel === 'prep' && "Interview Prep Guide"}

                      {activePanel === 'coach' && "AI Career Coach Dashboard"}
                    </h3>
                    <p className="text-[10px] text-muted tracking-wider uppercase font-semibold">
                      Powered by Groq Llama 3.3
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleClosePanel}
                  className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-muted hover:text-white transition-colors cursor-pointer"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Modal Core Content Scroll Area */}
              <div className="flex-grow overflow-y-auto p-4 sm:p-6 space-y-6">
                
                {/* 1. Loading State */}
                {loading && (
                  <div className="py-20 flex flex-col items-center justify-center space-y-4">
                    <RefreshCw className="h-10 w-10 text-primary animate-spin" />
                    <div className="space-y-1 text-center">
                      <p className="text-sm font-semibold text-white">Generating AI insights...</p>
                      <p className="text-xs text-muted max-w-xs">
                        {activePanel === 'review' && "Evaluating spelling, format, and ATS metrics..."}
                        {activePanel === 'analysis' && "Comparing skill overlaps and mapping experience..."}
                        {activePanel === 'gap' && "Pinpointing resource listings and estimating learning time..."}
                        {activePanel === 'prep' && "Analyzing role requirements for deep dive technical prep..."}

                        {activePanel === 'coach' && "Building strategic roadmap milestones..."}
                      </p>
                    </div>
                  </div>
                )}

                {/* 2. Error State */}
                {error && !loading && (
                  <div className="py-12 px-6 text-center space-y-4 max-w-md mx-auto">
                    <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/25 flex items-center justify-center mx-auto text-red-400">
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-bold text-white">Something Went Wrong</h4>
                      <p className="text-xs text-muted leading-relaxed">
                        {error}
                      </p>
                    </div>
                    <button
                      onClick={() => handleOpenPanel(activePanel)}
                      className="px-4 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-xs rounded-xl shadow-lg transition-all"
                    >
                      Retry Generation
                    </button>
                  </div>
                )}

                {/* 3. Panel Data Render */}
                {!loading && !error && panelData && (
                  <div className="text-left space-y-6">
                    
                    {/* A. Resume Review Rendering */}
                    {activePanel === 'review' && (
                      <div className="space-y-6">
                        
                        {/* Scores row */}
                        <div className="grid grid-cols-1 xs:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col items-center justify-center text-center">
                            <span className="text-4xl font-extrabold text-primary mb-1">
                              {panelData.overall_score}
                            </span>
                            <span className="text-xs text-white font-semibold uppercase tracking-wider">
                              Resume Score
                            </span>
                          </div>
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col items-center justify-center text-center">
                            <span className="text-4xl font-extrabold text-accent mb-1">
                              {panelData.ats_compatibility_score}
                            </span>
                            <span className="text-xs text-white font-semibold uppercase tracking-wider">
                              ATS Match Gauge
                            </span>
                          </div>
                        </div>

                        {/* Professional Summary */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
                          <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <UserCheck className="h-4 w-4 text-primary" />
                            AI Profile Summary
                          </h4>
                          <p className="text-sm text-muted leading-relaxed">
                            {panelData.resume_summary}
                          </p>
                        </div>

                        {/* Strengths and Weaknesses */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-green-500/[0.02] border border-green-500/10 space-y-3">
                            <h4 className="text-sm font-bold text-green-400 flex items-center gap-2">
                              <CheckCircle2 className="h-4 w-4" />
                              Key Strengths
                            </h4>
                            <ul className="space-y-2 text-xs text-muted">
                              {panelData.strengths?.map((str, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-green-500 font-bold">•</span>
                                  <span>{str}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="p-5 rounded-2xl bg-red-500/[0.02] border border-red-500/10 space-y-3">
                            <h4 className="text-sm font-bold text-red-400 flex items-center gap-2">
                              <AlertTriangle className="h-4 w-4" />
                              Weaknesses
                            </h4>
                            <ul className="space-y-2 text-xs text-muted">
                              {panelData.weaknesses?.map((weak, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-red-500 font-bold">•</span>
                                  <span>{weak}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {/* Suggestions and Skill Suggestions */}
                        <div className="space-y-4">
                          <h4 className="text-xs font-bold text-white/40 uppercase tracking-widest">
                            Improvement Action Items
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Formatting & structure</h5>
                              <ul className="space-y-1.5 text-xs text-muted">
                                {panelData.formatting_suggestions?.map((item, i) => <li key={i}>• {item}</li>)}
                                {panelData.missing_sections?.map((item, i) => <li key={i} className="text-red-400">• Missing: {item}</li>)}
                              </ul>
                            </div>
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                              <h5 className="text-xs font-bold text-white uppercase tracking-wider">General suggestions</h5>
                              <ul className="space-y-1.5 text-xs text-muted">
                                {panelData.resume_improvement_suggestions?.map((item, i) => <li key={i}>• {item}</li>)}
                              </ul>
                            </div>
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Project suggestions</h5>
                              <ul className="space-y-1.5 text-xs text-muted">
                                {panelData.project_suggestions?.map((item, i) => <li key={i}>• {item}</li>)}
                              </ul>
                            </div>
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Skills suggestions</h5>
                              <ul className="space-y-1.5 text-xs text-muted font-sans">
                                <li className="font-semibold text-white/70">Technical:</li>
                                {panelData.technical_skill_suggestions?.map((item, i) => <li key={i} className="ml-2">• {item}</li>)}
                                <li className="font-semibold text-white/70 mt-2">Soft Skills:</li>
                                {panelData.soft_skill_suggestions?.map((item, i) => <li key={i} className="ml-2">• {item}</li>)}
                              </ul>
                            </div>
                          </div>
                        </div>

                      </div>
                    )}

                    {/* B. Job Match Explanation Rendering */}
                    {activePanel === 'analysis' && (
                      <div className="space-y-6">
                        
                        {/* Why Matches Text Card */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
                          <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Check className="h-4 w-4 text-green-400" />
                            Match Summary
                          </h4>
                          <p className="text-sm text-muted leading-relaxed">
                            {panelData.why_matches}
                          </p>
                        </div>

                        {/* Explanation Text */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2 font-sans">
                          <h4 className="text-sm font-bold text-white">Detailed Match Analysis</h4>
                          <p className="text-sm text-muted/90 whitespace-pre-line leading-relaxed">
                            {panelData.match_explanation}
                          </p>
                        </div>

                        {/* Overlaps grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-primary uppercase tracking-wider">Matched skills</h5>
                            <div className="flex flex-wrap gap-1.5">
                              {panelData.matched_skills?.map((item, i) => (
                                <span key={i} className="px-2 py-1 rounded bg-primary/10 border border-primary/20 text-[10px] font-semibold text-primary">
                                  {item}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-accent uppercase tracking-wider">Matched projects</h5>
                            <ul className="space-y-1 text-xs text-muted list-disc list-inside">
                              {panelData.matched_projects?.map((item, i) => <li key={i}>{item}</li>)}
                            </ul>
                          </div>
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-green-400 uppercase tracking-wider">Matched experience</h5>
                            <ul className="space-y-1 text-xs text-muted list-disc list-inside">
                              {panelData.matched_experience?.map((item, i) => <li key={i}>{item}</li>)}
                            </ul>
                          </div>
                        </div>

                        {/* Gaps in match */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-yellow-500/[0.01] border border-yellow-500/10 space-y-2.5">
                            <h5 className="text-xs font-bold text-yellow-400 uppercase tracking-wider">Missing requirements</h5>
                            <div className="flex flex-wrap gap-1.5">
                              {panelData.missing_skills?.map((item, i) => (
                                <span key={i} className="px-2 py-1 rounded bg-yellow-500/10 border border-yellow-500/20 text-[10px] font-semibold text-yellow-400">
                                  {item}
                                </span>
                              ))}
                              {panelData.missing_technologies?.map((item, i) => (
                                <span key={i} className="px-2 py-1 rounded bg-yellow-500/10 border border-yellow-500/20 text-[10px] font-semibold text-yellow-400">
                                  {item}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-white uppercase tracking-wider">Improvement & Career Advice</h5>
                            <p className="text-xs text-muted leading-relaxed">
                              {panelData.career_advice}
                            </p>
                          </div>
                        </div>

                      </div>
                    )}

                    {/* C. Skill Gap Analysis Rendering */}
                    {activePanel === 'gap' && (
                      <div className="space-y-6">
                        
                        {/* Overall stats */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col items-center justify-center text-center">
                            <span className="text-lg font-bold text-white mb-1">
                              {panelData.estimated_time_to_learn}
                            </span>
                            <span className="text-[10px] text-muted font-semibold uppercase tracking-wider">
                              Est. Prep Time
                            </span>
                          </div>
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col items-center justify-center text-center">
                            <span className="text-sm font-bold text-yellow-400 mb-1 flex items-center gap-1.5">
                              <AlertTriangle className="h-4 w-4" />
                              {panelData.missing_skills?.length || 0} gaps identified
                            </span>
                            <span className="text-[10px] text-muted font-semibold uppercase tracking-wider">
                              Skill Deficit Count
                            </span>
                          </div>
                        </div>

                        {/* Gaps List & Priority */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                            <h4 className="text-xs font-bold text-white uppercase tracking-widest">Profile vs Job Gaps</h4>
                            <div className="space-y-2.5">
                              <div>
                                <h5 className="text-[11px] font-semibold text-green-400 uppercase tracking-wider">Your matched skills</h5>
                                <div className="flex flex-wrap gap-1.5 mt-1">
                                  {panelData.current_skills?.map((item, i) => (
                                    <span key={i} className="px-2 py-0.5 rounded bg-green-500/10 border border-green-500/20 text-[10px] text-green-400">
                                      {item}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <h5 className="text-[11px] font-semibold text-yellow-400 uppercase tracking-wider">Target missing skills</h5>
                                <div className="flex flex-wrap gap-1.5 mt-1">
                                  {panelData.missing_skills?.map((item, i) => (
                                    <span key={i} className="px-2 py-0.5 rounded bg-yellow-500/10 border border-yellow-500/20 text-[10px] text-yellow-400">
                                      {item}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                            <h4 className="text-xs font-bold text-white uppercase tracking-widest">Recommended Learning Priority</h4>
                            <ol className="space-y-2 text-xs text-muted">
                              {panelData.priority_order?.map((item, i) => (
                                <li key={i} className="flex items-center space-x-2">
                                  <span className="w-5 h-5 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-[10px]">
                                    {i + 1}
                                  </span>
                                  <span className="text-white font-medium">{item}</span>
                                </li>
                              ))}
                            </ol>
                          </div>
                        </div>

                        {/* Recommended Courses Table */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                          <h4 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-1.5">
                            <BookOpen className="h-4 w-4 text-primary" />
                            Curated Courses
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="w-full min-w-[520px] text-left border-collapse text-xs">
                              <thead>
                                <tr className="border-b border-white/10 text-muted uppercase tracking-wider">
                                  <th className="py-2">Course Name</th>
                                  <th className="py-2">Platform</th>
                                  <th className="py-2">Priority</th>
                                  <th className="py-2 text-right">Duration</th>
                                </tr>
                              </thead>
                              <tbody>
                                {panelData.recommended_courses?.map((c, i) => (
                                  <tr key={i} className="border-b border-white/5 hover:bg-white/[0.01]">
                                    <td className="py-3 text-white font-medium">{c.course_name}</td>
                                    <td className="py-3 text-muted">{c.platform}</td>
                                    <td className="py-3">
                                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                                        c.priority === 'High' ? 'bg-red-500/10 text-red-400' :
                                        c.priority === 'Medium' ? 'bg-yellow-500/10 text-yellow-400' :
                                        'bg-blue-500/10 text-blue-400'
                                      }`}>
                                        {c.priority}
                                      </span>
                                    </td>
                                    <td className="py-3 text-right text-muted">{c.estimated_time}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                        {/* Recommended Certifications Table */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                          <h4 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-1.5">
                            <Award className="h-4 w-4 text-accent" />
                            Strategic Certifications
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="w-full min-w-[520px] text-left border-collapse text-xs">
                              <thead>
                                <tr className="border-b border-white/10 text-muted uppercase tracking-wider">
                                  <th className="py-2">Certification</th>
                                  <th className="py-2">Priority</th>
                                  <th className="py-2 text-right">Est. Prep Time</th>
                                </tr>
                              </thead>
                              <tbody>
                                {panelData.recommended_certifications?.map((c, i) => (
                                  <tr key={i} className="border-b border-white/5 hover:bg-white/[0.01]">
                                    <td className="py-3 text-white font-medium">{c.certification_name}</td>
                                    <td className="py-3">
                                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                                        c.priority === 'High' ? 'bg-red-500/10 text-red-400' :
                                        c.priority === 'Medium' ? 'bg-yellow-500/10 text-yellow-400' :
                                        'bg-blue-500/10 text-blue-400'
                                      }`}>
                                        {c.priority}
                                      </span>
                                    </td>
                                    <td className="py-3 text-right text-muted">{c.estimated_time}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                      </div>
                    )}

                    {/* D. Interview Preparation Guide Rendering */}
                    {activePanel === 'prep' && (
                      <div className="space-y-6">
                        
                        {/* Tab selectors for question type */}
                        <div className="flex border-b border-white/5 overflow-x-auto gap-2">
                          {['technical', 'behavioral', 'hr', 'coding', 'machine_learning', 'backend', 'sql', 'cloud'].map((tab) => {
                            const listKey = `${tab}_questions`
                            const list = panelData[listKey]
                            if (!list || list.length === 0) return null
                            return (
                              <button
                                key={tab}
                                onClick={() => setPrepTab(tab)}
                                className={`px-4 py-2 border-b-2 font-bold text-xs uppercase tracking-wider whitespace-nowrap cursor-pointer transition-colors ${
                                  prepTab === tab
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted hover:text-white'
                                }`}
                              >
                                {tab.replace('_', ' ')} ({list.length})
                              </button>
                            )
                          })}
                        </div>

                        {/* List of active questions in tab */}
                        <div className="space-y-4">
                          {panelData[`${prepTab}_questions`]?.map((q, idx) => (
                            <QuestionAccordion key={idx} q={q} idx={idx} />
                          ))}
                        </div>

                      </div>
                    )}



                    {/* F. Career Coach Advisor Panel Rendering */}
                    {activePanel === 'coach' && (
                      <div className="space-y-6">
                        
                        {/* Stats Row */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-white/50 uppercase tracking-widest">Salary Benchmark Advice</h5>
                            <p className="text-sm font-semibold text-white leading-snug">
                              {panelData.expected_salary_growth}
                            </p>
                          </div>

                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-white/50 uppercase tracking-widest">Recommended Career Progression</h5>
                            <div className="flex flex-wrap gap-1.5">
                              {panelData.next_roles?.map((role, i) => (
                                <span key={i} className="px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-bold text-indigo-400">
                                  {role}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* Interactive Career Roadmap path timeline */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                          <h4 className="text-xs font-bold text-white uppercase tracking-widest">Long Term Career Path Guidance</h4>
                          <div className="relative border-l border-white/10 pl-6 ml-2 space-y-6 my-2">
                            {panelData.career_path?.map((step, i) => (
                              <div key={i} className="relative">
                                <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-indigo-500 border-2 border-zinc-950 flex items-center justify-center">
                                  <div className="w-1.5 h-1.5 rounded-full bg-white"></div>
                                </div>
                                <span className="text-[10px] text-muted uppercase font-bold block">
                                  {i === 0 ? "Short-Term Goal (1-2 years)" : i === 1 ? "Mid-Term Goal (3-5 years)" : "Long-Term Goal (5-10 years)"}
                                </span>
                                <h5 className="font-bold text-sm text-white mt-0.5">{step}</h5>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Technologies & Certifications */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-primary uppercase tracking-widest">Technologies to adopt</h5>
                            <div className="flex flex-wrap gap-1.5">
                              {panelData.recommended_technologies?.map((tech, i) => (
                                <span key={i} className="px-2 py-0.5 bg-primary/10 border border-primary/20 rounded text-xs text-primary font-medium">
                                  {tech}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2.5">
                            <h5 className="text-xs font-bold text-accent uppercase tracking-widest">Certifications to Target</h5>
                            <div className="flex flex-wrap gap-1.5">
                              {panelData.recommended_certifications?.map((cert, i) => (
                                <span key={i} className="px-2 py-0.5 bg-accent/10 border border-accent/20 rounded text-xs text-accent font-medium">
                                  {cert}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* Recommended projects list */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                          <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest">Portfolio Project suggestions</h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {panelData.recommended_projects?.map((proj, i) => (
                              <div key={i} className="p-4 rounded-xl bg-white/[0.01] border border-white/5 space-y-2 text-left font-sans">
                                <h5 className="font-bold text-white text-sm">{proj.title}</h5>
                                <p className="text-xs text-muted leading-relaxed">{proj.description}</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {proj.technologies?.map((t, idx) => (
                                    <span key={idx} className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] text-white/70">
                                      {t}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* 90-Day Improvement Plan */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3 font-sans">
                          <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest">Strategic 90-Day Plan</h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {panelData.ninety_day_improvement_plan?.map((plan, i) => (
                              <div key={i} className="p-4 rounded-xl bg-white/[0.01] border border-white/5 space-y-2 text-left">
                                <h5 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
                                  <Calendar className="h-3.5 w-3.5 text-primary" />
                                  {plan.timeframe}
                                </h5>
                                <ul className="space-y-1.5 text-xs text-muted list-disc list-inside">
                                  {plan.actions?.map((item, idx) => <li key={idx}>{item}</li>)}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Long-term Learning Roadmap */}
                        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3 font-sans">
                          <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest">Milestone Learning Roadmap</h4>
                          <div className="space-y-3.5">
                            {panelData.learning_roadmap?.map((roadmap, i) => (
                              <div key={i} className="p-4 rounded-xl bg-black/25 border border-white/5 space-y-2 text-left">
                                <h5 className="font-bold text-sm text-white flex items-center gap-1.5">
                                  <span className="w-5 h-5 rounded-full bg-primary/20 text-primary text-[10px] flex items-center justify-center font-bold">
                                    {i+1}
                                  </span>
                                  {roadmap.phase}
                                </h5>
                                <p className="text-xs text-white/70 font-semibold pl-6">Milestone: {roadmap.milestone}</p>
                                <ul className="pl-6 space-y-1 text-xs text-muted list-disc list-inside">
                                  {roadmap.action_items?.map((item, idx) => <li key={idx}>{item}</li>)}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </div>

                      </div>
                    )}

                  </div>
                )}

              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </motion.div>
  )
}

// Sub-component for accordion-based questions prep list
function QuestionAccordion({ q, idx }) {
  const [isOpen, setIsOpen] = useState(false)
  const [showHint, setShowHint] = useState(false)

  return (
    <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 text-left transition-all duration-200">
      <div className="flex justify-between items-start gap-4">
        <div className="space-y-1">
          <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider ${
            q.difficulty === 'Easy' ? 'bg-green-500/10 text-green-400' :
            q.difficulty === 'Hard' ? 'bg-red-500/10 text-red-400' :
            'bg-yellow-500/10 text-yellow-400'
          }`}>
            {q.difficulty}
          </span>
          <h5 className="font-bold text-white text-sm leading-relaxed mt-1">
            {idx + 1}. {q.question}
          </h5>
        </div>
        <button
          onClick={() => {
            setIsOpen(!isOpen)
            setShowHint(false)
          }}
          className="p-1 rounded bg-white/5 hover:bg-white/10 text-muted hover:text-white transition-colors cursor-pointer"
        >
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden mt-3 pt-3 border-t border-white/5 space-y-3 text-xs"
          >
            {/* Expected Topics */}
            <div className="flex flex-wrap gap-1.5 items-center">
              <span className="text-[10px] text-muted font-bold uppercase tracking-wider">Topics:</span>
              {q.expected_topics?.map((t, i) => (
                <span key={i} className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] text-white/80">
                  {t}
                </span>
              ))}
            </div>

            {/* Hint toggler */}
            <div>
              {showHint ? (
                <div className="p-3 bg-yellow-500/[0.02] border border-yellow-500/10 rounded-lg text-yellow-300">
                  <span className="font-bold block mb-0.5 text-[10px] uppercase">Hint:</span>
                  <ul className="list-disc list-inside space-y-0.5">
                    {q.hints?.map((h, i) => <li key={i} className="font-sans">{h}</li>)}
                  </ul>
                </div>
              ) : (
                <button
                  onClick={() => setShowHint(true)}
                  className="px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-white font-semibold transition-colors cursor-pointer"
                >
                  Reveal Hint
                </button>
              )}
            </div>

            {/* Ideal Answer guidelines */}
            <div className="space-y-1 font-sans text-muted/90">
              <span className="font-bold text-white text-[10px] uppercase tracking-wider block">Ideal Answer Guidelines:</span>
              <p className="leading-relaxed bg-black/10 border border-white/5 p-3 rounded-lg whitespace-pre-line">
                {q.ideal_answer_guidelines}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
