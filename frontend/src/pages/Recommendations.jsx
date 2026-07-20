import { useLocation, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Briefcase, ArrowLeft, Upload, FileText, Search } from 'lucide-react'
import RecommendationCard from '../components/RecommendationCard'

export default function Recommendations() {
  const location = useLocation()
  const state = location.state || {}
  const { recommendations = [], resumeName = '', query = '', topK = 10 } = state

  const hasData = recommendations && recommendations.length > 0

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 sm:py-12 relative min-h-[85vh] overflow-hidden">
      {/* Glow highlight */}
      <div className="absolute top-0 right-0 translate-x-1/3 w-[260px] h-[260px] sm:w-[400px] sm:h-[400px] bg-accent/5 rounded-full blur-[100px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>
      
      {/* Return Path Header */}
      <div className="flex items-center justify-between mb-8">
        <Link
          to="/upload"
          className="inline-flex items-center space-x-2 text-sm text-muted hover:text-text transition-colors font-bold"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Upload Another Resume</span>
        </Link>
      </div>

      {hasData ? (
        <div className="space-y-8 text-left">
          {/* Main Title Info */}
          <div className="space-y-3">
            <h1 className="text-3xl sm:text-4xl font-black text-text tracking-tight font-display">
              Job Recommendations
            </h1>
            
            {/* Session Metadata Info Row */}
            <div className="flex flex-wrap gap-4 text-xs text-muted font-medium pt-1">
              <div className="flex items-center space-x-1.5 bg-surface border border-zinc-200 px-3 py-1.5 rounded-xl text-text">
                <FileText className="h-4 w-4 text-primary" />
                <span className="font-bold">{resumeName}</span>
              </div>
              
              {query && (
                <div className="flex items-center space-x-1.5 bg-surface border border-zinc-200 px-3 py-1.5 rounded-xl text-text">
                  <Search className="h-4 w-4 text-accent" />
                  <span>Query: </span>
                  <span className="font-bold">"{query}"</span>
                </div>
              )}

              <div className="flex items-center space-x-1.5 bg-surface border border-zinc-200 px-3 py-1.5 rounded-xl text-text">
                <Briefcase className="h-4 w-4 text-primary" />
                <span>Matches Found: </span>
                <span className="font-bold">{recommendations.length}</span>
              </div>
            </div>
          </div>

          {/* Cards Grid List */}
          <div className="space-y-6">
            {recommendations.map((job, idx) => (
              <RecommendationCard key={idx} job={job} index={idx} />
            ))}
          </div>
        </div>
      ) : (
        /* Empty / Fallback view if navigated directly */
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-xl mx-auto bg-card border border-white/5 rounded-3xl p-8 sm:p-12 shadow-2xl text-center space-y-6"
        >
          <div className="w-16 h-16 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto text-muted">
            <Briefcase className="h-8 w-8 text-primary" />
          </div>
          
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-white font-display">No Recommendations</h2>
            <p className="text-sm text-zinc-400 leading-relaxed max-w-sm mx-auto">
              Please upload and process your resume file to see matches tailored to your engineering skills.
            </p>
          </div>

          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl btn-primary shadow-lg"
          >
            <Upload className="h-4 w-4" />
            <span>Go to Upload page</span>
          </Link>
        </motion.div>
      )}
    </div>
  )
}
