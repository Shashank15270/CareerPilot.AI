export default function LoadingSpinner({ size = "md", className = "" }) {
  const sizeClasses = {
    sm: "w-6 h-6 border-2",
    md: "w-10 h-10 border-3",
    lg: "w-16 h-16 border-4"
  }

  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Spinning element */}
      <div className={`animate-spin rounded-full border-solid border-white/10 border-t-primary ${sizeClasses[size]}`}></div>
      
      {/* Ping ring for secondary visual rhythm */}
      <div className={`absolute rounded-full border border-solid border-accent/20 animate-ping opacity-40 ${sizeClasses[size]}`}></div>
    </div>
  )
}
