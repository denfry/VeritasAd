"use client"

import { useState, useMemo } from "react"
import { motion } from "framer-motion"
import { Clock, Filter, ZoomIn, ZoomOut } from "lucide-react"

type TimelineMarker = {
  label: string
  time: number
  confidence?: number
  duration?: number
}

// Brand colors for consistent coloring
const BRAND_COLORS: Record<string, string> = {
  "Twitch": "bg-purple-500 border-purple-600",
  "YouTube": "bg-red-500 border-red-600",
  "Apple": "bg-gray-500 border-gray-600",
  "Samsung": "bg-blue-500 border-blue-600",
  "Nike": "bg-orange-500 border-orange-600",
  "Adidas": "bg-green-500 border-green-600",
  "Coca-Cola": "bg-red-600 border-red-700",
  "McDonald's": "bg-yellow-500 border-yellow-600",
  "Winline": "bg-emerald-500 border-emerald-600",
  "1xBet": "bg-blue-600 border-blue-700",
  "Сбербанк": "bg-green-600 border-green-700",
  "Тинькофф": "bg-yellow-600 border-yellow-700",
  "Яндекс": "bg-red-500 border-red-600",
  "Wildberries": "bg-purple-600 border-purple-700",
  "Ozon": "bg-blue-500 border-blue-600",
}

const DEFAULT_COLOR = "bg-primary border-primary/80"

export function VideoTimeline({
  duration,
  markers,
  showFilter = true,
}: {
  duration: number
  markers: TimelineMarker[]
  showFilter?: boolean
}) {
  const safeDuration = duration > 0 ? duration : 1
  const [hoveredMarker, setHoveredMarker] = useState<number | null>(null)
  const [zoom, setZoom] = useState(1)
  const [selectedBrands, setSelectedBrands] = useState<Set<string>>(new Set())
  const [minConfidence, setMinConfidence] = useState(50)

  // Group markers by brand
  const groupedMarkers = useMemo(() => {
    const groups: Record<string, TimelineMarker[]> = {}
    markers
      .filter((marker) => ((marker.confidence ?? 0) * 100) >= minConfidence)
      .forEach((marker) => {
      if (!groups[marker.label]) {
        groups[marker.label] = []
      }
      groups[marker.label].push(marker)
      })
    return groups
  }, [markers, minConfidence])

  // Get unique brands sorted by detection count
  const uniqueBrands = useMemo(() => {
    return Object.entries(groupedMarkers)
      .sort((a, b) => b[1].length - a[1].length)
      .map(([name]) => name)
  }, [groupedMarkers])

  // Filter markers based on selected brands
  const filteredMarkers = useMemo(() => {
    const source = markers.filter((m) => ((m.confidence ?? 0) * 100) >= minConfidence)
    if (selectedBrands.size === 0) return source
    return source.filter(m => selectedBrands.has(m.label))
  }, [markers, selectedBrands, minConfidence])

  // Get color for brand
  const getBrandColor = (brandName: string) => {
    // Check exact match first
    if (BRAND_COLORS[brandName]) return BRAND_COLORS[brandName]
    
    // Check partial match
    for (const [brand, color] of Object.entries(BRAND_COLORS)) {
      if (brandName.toLowerCase().includes(brand.toLowerCase())) {
        return color
      }
    }
    
    // Generate consistent color based on brand name hash
    const hash = brandName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const colors = [
      "bg-pink-500 border-pink-600",
      "bg-indigo-500 border-indigo-600",
      "bg-cyan-500 border-cyan-600",
      "bg-teal-500 border-teal-600",
      "bg-rose-500 border-rose-600",
      "bg-violet-500 border-violet-600",
    ]
    return colors[hash % colors.length] || DEFAULT_COLOR
  }

  const toggleBrand = (brand: string) => {
    setSelectedBrands(prev => {
      const next = new Set(prev)
      if (next.has(brand)) {
        next.delete(brand)
      } else {
        next.add(brand)
      }
      return next
    })
  }

  const clearFilters = () => {
    setSelectedBrands(new Set())
    setZoom(1)
    setMinConfidence(50)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const visibleMarkers = filteredMarkers
  const zoomOffset = zoom > 1 ? (zoom - 1) * safeDuration * 0.1 : 0

  return (
    <div className="space-y-4">
      {/* Controls */}
      {showFilter && (
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Filter:</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMinConfidence((prev) => (prev === 50 ? 0 : 50))}
              className={`text-xs px-2 py-1 rounded-full border transition-colors ${
                minConfidence >= 50 ? "border-primary/50 text-primary bg-primary/10" : "border-border text-muted-foreground"
              }`}
              title="Show only brands with confidence above 50%"
            >
              {minConfidence >= 50 ? "Confidence >50%" : "All confidence"}
            </button>
            <button
              onClick={() => setZoom(z => Math.max(1, z - 0.5))}
              className="p-1 rounded hover:bg-muted transition-colors"
              disabled={zoom <= 1}
            >
              <ZoomOut className="h-4 w-4 text-muted-foreground" />
            </button>
            <span className="text-xs text-muted-foreground tabular-nums">{zoom.toFixed(1)}x</span>
            <button
              onClick={() => setZoom(z => Math.min(3, z + 0.5))}
              className="p-1 rounded hover:bg-muted transition-colors"
              disabled={zoom >= 3}
            >
              <ZoomIn className="h-4 w-4 text-muted-foreground" />
            </button>
            {(selectedBrands.size > 0 || zoom > 1) && (
              <button
                onClick={clearFilters}
                className="text-xs text-primary hover:underline"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      )}

      {/* Brand filter chips */}
      {showFilter && uniqueBrands.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {uniqueBrands.map((brand) => (
            <button
              key={brand}
              onClick={() => toggleBrand(brand)}
              className={`px-2 py-1 rounded-full text-xs transition-all ${
                selectedBrands.has(brand) || selectedBrands.size === 0
                  ? `text-white ${getBrandColor(brand)}`
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {brand} ({groupedMarkers[brand].length})
            </button>
          ))}
        </div>
      )}

      {/* Time labels */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {formatTime(0 + zoomOffset)}
        </motion.span>
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {formatTime(safeDuration - zoomOffset)}
        </motion.span>
      </div>

      {/* Timeline bar with heatmap */}
      <motion.div
        className="relative h-6 rounded-full bg-muted overflow-hidden border border-border/50 shadow-inner"
        initial={{ opacity: 0, scaleY: 0.5 }}
        animate={{ opacity: 1, scaleY: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        {/* Heatmap layer */}
        <div className="absolute inset-0 opacity-30">
          {visibleMarkers.map((marker, idx) => {
            const left = Math.min(95, Math.max(0, ((marker.time - zoomOffset) / safeDuration) * 100))
            const width = Math.max(2, (marker.duration || 2) / safeDuration * 100)
            return (
              <div
                key={`heatmap-${idx}`}
                className={`absolute h-full ${getBrandColor(marker.label).split(' ')[0]} blur-sm opacity-40`}
                style={{ left: `${left}%`, width: `${width}%` }}
              />
            )
          })}
        </div>

        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((pos) => (
          <div
            key={pos}
            className="absolute top-0 bottom-0 w-px bg-border/50"
            style={{ left: `${pos}%` }}
          />
        ))}

        {/* Markers */}
        {visibleMarkers.map((marker, index) => {
          const left = Math.min(95, Math.max(5, ((marker.time - zoomOffset) / safeDuration) * 100))
          const colorClass = getBrandColor(marker.label)
          
          return (
            <motion.div
              key={`${marker.label}-${marker.time}-${index}`}
              className={`absolute -top-1 h-8 w-2.5 rounded-full ${colorClass} cursor-pointer shadow-md hover:shadow-lg transition-shadow`}
              style={{ left: `${left}%`, transform: "translateX(-50%)" }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4 + index * 0.03, duration: 0.2 }}
              whileHover={{ scale: 1.5, zIndex: 10 }}
              onMouseEnter={() => setHoveredMarker(index)}
              onMouseLeave={() => setHoveredMarker(null)}
            >
              {/* Tooltip */}
              <motion.div
                className="absolute -top-16 left-1/2 -translate-x-1/2 px-3 py-2 bg-foreground text-background text-xs rounded-lg shadow-lg z-20 min-w-[120px]"
                animate={{
                  opacity: hoveredMarker === index ? 1 : 0,
                  y: hoveredMarker === index ? -4 : 0,
                }}
                transition={{ duration: 0.2 }}
              >
                <div className="font-semibold">{marker.label}</div>
                <div className="text-[10px] text-muted-foreground space-y-0.5 mt-1">
                  <div>Time: {formatTime(marker.time)}</div>
                  {marker.confidence && (
                    <div>Confidence: {Math.round(marker.confidence * 100)}%</div>
                  )}
                  {marker.duration && (
                    <div>Duration: {marker.duration.toFixed(1)}s</div>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Brand summary cards */}
      {Object.entries(groupedMarkers).length > 0 && (
        <motion.div
          className="grid grid-cols-2 sm:grid-cols-3 gap-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {Object.entries(groupedMarkers)
            .sort((a, b) => b[1].length - a[1].length)
            .slice(0, 6)
            .map(([brand, markers], idx) => {
              const totalExposure = markers.reduce((sum, m) => sum + (m.duration || 2), 0)
              const avgConfidence = markers.reduce((sum, m) => sum + (m.confidence || 0), 0) / markers.length
              const colorClass = getBrandColor(brand)
              
              return (
                <motion.button
                  key={brand}
                  onClick={() => toggleBrand(brand)}
                  className={`p-3 rounded-lg border transition-all hover:shadow-md ${
                    selectedBrands.has(brand) || selectedBrands.size === 0
                      ? `bg-gradient-to-br from-muted to-muted/50 border-border`
                      : "bg-muted/30 border-border/50 opacity-60"
                  }`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + idx * 0.05 }}
                >
                  <div className={`w-full h-1 rounded-full mb-2 ${colorClass.split(' ')[0]}`} />
                  <div className="text-xs font-semibold truncate">{brand}</div>
                  <div className="text-[10px] text-muted-foreground space-y-0.5 mt-1">
                    <div className="flex justify-between">
                      <span>Detections:</span>
                      <span className="font-medium">{markers.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Exposure:</span>
                      <span className="font-medium">{totalExposure.toFixed(1)}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Confidence:</span>
                      <span className="font-medium">{Math.round(avgConfidence * 100)}%</span>
                    </div>
                  </div>
                </motion.button>
              )
            })}
        </motion.div>
      )}

      {/* Brand badges list */}
      <motion.div
        className="flex flex-wrap gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {visibleMarkers.slice(0, 20).map((marker, index) => {
          const colorClass = getBrandColor(marker.label)
          return (
            <motion.button
              key={`${marker.label}-${marker.time}-label`}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border text-xs transition-all ${colorClass} text-white`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + index * 0.03 }}
              whileHover={{ scale: 1.05 }}
              onClick={() => toggleBrand(marker.label)}
            >
              <span className="font-medium">{marker.label}</span>
              <span className="text-[10px] opacity-80">@{formatTime(marker.time)}</span>
            </motion.button>
          )
        })}
      </motion.div>

      {visibleMarkers.length === 0 && markers.length > 0 && (
        <div className="text-center py-4 text-sm text-muted-foreground">
          No markers match the selected filters
        </div>
      )}
    </div>
  )
}
