"use client"

import { useEffect, useState } from "react"
import { Search, Plus } from "lucide-react"
import { toast } from "sonner"

interface SearchPanelProps {
  onSearch: (query?: string) => void
}

export function SearchPanel({ onSearch }: SearchPanelProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [isFocused, setIsFocused] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => onSearch(searchTerm || undefined), 300)
    return () => clearTimeout(timer)
  }, [searchTerm, onSearch])

  return (
    <div className={`w-full rounded-3xl bg-linear-to-br from-card/95 to-card/80 backdrop-blur-sm shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:shadow-[0_12px_40px_rgb(0,0,0,0.16)] border border-border/30 p-6 mb-10 transform transition-all duration-300 ease-out hover:-translate-y-1 ${isFocused ? 'ring-2 ring-primary/20 shadow-[0_12px_40px_rgb(27,94,110,0.15)]' : ''}`}>
      <div className="flex flex-col sm:flex-row gap-4 items-stretch relative">
        <Search className={`absolute left-4 top-6 sm:top-1/2 sm:-translate-y-1/2 h-5 w-5 z-10 transition-colors duration-200 ${isFocused ? 'text-primary' : 'text-muted-foreground'}`} />
        <input
          type="text"
          placeholder="Search cards by title..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="flex-1 h-12 pl-12 pr-4 bg-transparent border-0 text-foreground placeholder:text-muted-foreground/60 focus:outline-none transition-all duration-200 text-sm font-medium"
          aria-label="Search cards"
        />
        <button
          onClick={() => toast.info("Add card feature coming soon!")}
          className="flex items-center justify-center gap-2 px-6 h-12 rounded-2xl bg-accent hover:bg-accent/90 text-white font-semibold text-sm shadow-[0_4px_12px_rgba(232,132,92,0.3)] hover:shadow-[0_6px_16px_rgba(232,132,92,0.4)] transform transition-all duration-200 ease-out hover:-translate-y-0.5 active:translate-y-0 whitespace-nowrap"
        >
          <Plus className="h-5 w-5" />
          Add Card
        </button>
      </div>
    </div>
  )
}
