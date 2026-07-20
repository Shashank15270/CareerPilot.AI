import { Briefcase, Github, Linkedin, Twitter } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-zinc-200 bg-background py-8 mt-auto text-muted">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center space-x-2">
            <div className="p-1 rounded-md bg-primary/20 border border-primary/40 flex items-center justify-center">
              <Briefcase className="h-4 w-4 text-primary" />
            </div>
            <span className="font-extrabold text-base tracking-wide text-text font-display">
              Antigravity<span className="text-accent font-semibold ml-0.5">AI</span>
            </span>
          </div>
          
          <p className="text-xs text-muted text-center md:text-left font-semibold">
            &copy; {new Date().getFullYear()} Antigravity AI. Powered by Advanced Neural Embeddings & Grok AI.
          </p>
          
          <div className="flex space-x-4">
            <a href="#" className="text-muted hover:text-text transition-colors">
              <Twitter className="h-4 w-4" />
            </a>
            <a href="#" className="text-muted hover:text-text transition-colors">
              <Linkedin className="h-4 w-4" />
            </a>
            <a href="#" className="text-muted hover:text-text transition-colors">
              <Github className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
