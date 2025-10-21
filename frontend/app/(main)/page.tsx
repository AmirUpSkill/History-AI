"use client"

import { useEffect } from "react"
import { useAppStore } from "@/store/app-store"
import { SearchPanel } from "@/components/layout/search-panel"
import { CardGrid } from "@/components/layout/card-grid"

export default function HomePage() {
  const { cards, isLoading, error, fetchCards } = useAppStore()

  // --- Fetch cards on mount ---
  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8">
      {/* ---  Page Header  --- */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-primary mb-2">
          Welcome to AI Wiki
        </h1>
        <p className="text-lg text-foreground/70">
          Curating AI-generated historical and political event cards
        </p>
      </div>

      {/* ---  Search Panel --- */}
      <SearchPanel onSearch={fetchCards} />

      {/* --- Cards Grid --- */}
      <CardGrid 
        cards={cards} 
        isLoading={isLoading} 
        error={error}
        onRetry={() => fetchCards()}
      />
    </div>
  )
}