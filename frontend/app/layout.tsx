import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/layout/theme-provider"
import { Toaster } from "sonner"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "AI Wiki - Historical Events",
  description: "Curating AI-generated historical and political event cards",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster 
            position="top-center" 
            richColors 
            closeButton
            toastOptions={{
              classNames: {
                toast: "bg-card border-border",
                title: "text-primary",
                description: "text-foreground/70",
              }
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  )
}