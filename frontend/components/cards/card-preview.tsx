import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Card as CardType } from "@/lib/validators"

interface CardPreviewProps {
  card: CardType
}

export function CardPreview({ card }: CardPreviewProps) {
  return (
    <Link href={`/cards/${card.id}`} className="block group">
      <Card className="h-full transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer border-border/50 hover:border-primary/30">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-primary group-hover:text-primary/80 transition-colors line-clamp-2">
            {card.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* --- Description --- */}
          <p className="text-sm text-foreground/70 line-clamp-3 leading-relaxed">
            {card.description}
          </p>

          {/* Keywords */}
          {card.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {card.keywords.slice(0, 4).map((keyword, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="bg-secondary/50 text-primary hover:bg-secondary/70 transition-colors text-xs"
                >
                  {keyword}
                </Badge>
              ))}
              {card.keywords.length > 4 && (
                <Badge variant="outline" className="text-xs text-foreground/50">
                  +{card.keywords.length - 4} more
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}