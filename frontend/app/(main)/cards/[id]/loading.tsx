export default function CardLoading() {
  return (
    <div className="container max-w-4xl mx-auto px-4 py-12">
      <div className="mb-8 space-y-4">
        <div className="h-12 bg-primary/10 rounded-lg w-3/4 animate-pulse" />
        <div className="h-6 bg-foreground/5 rounded w-1/2 animate-pulse" />
      </div>
      <div className="flex gap-2 mb-8">
        {[...Array(4)].map((_, i) => <div key={i} className="h-6 w-20 bg-secondary/20 rounded-full animate-pulse" />)}
      </div>
      <div className="space-y-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 bg-foreground/5 rounded w-full animate-pulse" />
            <div className="h-4 bg-foreground/5 rounded w-11/12 animate-pulse" />
            <div className="h-4 bg-foreground/5 rounded w-10/12 animate-pulse" />
          </div>
        ))}
      </div>
      <div className="mt-12 pt-8 border-t border-border">
        <div className="h-12 bg-accent/20 rounded-2xl w-48 animate-pulse" />
      </div>
    </div>
  )
}
