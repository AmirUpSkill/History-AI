import { notFound } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { BlogCardContent } from "@/components/cards/blog-card-content"
import { fetchCardById } from "@/lib/api"

export default async function CardPage({ params }: { params: { id: string } }) {
  const { id } = await params
  let card

  try {
    card = await fetchCardById(id)
  } catch (error: any) {
    if ((error.message || "").toLowerCase().includes("not found")) notFound()
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-primary mb-4">Oops! Something went wrong</h1>
        <p className="text-foreground/70">Failed to load this card. Please try again.</p>
      </div>
    )
  }

  return (
    <article className="container max-w-4xl mx-auto px-4 py-12">
      <header className="mb-12">
        <h1 className="text-5xl font-bold text-primary mb-4 leading-tight">{card.title}</h1>
        {card.keywords.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {card.keywords.map((keyword, i) => (
              <Badge key={i} variant="secondary" className="bg-secondary/50 text-primary hover:bg-secondary/70 transition-colors text-sm px-3 py-1">
                {keyword}
              </Badge>
            ))}
          </div>
        )}
      </header>

      <div className="h-px bg-border mb-12" />
      <BlogCardContent content={card.description} />
    </article>
  )
}
