"use client"

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { motion, AnimatePresence } from "framer-motion"
import {
  AlertCircle,
  AudioLines,
  CheckCircle2,
  Eye,
  FileVideo,
  Link as LinkIcon,
  Loader2,
  ShieldCheck,
  Sparkles,
  XCircle,
  Tag,
  Timer,
  UploadCloud,
} from "lucide-react"
import { SiteShell } from "@/components/SiteShell"
import { ProgressBar } from "@/components/ProgressBar"
import { VideoTimeline } from "@/components/VideoTimeline"
import { Skeleton } from "@/components/ui/Skeleton"
import { useAuth } from "@/contexts/auth-context"
import { analyzeVideo, fetchAnalysisResult, streamAnalysisProgress } from "@/lib/api-client"
import type { AnalysisResult } from "@/types/api"
import { getPlatformIcon, type PlatformType } from "@/lib/platforms"

export default function AnalyzePage() {
  const router = useRouter()
  const { user, loading: authLoading, signOut } = useAuth()
  const [url, setUrl] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressStatus, setProgressStatus] = useState("")
  const [progressStage, setProgressStage] = useState("idle")
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const analysisAbortRef = useRef<AbortController | null>(null)

  const platformType: PlatformType = useMemo(() => {
    if (file) return 'file'
    return getPlatformIcon(url).name === 'URL' ? 'url' : getPlatformIcon(url).name.toLowerCase() as PlatformType
  }, [url, file])

  useEffect(() => {
    if (!authLoading && !user) {
      toast.error("Please sign in to use analysis")
      router.push("/auth/login")
    }
  }, [user, authLoading, router])

  const handleAuthExpired = async () => {
    toast.error("Session expired. Please sign in again.")
    try {
      await signOut()
    } catch (signOutError) {
      console.warn("Failed to sign out after session expiry:", signOutError)
    }
    router.push("/auth/login")
  }

  const markers = useMemo(() => {
    if (!result?.detected_brands) {
      return []
    }
    return result.detected_brands
      .filter((brand) => (brand.confidence ?? 0) >= 0.5)
      .flatMap((brand) => {
        const sorted = [...(brand.timestamps ?? [])].sort((a, b) => a - b)
        if (!sorted.length) return []
        return sorted.map((timestamp, idx) => {
          const next = sorted[idx + 1]
          const duration = next ? Math.min(4, Math.max(0.5, next - timestamp)) : 1
          return {
            label: brand.name,
            time: Math.round(timestamp),
            confidence: brand.confidence,
            duration,
          }
        })
      })
  }, [result])

  const normalizedStatus = (result?.status ?? "").toLowerCase()

  const sortedBrands = useMemo(() => {
    return [...(result?.detected_brands ?? [])].sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0))
  }, [result?.detected_brands])

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile && droppedFile.type.startsWith("video/")) {
      setFile(droppedFile)
      toast.success(`File selected: ${droppedFile.name}`)
    } else {
      toast.error("Please drop a valid video file")
    }
  }

  async function handleAnalyze(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!user) {
      toast.error("Please sign in first")
      router.push("/auth/login")
      return
    }
    if (!url.trim() && !file) {
      toast.error("Provide a URL or upload a video file")
      return
    }

    setIsSubmitting(true)
    setProgress(0)
    setProgressStatus("Preparing...")
    setProgressStage("upload")
    setResult(null)
    analysisAbortRef.current = new AbortController()

    try {
      const response = await analyzeVideo({ url: url.trim() || undefined, file: file ?? undefined })
      setResult(response)

      if (response.task_id) {
        await streamAnalysisProgress({
          taskId: response.task_id,
          signal: analysisAbortRef.current.signal,
          onMessage: (payload) => {
            setProgress(payload.progress ?? 0)
            setProgressStatus(payload.message ?? payload.status ?? "Processing")
            setProgressStage(payload.stage ?? "processing")
          },
          onError: (error) => {
            if (error.name !== "AbortError") {
              toast.error(error.message)
            }
          },
        })
        try {
          const finalResult = await fetchAnalysisResult({ taskId: response.task_id })
          setResult(finalResult)
          setProgress(100)
          setProgressStatus(finalResult.status ?? "Completed")
          setProgressStage("complete")
          setUrl("")
        } catch (error: any) {
          if (error.response?.status === 401) {
            await handleAuthExpired()
            return
          }
          toast.error("Failed to load analysis results.")
          setUrl("")
        }
      } else {
        setProgress(100)
        setProgressStatus("Completed")
        setProgressStage("complete")
        setUrl("")
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        setProgressStatus("Analysis cancelled")
        setProgressStage("idle")
      } else if (error.response?.status === 401) {
        await handleAuthExpired()
      } else {
        toast.error("Analysis failed. Check logs for details.")
        setUrl("")
      }
    } finally {
      setIsSubmitting(false)
      analysisAbortRef.current = null
    }
  }

  const handleCancelAnalysis = () => {
    analysisAbortRef.current?.abort()
    setIsSubmitting(false)
    setProgressStage("idle")
    setProgressStatus("Analysis cancelled")
    toast.message("Analysis cancelled. Processing may still continue on the server.")
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-5xl px-4 py-12">
        {/* Header */}
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.p
            className="text-sm font-medium text-primary mb-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            Content analysis
          </motion.p>
          <motion.h1
            className="text-4xl font-semibold tracking-tight"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            Analyze content for advertising
          </motion.h1>
          <motion.p
            className="mt-3 text-muted-foreground max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Upload a video or paste a URL from YouTube, Telegram, Instagram, TikTok, or VK.
            Get instant insights about sponsored content and brand mentions.
          </motion.p>
        </motion.div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Left Column - Form */}
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <motion.form
              className="card p-6 space-y-6"
              onSubmit={handleAnalyze}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              {/* URL Input */}
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <LinkIcon className="h-4 w-4 text-muted-foreground" />
                  Video or Post URL
                </label>
                <div className="relative">
                  <input
                    type="url"
                    placeholder="https://youtube.com/... or https://t.me/..."
                    className="input-field pr-12"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={isSubmitting || !!file}
                  />
                  {url && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <PlatformBadge url={url} />
                    </div>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  Supports: YouTube, Telegram, Instagram, TikTok, VK
                </p>
              </div>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">or upload file</span>
                </div>
              </div>

              {/* File Upload */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Upload video file</label>
                <label
                  className={`flex cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed px-4 py-8 text-sm transition-all duration-300 ${
                    isDragging
                      ? "border-primary bg-primary/5 scale-[1.02]"
                      : "border-border bg-muted/30 hover:bg-muted/50 hover:border-primary/50"
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <UploadCloud className={`h-8 w-8 ${isDragging ? "text-primary" : "text-muted-foreground"}`} />
                  <div className="text-center">
                    {file ? (
                      <motion.div
                        className="flex items-center gap-2 text-foreground font-medium"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      >
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        {file.name}
                      </motion.div>
                    ) : (
                      <div className="space-y-1">
                        <span className="text-muted-foreground">
                          Drop your video file here or click to browse
                        </span>
                        <p className="text-xs text-muted-foreground">
                          MP4, MOV, WebM, MKV (max 500MB)
                        </p>
                      </div>
                    )}
                  </div>
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                    disabled={isSubmitting || !!url}
                  />
                </label>
              </div>

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={isSubmitting || (!url && !file)}
                className="btn btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed group"
                whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
                whileTap={{ scale: isSubmitting ? 1 : 0.98 }}
              >
                <AnimatePresence mode="wait">
                  {isSubmitting ? (
                    <motion.div
                      key="loading"
                      className="flex items-center gap-2"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>{progressStatus || "Processing..."}</span>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="submit"
                      className="flex items-center gap-2"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <FileVideo className="h-4 w-4" />
                      <span>Start analysis</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
              {isSubmitting && (
                <button
                  type="button"
                  onClick={handleCancelAnalysis}
                  className="btn w-full py-3 border border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <span className="inline-flex items-center gap-2">
                    <XCircle className="h-4 w-4" />
                    Cancel analysis
                  </span>
                </button>
              )}
            </motion.form>
          </motion.div>

          {/* Right Column - Results */}
          <motion.div
            className="lg:sticky lg:top-24 h-fit space-y-6"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="card p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  Analysis Report
                  {isSubmitting && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {isSubmitting ? "Processing content pipeline..." : "Detailed breakdown of advertising signals and brand mentions."}
                </p>
                <div className="mt-4">
                  <ProgressBar value={progress} label={progressStatus || "Idle"} stage={progressStage} />
                </div>
              </div>

              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div
                    className="space-y-6"
                    key="results"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.4 }}
                  >
                    {/* Status & Summary Card */}
                    <motion.div
                      className={`rounded-xl p-5 border relative overflow-hidden ${
                        normalizedStatus === "completed"
                          ? "bg-emerald-500/5 border-emerald-500/20" 
                          : result.error 
                            ? "bg-red-500/5 border-red-500/20"
                            : "bg-muted/30 border-border"
                      }`}
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                    >
                      <div className="absolute top-0 right-0 p-3 opacity-10">
                         {normalizedStatus === "completed" ? (
                           <ShieldCheck className="h-16 w-16" />
                         ) : (
                           <AlertCircle className="h-16 w-16" />
                         )}
                      </div>
                      
                      <div className="flex items-start gap-4 relative z-10">
                        <div className={`mt-1 p-2 rounded-lg ${
                           normalizedStatus === "completed" ? "bg-emerald-500/20 text-emerald-600" : "bg-red-500/20 text-red-600"
                        }`}>
                          {normalizedStatus === "completed" ? (
                            <CheckCircle2 className="h-5 w-5" />
                          ) : (
                            <AlertCircle className="h-5 w-5" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-sm uppercase tracking-wider text-muted-foreground/80 mb-1">Final Verdict</p>
                          <h3 className="text-xl font-bold mb-2">
                             {result.has_advertising ? "Advertising Detected" : "No Advertising Detected"}
                          </h3>
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {result.ad_reason || "Content has been scanned for visual, audio, and textual advertising signals."}
                          </p>
                        </div>
                      </div>
                    </motion.div>

                    {/* Scores Grid */}
                    <div className="grid gap-4">
                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Signal strength</p>
                      <div className="space-y-4">
                        <ScoreBar
                          label="Overall Confidence"
                          value={result.confidence_score}
                          icon={<Sparkles className="h-4 w-4" />}
                          delay={0.1}
                          color="confidence"
                          tooltip="Combined score from all detection methods"
                        />
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <ScoreBar
                            label="Visual"
                            value={result.visual_score}
                            icon={<Eye className="h-4 w-4" />}
                            delay={0.15}
                            color="visual"
                            compact
                          />
                          <ScoreBar
                            label="Audio"
                            value={result.audio_score}
                            icon={<AudioLines className="h-4 w-4" />}
                            delay={0.2}
                            color="audio"
                            compact
                          />
                        </div>
                      </div>
                    </div>

                    {/* Detected Brands - Enhanced List */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Detected Brands</p>
                        {result.detected_brands && result.detected_brands.length > 0 && (
                          <span className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-0.5 rounded-full">
                            {result.detected_brands.length}
                          </span>
                        )}
                      </div>
                      
                      <div className="grid gap-2">
                        {sortedBrands.length > 0 ? (
                          sortedBrands.map((brand, index) => (
                            <motion.div
                              key={`${brand.name}-${index}`}
                              className="group flex items-center gap-3 rounded-xl border border-border/50 bg-muted/20 p-3 hover:bg-muted/40 hover:border-border transition-all"
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.3 + index * 0.05 }}
                            >
                              <div className="h-10 w-10 shrink-0 rounded-lg bg-background border flex items-center justify-center overflow-hidden shadow-sm group-hover:scale-105 transition-transform">
                                {brand.logo_url ? (
                                  // eslint-disable-next-line @next/next/no-img-element
                                  <img src={brand.logo_url} alt={brand.name} className="h-7 w-7 object-contain" />
                                ) : (
                                  <span className="text-lg font-bold text-primary/40">{brand.name[0]}</span>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between gap-2">
                                  <h4 className="text-sm font-bold truncate">{brand.name}</h4>
                                  <span className="text-xs font-mono font-bold text-primary">{Math.round((brand.confidence ?? 0) * 100)}%</span>
                                </div>
                                <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground font-medium">
                                  <span className="flex items-center gap-1"><Tag className="h-3 w-3" /> {brand.detections || 1} hits</span>
                                  <span className="flex items-center gap-1"><Timer className="h-3 w-3" /> {brand.total_exposure_seconds?.toFixed(1) || 0}s</span>
                                </div>
                              </div>
                            </motion.div>
                          ))
                        ) : (
                          <div className="py-4 text-center border border-dashed rounded-xl">
                            <p className="text-xs text-muted-foreground">No specific brands identified</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Timeline with better label */}
                    <div className="space-y-3">
                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Exposure Timeline</p>
                      <VideoTimeline duration={result.duration ?? 0} markers={markers} showFilter={true} />
                    </div>

                    {/* Export Actions - New Section */}
                    {normalizedStatus === "completed" && (
                      <div className="pt-2 flex gap-2">
                        <button className="btn btn-outline flex-1 text-xs py-2 h-9">
                           Download PDF Report
                        </button>
                        <button className="btn btn-outline flex-1 text-xs py-2 h-9">
                           Share Results
                        </button>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <motion.div
                    key="placeholder"
                    className="space-y-6"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    {isSubmitting ? (
                      <div className="space-y-6">
                        <Skeleton className="h-32 w-full rounded-2xl" />
                        <div className="space-y-4">
                          <Skeleton className="h-4 w-32" />
                          <Skeleton className="h-10 w-full rounded-xl" />
                          <Skeleton className="h-10 w-full rounded-xl" />
                        </div>
                        <div className="space-y-3">
                          <Skeleton className="h-4 w-24" />
                          <div className="grid grid-cols-2 gap-3">
                            <Skeleton className="h-16 w-full rounded-xl" />
                            <Skeleton className="h-16 w-full rounded-xl" />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <EmptyState />
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </section>
    </SiteShell>
  )
}

// ==================== Sub-components ====================

function PlatformBadge({ url }: { url: string }) {
  const { icon: Icon, color, name } = getPlatformIcon(url)
  return (
    <div className={`flex items-center gap-1.5 ${color}`} title={name}>
      <Icon className="h-4 w-4" />
      <span className="text-xs font-medium hidden sm:inline">{name}</span>
    </div>
  )
}

interface ScoreBarProps {
  label: string
  value?: number
  delay?: number
  color?: "confidence" | "visual" | "audio" | "disclosure"
  tooltip?: string
  icon?: ReactNode
  compact?: boolean
}

function ScoreBar({ label, value, delay = 0, color = "confidence", tooltip, icon, compact }: ScoreBarProps) {
  const numericValue = Math.round((value ?? 0) * 100)
  const displayValue = `${numericValue}%`

  const confidenceGradient = () => {
    if (numericValue < 30) return "from-red-500 to-red-400"
    if (numericValue < 70) return "from-amber-500 to-amber-400"
    return "from-emerald-500 to-emerald-400"
  }

  const colorClasses = {
    confidence: `bg-gradient-to-r ${confidenceGradient()}`,
    visual: "bg-gradient-to-r from-blue-600 to-cyan-500",
    audio: numericValue === 0 ? "bg-muted-foreground/30" : "bg-gradient-to-r from-sky-500 to-indigo-500",
    disclosure: numericValue === 0 ? "bg-muted-foreground/30" : "bg-gradient-to-r from-emerald-600 to-green-500",
  }

  return (
    <motion.div
      className={`group ${compact ? 'space-y-1' : 'space-y-2'}`}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.3 }}
    >
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-1.5">
          <span className="text-muted-foreground shrink-0">{icon}</span>
          <span className="text-[11px] font-bold text-muted-foreground/80 uppercase tracking-tight">{label}</span>
          {tooltip && (
            <div className="relative group/tip">
              <AlertCircle className="h-3 w-3 text-muted-foreground/40 cursor-help" />
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-3 py-2 bg-foreground text-background text-[10px] font-medium rounded-lg opacity-0 invisible group-hover/tip:opacity-100 group-hover/tip:visible transition-all whitespace-nowrap z-50 shadow-xl">
                {tooltip}
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-foreground" />
              </div>
            </div>
          )}
        </div>
        <span className="font-mono font-bold text-xs">{displayValue}</span>
      </div>
      <div className={`relative ${compact ? 'h-1.5' : 'h-2.5'} rounded-full bg-muted overflow-hidden border border-border/10`}>
        <motion.div
          className={`h-full rounded-full ${colorClasses[color]}`}
          initial={{ width: 0 }}
          animate={{ width: `${numericValue}%` }}
          transition={{ delay: delay + 0.2, duration: 0.8, ease: "easeOut" }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </motion.div>
      </div>
    </motion.div>
  )
}

function EmptyState() {
  const examples = [
    { platform: 'YouTube', url: 'https://youtube.com/watch?v=...' },
    { platform: 'Telegram', url: 'https://t.me/channel/123' },
    { platform: 'Instagram', url: 'https://instagram.com/p/...' },
  ]

  return (
    <motion.div
      className="text-center py-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="mb-4">
        <FileVideo className="h-12 w-12 mx-auto text-muted-foreground/50" />
      </div>
      <p className="text-sm text-muted-foreground mb-4">
        No analysis yet. Submit a video or URL to see results.
      </p>
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Quick examples
        </p>
        {examples.map((example, i) => (
          <motion.button
            key={example.platform}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors block w-full text-center"
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            whileHover={{ x: 5 }}
          >
            {example.platform}: <code className="bg-muted px-1.5 py-0.5 rounded">{example.url}</code>
          </motion.button>
        ))}
      </div>
    </motion.div>
  )
}
