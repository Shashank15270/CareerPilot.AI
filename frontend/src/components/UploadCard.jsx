import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UploadCloud, Trash2, FileCheck } from 'lucide-react'

export default function UploadCard({ file, onFileChange, onRemove, onAnalyze, isAnalyzing }) {
  const [isDragActive, setIsDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true)
    } else if (e.type === "dragleave") {
      setIsDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0])
    }
  }

  const handleFileBrowse = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0])
    }
  }

  const validateAndSelectFile = (selectedFile) => {
    const allowedExtensions = ['.pdf', '.docx']
    const extension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
    
    if (allowedExtensions.includes(extension)) {
      onFileChange(selectedFile)
    } else {
      alert("Invalid file format. Only PDF and DOCX files are allowed.")
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-card rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden border border-white/5">
        
        {/* Drag and Drop Area */}
        {!file ? (
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
              isDragActive
                ? 'border-primary bg-primary/5 scale-[1.01]'
                : 'border-white/10 hover:border-white/20 bg-white/[0.01]'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileBrowse}
              className="hidden"
            />
            
            <motion.div
              animate={{ y: isDragActive ? -5 : 0 }}
              className="p-4 rounded-full bg-white/[0.02] border border-white/5 text-zinc-400 mb-4"
            >
              <UploadCloud className={`h-10 w-10 transition-colors ${isDragActive ? 'text-primary' : ''}`} />
            </motion.div>
            
            <h3 className="text-lg font-bold text-white mb-1 font-display">
              Upload your resume
            </h3>
            <p className="text-zinc-400 text-sm text-center mb-6">
              Drag & drop your file here, or click to browse
            </p>
            
            <div className="text-xs text-zinc-400 bg-white/[0.02] border border-white/5 px-4 py-1.5 rounded-full uppercase tracking-wider font-semibold">
              PDF or DOCX
            </div>
          </div>
        ) : (
          /* File Selected View */
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-6"
            >
              <div className="p-4 sm:p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
                <div className="flex items-center space-x-4 min-w-0">
                  <div className="p-3 bg-primary/10 rounded-xl border border-primary/20 text-primary">
                    <FileCheck className="h-6 w-6" />
                  </div>
                  <div className="text-left">
                    <div className="text-white font-semibold truncate">
                      {file.name}
                    </div>
                    <div className="text-xs text-zinc-400">
                      {formatFileSize(file.size)}
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={onRemove}
                  className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500 hover:text-white transition-all cursor-pointer"
                  title="Remove file"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>

              {/* Action Button */}
              <button
                onClick={onAnalyze}
                disabled={isAnalyzing}
                className="w-full py-4 px-6 rounded-xl btn-primary text-white font-bold flex items-center justify-center space-x-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>Analyze Resume</span>
              </button>
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}
