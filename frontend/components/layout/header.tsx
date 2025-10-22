import Image from "next/image"
import Link from "next/link"
import { ThemeToggle } from "./theme-toggle"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 max-w-7xl items-center justify-between px-4 mx-auto">
        {/* --- Logo and Title --- */}
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity duration-200">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg">
            <Image src="/book.png" alt="AI Wiki Logo" width={40} height={40} />
          </div>
          <h1 className="text-2xl font-bold text-primary">AI Wiki</h1>
        </Link>

        {/* --- Theme Toggle  --- */}
        <ThemeToggle />
      </div>
    </header>
  )
}
