import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { SlidersHorizontal, AlertCircle } from 'lucide-react'
import UploadCard from '../components/UploadCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { getRecommendations } from '../services/api'

const PIPELINE_STEPS = [
  "Uploading Resume...",
  "Parsing Resume...",
  "Extracting Information...",
  "Generating Embeddings...",
  "Finding Jobs...",
  "Ranking Jobs...",
  "Preparing Recommendations..."
]

export default function Upload() {
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [error, setError] = useState('')
  const [showOptions, setShowOptions] = useState(false)

  // Advanced Filters State
  const [country, setCountry] = useState('')
  const [state, setState] = useState('')
  const [city, setCity] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [workplaceType, setWorkplaceType] = useState('')
  const [salaryMin, setSalaryMin] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [skills, setSkills] = useState('')
  const [industry, setIndustry] = useState('')
  
  const navigate = useNavigate()

  useEffect(() => {
    let interval
    if (isAnalyzing) {
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          // Progress through steps 0 to 4 automatically, then wait for the actual API response
          if (prev < 4) {
            return prev + 1
          }
          return prev
        })
      }, 1200)
    } else {
      setCurrentStep(0)
    }
    return () => clearInterval(interval)
  }, [isAnalyzing])

  const handleAnalyze = async () => {
    if (!file) return
    setIsAnalyzing(true)
    setError('')
    setCurrentStep(0)

    try {
      // Start API Call with advanced filters
      const recommendations = await getRecommendations(file, {
        query,
        top_k: topK,
        country,
        state,
        city,
        experience_level: experienceLevel,
        employment_type: employmentType,
        workplace_type: workplaceType,
        salary_min: salaryMin ? parseInt(salaryMin, 10) : undefined,
        company_name: companyName,
        skills,
        industry
      })
      
      // Complete remaining steps dynamically
      setCurrentStep(5) // Ranking Jobs...
      await new Promise(resolve => setTimeout(resolve, 800))
      
      setCurrentStep(6) // Preparing Recommendations...
      await new Promise(resolve => setTimeout(resolve, 800))

      // Navigate to results
      navigate('/recommendations', {
        state: {
          recommendations,
          resumeName: file.name,
          query,
          topK,
          filters: {
            country,
            state,
            city,
            experienceLevel,
            employmentType,
            workplaceType,
            salaryMin,
            companyName,
            skills,
            industry
          }
        }
      })
    } catch (err) {
      console.error(err)
      setIsAnalyzing(false)
      const detail = err.response?.data?.detail;
      const errorMsg = typeof detail === 'string' ? detail : (Array.isArray(detail) ? detail[0]?.msg : "An error occurred while analyzing the resume. Please try again.");
      setError(errorMsg)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 relative min-h-[80vh] flex flex-col justify-center">
      
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-primary/5 rounded-full blur-[120px] pointer-events-none -z-10"></div>

      <AnimatePresence mode="wait">
        {!isAnalyzing ? (
          <motion.div
            key="upload-form"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-8"
          >
            <div className="text-center">
              <h1 className="text-4xl font-extrabold text-text tracking-tight mb-3 font-display">
                Analyze Your Profile
              </h1>
              <p className="text-muted text-base max-w-lg mx-auto leading-relaxed">
                Upload your resume in PDF or DOCX format. Our AI will analyze your skill profile and scan live jobs to match you instantly.
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="max-w-2xl mx-auto p-4 rounded-xl bg-red-500/10 border border-red-500/25 flex items-center space-x-3 text-red-400 text-sm text-left"
              >
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Upload Card Component */}
            <UploadCard
              file={file}
              onFileChange={setFile}
              onRemove={() => setFile(null)}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
            />

            {/* Optional search filters & options */}
            {file && (
              <div className="max-w-2xl mx-auto">
                <button
                  type="button"
                  onClick={() => setShowOptions(!showOptions)}
                  className="flex items-center space-x-2 text-sm text-muted hover:text-white transition-colors py-2 px-3 rounded-lg border border-white/5 bg-white/[0.01] hover:bg-white/[0.04] mx-auto cursor-pointer"
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  <span>{showOptions ? "Hide Advanced Options" : "Show Advanced Options"}</span>
                </button>

                <AnimatePresence>
                  {showOptions && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden mt-4"
                    >
                      <div className="p-6 rounded-3xl bg-card border border-white/5 text-left space-y-6 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-white/5 pb-2">Target Job Search Criteria</h3>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
                          {/* Row 1 */}
                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Search Query / Role Title
                            </label>
                            <input
                              type="text"
                              value={query}
                              onChange={(e) => setQuery(e.target.value)}
                              placeholder="e.g. Python Developer"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Target Skills (Comma Separated)
                            </label>
                            <input
                              type="text"
                              value={skills}
                              onChange={(e) => setSkills(e.target.value)}
                              placeholder="e.g. React, Docker, SQL"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Top Recommendations (Count)
                            </label>
                            <select
                              value={topK}
                              onChange={(e) => setTopK(Number(e.target.value))}
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer font-semibold"
                            >
                              <option value={3}>Top 3 Matches</option>
                              <option value={5}>Top 5 Matches</option>
                              <option value={10}>Top 10 Matches</option>
                              <option value={15}>Top 15 Matches</option>
                              <option value={20}>Top 20 Matches</option>
                            </select>
                          </div>

                          {/* Row 2 */}
                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Country
                            </label>
                            <select
                              value={country}
                              onChange={(e) => setCountry(e.target.value)}
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer font-semibold"
                            >
                              <option value="">Any Country</option>
                              <option value="India">India</option>
                              <option value="United States">United States</option>
                              <option value="Canada">Canada</option>
                              <option value="United Kingdom">United Kingdom</option>
                              <option value="Germany">Germany</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              State / Region
                            </label>
                            <input
                              type="text"
                              value={state}
                              onChange={(e) => setState(e.target.value)}
                              placeholder="e.g. Karnataka"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              City
                            </label>
                            <input
                              type="text"
                              value={city}
                              onChange={(e) => setCity(e.target.value)}
                              placeholder="e.g. Bangalore"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          {/* Row 3 */}
                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Experience Level
                            </label>
                            <select
                              value={experienceLevel}
                              onChange={(e) => setExperienceLevel(e.target.value)}
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer font-semibold"
                            >
                              <option value="">Any Experience</option>
                              <option value="Entry Level">0–1 Years (Entry)</option>
                              <option value="Mid Level">1–3 Years (Mid)</option>
                              <option value="Senior Level">3–5 Years (Senior)</option>
                              <option value="Lead">5+ Years (Lead / Exec)</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Employment Type
                            </label>
                            <select
                              value={employmentType}
                              onChange={(e) => setEmploymentType(e.target.value)}
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer font-semibold"
                            >
                              <option value="">Any Type</option>
                              <option value="Full-time">Full Time</option>
                              <option value="Internship">Internship</option>
                              <option value="Contract">Contract</option>
                              <option value="Part-time">Part Time</option>
                              <option value="Freelance">Freelance</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Workplace Style
                            </label>
                            <select
                              value={workplaceType}
                              onChange={(e) => setWorkplaceType(e.target.value)}
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors cursor-pointer font-semibold"
                            >
                              <option value="">Any Style</option>
                              <option value="Remote">Remote Only</option>
                              <option value="Hybrid">Hybrid</option>
                              <option value="Onsite">Onsite</option>
                            </select>
                          </div>

                          {/* Row 4 */}
                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Minimum Salary (Annual)
                            </label>
                            <input
                              type="number"
                              value={salaryMin}
                              onChange={(e) => setSalaryMin(e.target.value)}
                              placeholder="e.g. 1000000"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Company Name
                            </label>
                            <input
                              type="text"
                              value={companyName}
                              onChange={(e) => setCompanyName(e.target.value)}
                              placeholder="e.g. Stripe"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-2">
                              Industry Keywords
                            </label>
                            <input
                              type="text"
                              value={industry}
                              onChange={(e) => setIndustry(e.target.value)}
                              placeholder="e.g. Fintech, Healthcare"
                              className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-zinc-500 font-semibold"
                            />
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </motion.div>
        ) : (
          /* Analyzing / Progress View */
          <motion.div
            key="analyzing-progress"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="w-full max-w-xl mx-auto glass rounded-3xl p-8 sm:p-10 shadow-2xl text-center space-y-8"
          >
            <LoadingSpinner size="lg" className="mx-auto" />

            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-white tracking-wide">
                Analyzing Resume
              </h2>
              <p className="text-sm text-muted">
                Connecting with AI Matching Model...
              </p>
            </div>

            {/* Pipeline Step List */}
            <div className="space-y-3.5 max-w-xs mx-auto text-left py-4">
              {PIPELINE_STEPS.map((step, idx) => {
                const isCompleted = idx < currentStep
                const isActive = idx === currentStep
                return (
                  <div
                    key={step}
                    className={`flex items-center space-x-3.5 text-sm transition-all duration-300 ${
                      isCompleted
                        ? 'text-white/40'
                        : isActive
                        ? 'text-primary font-semibold'
                        : 'text-muted/40'
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {isCompleted ? (
                        <div className="w-5 h-5 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-primary text-xs font-bold font-mono">
                          ✓
                        </div>
                      ) : isActive ? (
                        <div className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
                      ) : (
                        <div className="w-5 h-5 rounded-full border border-white/10 bg-white/[0.01]"></div>
                      )}
                    </div>
                    <span>{step}</span>
                  </div>
                )
              })}
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
                initial={{ width: "0%" }}
                animate={{ width: `${((currentStep + 1) / PIPELINE_STEPS.length) * 100}%` }}
                transition={{ duration: 0.5 }}
              ></motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
