import { BookOpen, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Card } from "@/lib/validators"
import { CardPreview } from "@/components/cards/card-preview"

interface CardGridProps {
  cards: Card[]
  isLoading: boolean
  error: string | null
  onRetry?: () => void
}

export function CardGrid({ cards, isLoading, error, onRetry }: CardGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-64 w-full rounded-2xl bg-linear-to-br from-card/40 to-card/20 border border-border/20 animate-pulse">
            <div className="p-6 space-y-4">
              <div className="h-6 bg-primary/10 rounded-lg w-3/4" />
              <div className="space-y-2">
                <div className="h-3 bg-foreground/5 rounded w-full" />
                <div className="h-3 bg-foreground/5 rounded w-5/6" />
                <div className="h-3 bg-foreground/5 rounded w-4/6" />
              </div>
              <div className="flex gap-2 pt-4">
                <div className="h-6 w-16 bg-secondary/20 rounded-full" />
                <div className="h-6 w-20 bg-secondary/20 rounded-full" />
                <div className="h-6 w-14 bg-secondary/20 rounded-full" />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="bg-destructive/10 rounded-full p-4 mb-4">
          <AlertCircle className="h-12 w-12 text-destructive" />
        </div>
        <h3 className="text-xl font-semibold text-primary mb-2">Oops! Something went wrong</h3>
        <p className="text-foreground/70 text-center mb-6 max-w-md">{error}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="default" className="bg-accent hover:bg-accent/90">
            Try Again
          </Button>
        )}
      </div>
    )
  }

  if (cards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="bg-secondary/20 rounded-full p-4 mb-4">
          <BookOpen className="h-12 w-12 text-primary" />
        </div>
        <h3 className="text-xl font-semibold text-primary mb-2">No Cards Found</h3>
        <p className="text-foreground/70 text-center max-w-md">
          There are no cards to display yet. Try adjusting your search or create a new card to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cards.map((card) => (
        <CardPreview key={card.id} card={card} />
      ))}
    </div>
  )
}
