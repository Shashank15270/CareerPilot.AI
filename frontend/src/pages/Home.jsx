import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Cpu, Search, FileJson, ShieldCheck, ArrowRight } from 'lucide-react'
import Hero from '../components/Hero'
import FeatureCard from '../components/FeatureCard'

export default function Home() {
  const features = [
    {
      icon: Cpu,
      title: "AI Semantic Vector Search",
      description: "Uses sentence-transformer embeddings to represent resumes and job listings in multi-dimensional space, discovering deep matches beyond keyword matches."
    },
    {
      icon: FileJson,
      title: "Parser & Information Extractor",
      description: "Extracts summary, skills, experience, and projects from PDF/DOCX files cleanly, converting unstructured files into high-quality profiles."
    },
    {
      icon: Search,
      title: "Smart Pre-Filtering Queries",
      description: "Optionally filter job feeds by standard developer terms (e.g. 'Python', 'React') to narrow the search scope before executing AI matching."
    },
    {
      icon: ShieldCheck,
      title: "Similarity Validation & Scores",
      description: "Calculates precise mathematical cosine similarity metrics and presents them in animated indicators, ensuring transparency."
    }
  ]

  const steps = [
    {
      number: "01",
      title: "Drop Your Document",
      description: "Upload your resume in PDF or DOCX format inside our drag-and-drop secure box."
    },
    {
      number: "02",
      title: "Semantic Vector Parsing",
      description: "FastAPI parses the text content and creates a dense neural vector representation of your experience."
    },
    {
      number: "03",
      title: "Multi-Source Job Scrape",
      description: "We query live remote job portals in real-time based on your optional keywords."
    },
    {
      number: "04",
      title: "Instant Match Analysis",
      description: "We rank all openings and output the best fits, complete with similarity breakdowns."
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.12 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } }
  }

  return (
    <div className="relative">
      <Hero />

      {/* Features Section */}
      <section className="py-12 sm:py-20 border-t border-zinc-200 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-text mb-4">
              Designed for Professional Job Matching
            </h2>
            <p className="text-muted text-base sm:text-lg">
              Our advanced software stack processes resume information accurately and searches live remote job feeds using machine learning algorithms.
            </p>
          </div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {features.map((feature, idx) => (
              <motion.div key={idx} variants={itemVariants}>
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 border-t border-zinc-200 bg-surface/60 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-20">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-text mb-4">
              Real-Time Pipeline Stages
            </h2>
            <p className="text-muted text-base sm:text-lg">
              Here is how we convert your raw document into structured, highly targeted career matches.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {steps.map((step, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                className="bg-card border border-white/5 shadow-xl rounded-2xl p-6 relative z-10 hover:border-white/10 transition-all text-left group"
              >
                <div className="flex items-center justify-between mb-6">
                  <span className="text-3xl font-black text-white/15 tracking-wider font-mono">{step.number}</span>
                  <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-white font-bold text-xs group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                    ✓
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2 tracking-wide font-display">{step.title}</h3>
                <p className="text-zinc-400 text-sm leading-relaxed">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-12 sm:py-20 border-t border-zinc-200 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="p-8 sm:p-12 rounded-3xl bg-card shadow-2xl relative overflow-hidden text-left border border-white/5">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] pointer-events-none -z-10 animate-pulse duration-[8000ms]"></div>
            
            <div className="max-w-xl space-y-4">
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
                Ready to Discover Your Next Role?
              </h2>
              <p className="text-zinc-400 text-sm sm:text-base leading-relaxed">
                Scan your resume now, analyze matching accuracy in real-time, and target the top placements matching your skill sets.
              </p>
              <div className="pt-4">
                <Link
                  to="/upload"
                  className="inline-flex items-center space-x-2 px-8 py-4 rounded-xl btn-primary shadow-lg"
                >
                  <span>Scan Resume Instantly</span>
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
