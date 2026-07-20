import { motion } from 'framer-motion'

export default function FeatureCard({ icon: Icon, title, description }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="p-5 sm:p-6 rounded-2xl glass-card flex flex-col items-start text-left relative overflow-hidden transition-all duration-300 group hover:border-primary/25 hover:shadow-[0_0_30px_rgba(112,79,56,0.08)] bg-card"
    >
      <div className="p-3 rounded-xl bg-primary/20 border border-primary/40 text-primary mb-4 group-hover:bg-primary group-hover:text-white transition-colors duration-300">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="text-lg font-bold text-white mb-2 tracking-wide font-display">{title}</h3>
      <p className="text-zinc-400 text-sm leading-relaxed">{description}</p>
      
      {/* Subtle border bottom glow */}
      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-primary/0 via-primary/40 to-accent/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    </motion.div>
  )
}
