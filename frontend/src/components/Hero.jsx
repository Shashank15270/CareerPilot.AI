import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, FileText, Briefcase } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-20 pb-16 sm:pb-24 lg:pt-32">
      {/* Decorative ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs font-semibold text-primary mb-6 uppercase tracking-wider"
          >
            <Sparkles className="h-3.5 w-3.5 text-accent animate-pulse" />
            <span>Next-Gen Semantic Job Matching</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-6xl font-black tracking-tight text-text mb-6 leading-[1.15] font-display"
          >
            Match Your Resume to <span className="text-gradient">AI-Powered</span> Job Openings
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg sm:text-xl text-muted mb-10 max-w-2xl mx-auto leading-relaxed"
          >
            Upload your resume and let our advanced neural embeddings automatically parse, extract, and match your skills to real-time opportunities in seconds.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <Link
              to="/upload"
              className="w-full sm:w-auto px-8 py-4 rounded-xl btn-primary flex items-center justify-center space-x-2 shadow-lg"
            >
              <span>Scan Your Resume</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="#how-it-works"
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-surface border border-zinc-200 text-text font-bold flex items-center justify-center space-x-2 hover:bg-zinc-100 transition-all shadow-sm"
            >
              <span>See How It Works</span>
            </a>
          </motion.div>
        </div>

        {/* Hero Interactive Mock Visual */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 40 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="relative max-w-4xl mx-auto rounded-2xl glass-card overflow-hidden p-1 shadow-2xl border border-white/5"
        >
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-accent/5 pointer-events-none"></div>
          
          {/* Mock UI Shell */}
          <div className="bg-surface/90 rounded-[14px] p-6 sm:p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6 border-b border-white/5 pb-6 mb-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-primary/10 rounded-xl border border-primary/20 text-primary">
                  <FileText className="h-6 w-6" />
                </div>
                <div className="text-left">
                  <div className="text-white font-semibold">resume_shashank.pdf</div>
                  <div className="text-sm text-muted">Parsed successfully • 45kb</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 text-accent bg-accent/10 border border-accent/20 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                <Sparkles className="h-3.5 w-3.5" />
                <span>AI Embeddings Generated</span>
              </div>
            </div>

            {/* Mock Matches List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/[0.02] border border-white/5 rounded-xl hover:border-white/10 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
                  <div className="text-left">
                    <div className="text-white font-medium text-sm sm:text-base">Senior Full Stack Engineer</div>
                    <div className="text-xs sm:text-sm text-muted">Lemon.io • Remote</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right hidden sm:block">
                    <div className="text-sm text-accent font-semibold">96.8% Match</div>
                    <div className="text-xs text-muted">Semantic Vector Similarity</div>
                  </div>
                  <div className="px-3.5 py-1.5 bg-primary/25 border border-primary/50 text-white rounded-lg text-xs font-semibold">
                    Best Match
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                <div className="flex items-center space-x-4">
                  <div className="w-2.5 h-2.5 rounded-full bg-green-400"></div>
                  <div className="text-left">
                    <div className="text-white font-medium text-sm sm:text-base">AI Software Engineer</div>
                    <div className="text-xs sm:text-sm text-muted">Stripe • Remote</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right hidden sm:block">
                    <div className="text-sm text-white font-semibold">92.4% Match</div>
                    <div className="text-xs text-muted">Semantic Vector Similarity</div>
                  </div>
                  <div className="px-3.5 py-1.5 bg-white/5 border border-white/10 text-white rounded-lg text-xs font-semibold">
                    Match
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
